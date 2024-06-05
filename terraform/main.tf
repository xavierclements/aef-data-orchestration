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


resource "local_file" "parameters_file" {
  filename = "../workflow-definitions/platform-parameters-${var.environment}.json"
  content  = jsonencode(local.workflows_generator_params)
}


resource "null_resource" "deploy_cloud_workflows" {
  for_each = var.deploy_cloud_workflows ? local.cloud_workflows_filenames : []
  provisioner "local-exec" {
    command = <<EOF
      python3 ../workflows-generator/orchestration_generator.py \
      ../workflow-definitions/${each.value} \
      ../workflow-definitions/platform-parameters-${var.environment}.json \
      ../cloud-workflows/${each.value} \
      False
    EOF
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [local_file.parameters_file]
}

resource "google_workflows_workflow" "workflows" {
  for_each        = var.deploy_cloud_workflows ? local.cloud_workflows_filenames : []
  name            = replace(each.value, ".json", "")
  region          = var.region
  project         = var.project
  call_log_level  = var.workflows_log_level
  source_contents = data.local_file.workflow[each.value].content
  depends_on = [data.local_file.workflow]
}

data "local_file" "workflow" {
  for_each = var.deploy_cloud_workflows ? local.cloud_workflows_filenames : []
  filename = "../cloud-workflows/${each.value}"
  depends_on = [null_resource.deploy_cloud_workflows]
}