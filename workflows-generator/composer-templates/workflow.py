# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# --------------------------------------------------------------------------------
# Load The Dependencies
# --------------------------------------------------------------------------------

import json
import uuid
import re
from airflow import models
import google.auth
from airflow.models.variable import Variable
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator
from airflow.operators import empty
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.utils.task_group import TaskGroup
from airflow.providers.google.cloud.operators.bigquery import  BigQueryInsertJobOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.sensors.dataform import DataformWorkflowInvocationStateSensor
from airflow.providers.google.cloud.operators.dataform import (
    DataformCreateCompilationResultOperator,
    DataformCreateWorkflowInvocationOperator,
)
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateBatchOperator,
    DataprocGetBatchOperator
)
from airflow.providers.google.cloud.sensors.dataproc import DataprocBatchSensor
from google.cloud.dataform_v1beta1 import WorkflowInvocation
from google.cloud import storage
from datetime import datetime, timedelta

# --------------------------------------------------------------------------------
# Read variables from GCS parameters file for the job
# --------------------------------------------------------------------------------
storage_client = storage.Client()
jobs_bucket = Variable.get("DATA_TRANSFORMATION_GCS_BUCKET")

batch_id = f"aef-{str(uuid.uuid4())}"

def extract_job_params(job_name, function_name, encoding='utf-8'):
    """Extracts parameters from a JSON job file.

    Args:
        bucket_name: Bucket containing the JSON parameters file .

    Returns:
        A dictionary containing the extracted parameters.
    """

    json_file_path = f'gs://{jobs_bucket}/{function_name}/{job_name}.json'

    parts = json_file_path.replace("gs://", "").split("/")
    bucket_name = parts[0]
    object_name = "/".join(parts[1:])
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    json_data = blob.download_as_bytes()
    params = json.loads(json_data.decode(encoding))
    return params


# --------------------------------------------------------------------------------
# Set default arguments
# --------------------------------------------------------------------------------

# If you are running Airflow in more than one time zone
# see https://airflow.apache.org/docs/apache-airflow/stable/timezone.html
# for best practices
yesterday = datetime.now() - timedelta(days=1)

default_args = {
    'owner': 'airflow',
    'start_date': yesterday,
    'depends_on_past': False,
    'email': [''],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}

<<STEPS_ARGS>>

start_date_str = yesterday.strftime('%Y-%m-%d')
end_date_str = datetime.today().strftime('%Y-%m-%d')
# --------------------------------------------------------------------------------
# Main DAG
# --------------------------------------------------------------------------------

with models.DAG(
        '<<DAG_NAME>>',
        default_args=default_args,
        params={
            "start_date_str": start_date_str,
            "end_date_str": end_date_str
        },
        catchup=False,
        schedule_interval=None) as dag:

    start = empty.EmptyOperator(
        task_id='start',
        trigger_rule='all_success'
    )

    <<LEVELS>>

    end = empty.EmptyOperator(
        task_id='end',
        trigger_rule='all_success'
    )

    start >> <<LEVEL_DEPENDENCIES>> >> end