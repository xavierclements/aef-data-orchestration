/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

variable "project" {
  description = "Project where the cloud workflows or Composer DAGs will be created."
  type        = string
  nullable    = false
}

variable "region" {
  description = "Region where the Cloud Workflows will be created."
  type        = string
  nullable    = false
}

variable "environment" {
  description = "AEF environment. Will be used to create the parameters file for Cloud Workflows: platform-parameters-<<environment>>.json"
  type        = string
  nullable    = false
}

variable "data_transformation_project" {
  description = "Project where the data transformation jobs definitions reside (will be used to infer bucket storing job parameter json files)."
  type        = string
  nullable    = false
}

variable "deploy_cloud_workflows" {
  description = "Controls whether cloud workflows are generated and deployed alongside Terraform resources. If false cloud workflows could be deployed as a next step in a CICD pipeline."
  type        = bool
  nullable    = true
  default     = true
}

variable "deploy_composer_dags" {
  description = "Controls whether Airflow DAGs are generated and deployed alongside Terraform resources. If false DAGs could be deployed as a next step in a CICD pipeline."
  type        = bool
  nullable    = true
  default     = false
}

variable "create_composer_environment" {
  description = "Controls whether a composer environment will be created, If false and deploy_composer_dags set to true, then composer_bucket_name needs to be set."
  type        = bool
  nullable    = true
  default     = false
}

variable "composer_bucket_name" {
  description = "If Composer environment is not created and deploy_composer_dags is set to true, then this will be used to upload DAGs to."
  type        = string
  nullable    = true
  default     = null
}

variable "composer_config" {
  description = "Cloud Composer config."
  type        = object({
    vpc                     = optional(string)
    subnet                  = optional(string)
    connection_subnetwork   = optional(string)
    cloud_sql               = optional(string)
    gke_master              = optional(string)
    service_encryption_keys = optional(string)

    environment_size = optional(string)
    software_config  = optional(object({
      airflow_config_overrides       = optional(map(string), {})
      pypi_packages                  = optional(map(string), {})
      env_variables                  = optional(map(string), {})
      image_version                  = optional(string)
      cloud_data_lineage_integration = optional(bool, true)
    }), {})
    web_server_access_control = optional(map(string), {})
    workloads_config          = optional(object({
      scheduler = optional(object({
        cpu        = optional(number)
        memory_gb  = optional(number)
        storage_gb = optional(number)
        count      = optional(number)
      }
      ), {})
      web_server = optional(object({
        cpu        = optional(number)
        memory_gb  = optional(number)
        storage_gb = optional(number)
      }), {})
      worker = optional(object({
        cpu        = optional(number)
        memory_gb  = optional(number)
        storage_gb = optional(number)
        min_count  = optional(number)
        max_count  = optional(number)
      }
      ), {})
    }), {})
  })
  nullable = true
  default  = {}
}

variable "workflows_log_level" {
  description = "Describes the level of platform logging to apply to calls and call responses during executions of cloud workflows"
  type        = string
  default     = "LOG_ERRORS_ONLY"
  nullable    = false
}
