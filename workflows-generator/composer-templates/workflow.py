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

import datetime

from airflow import models
from airflow.models.variable import Variable
from airflow.providers.google.cloud.operators.dataflow import DataflowTemplatedJobStartOperator
from airflow.operators import empty
from airflow.utils.task_group import TaskGroup
from airflow.providers.google.cloud.operators.bigquery import  BigQueryInsertJobOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.sensors.dataform import DataformWorkflowInvocationStateSensor
from airflow.providers.google.cloud.operators.dataform import (
    DataformCreateCompilationResultOperator,
    DataformCreateWorkflowInvocationOperator,
)
from google.cloud.dataform_v1beta1 import WorkflowInvocation

# --------------------------------------------------------------------------------
# Set variables - Variables nneds to be created manually
# --------------------------------------------------------------------------------
DATAFORM_PROJECT_ID = Variable.get("DATAFORM_PROJECT_ID")
DATAFORM_REGION = Variable.get("DATAFORM_REGION")
DATAFORM_REPOSITORY_ID = Variable.get("DATAFORM_REPOSITORY_ID")

# --------------------------------------------------------------------------------
# Set default arguments
# --------------------------------------------------------------------------------

# If you are running Airflow in more than one time zone
# see https://airflow.apache.org/docs/apache-airflow/stable/timezone.html
# for best practices
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

default_args = {
    'owner': 'airflow',
    'start_date': yesterday,
    'depends_on_past': False,
    'email': [''],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'project_id': DATAFORM_PROJECT_ID,
    'region': DATAFORM_REGION,
    'repository_id': DATAFORM_REPOSITORY_ID,
    'retry_delay': datetime.timedelta(minutes=5)
}

start_date_str = yesterday.strftime('%Y-%m-%d')
end_date_str = datetime.datetime.today().strftime('%Y-%m-%d')
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