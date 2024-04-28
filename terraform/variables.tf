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
  description = "Project where the the cloud workflows or Composer DAGs will be created."
  type        = string
  nullable    = false
}

variable "region" {
  description = "Region where the the cloud workflows will be created."
  type        = string
  nullable    = false
}

variable "deploy_cloud_workflows" {
  description = "Controls whether cloud workflows is generated and deployed alongside Terraform resources. If false cloud workflows can be deployed as a next step in a CICD pipeline."
  type        = bool
  nullable    = false
}

variable "workflows_log_level" {
  description = "Describes the level of platform logging to apply to calls and call responses during executions of cloud workflows"
  type        = string
  default     = "LOG_ERRORS_ONLY"
  nullable    = false
}

variable "workflows_parameter_filename" {
  description = "Name of the JSON parameters file in the workflow-definitions folder that define variables like environment."
  type        = string
  nullable    = true
}