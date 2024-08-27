# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

locals {
  workflow_definitions_dir = "../workflow-definitions"

  workflow_files = {
    for filename in fileset(local.workflow_definitions_dir, "*") :
    filename => jsondecode(file("${local.workflow_definitions_dir}/${filename}"))
  }

  cloud_workflows_filenames = toset([
    for filename, file_content in local.workflow_files : filename
    if (try(file_content.engine, null) == "cloud_workflows")
  ])

  composer_filenames = toset([
    for filename, file_content in local.workflow_files : filename
    if (try(file_content.engine, null) == "composer")
  ])

  workflows_generator_params = [
    {
      "ParameterKey" : "pRegion",
      "ParameterValue" : var.region
    },
    {
      "ParameterKey" : "pProjectID",
      "ParameterValue" : var.project
    },
    {
      "ParameterKey" : "pFunctionIntermediateName",
      "ParameterValue" : "orch-framework-intermediate"
    },
    {
      "ParameterKey" : "pJobsDefinitionsBucket",
      "ParameterValue" : "${var.data_transformation_project}_aef_jobs_bucket"
    }
  ]
  _env_variables = {
    DATA_TRANSFORMATION_GCS_BUCKET = "${var.data_transformation_project}_aef_jobs_bucket"
  }

  composer_env_variables = {
    for k, v in merge(
      var.composer_config.software_config.env_variables, local._env_variables
    ) : "AIRFLOW_VAR_${k}" => v
  }

}