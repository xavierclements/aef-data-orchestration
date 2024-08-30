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

data "google_project" "project" {
  project_id = var.project
}

# ------------------------------------------------------
# Cloud Workflows deployment
# ------------------------------------------------------
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

# ------------------------------------------------------
# Cloud Composer deployment
# ------------------------------------------------------
resource "null_resource" "deploy_composer_dags" {
  for_each = var.deploy_composer_dags ? local.composer_filenames : []
  provisioner "local-exec" {
    command = <<EOF
      python3 ../workflows-generator/orchestration_generator.py \
      ../workflow-definitions/${each.value} \
      ../workflow-definitions/platform-parameters-${var.environment}.json \
      ../composer-dags/${replace(each.value, ".json", ".py")} \
      False
    EOF
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [local_file.parameters_file]
}

resource "google_storage_bucket_object" "uploaded_artifacts_aef_composer" {
  for_each = var.deploy_composer_dags  && var.composer_bucket_name == null ? fileset("../composer-dags/", "**/*") : []
  name     = "dags/${each.key}"
  bucket   = "${replace(replace(google_composer_environment.aef_composer_environment[0].config[0].dag_gcs_prefix, "gs://", ""),"/dags","")}"
  source   = "../composer-dags/${each.key}"
  depends_on = [google_composer_environment.aef_composer_environment, null_resource.deploy_composer_dags]
}

resource "google_storage_bucket_object" "uploaded_artifacts_external_composer" {
  for_each = var.deploy_composer_dags  && var.composer_bucket_name != null ? fileset("../composer-dags/", "**/*") : []
  name     = "dags/${each.key}"
  bucket   = "gs://${var.composer_bucket_name}"
  source   = "../composer-dags/${each.key}"
  depends_on = [null_resource.deploy_composer_dags]
}

resource "google_composer_environment" "aef_composer_environment" {
  count    = var.create_composer_environment == true ? 1 : 0
  provider = google-beta
  project  = var.project
  name     = "aef-${var.project}-${var.environment}"
  region   = var.region
  config {
    software_config {
      airflow_config_overrides = var.composer_config.software_config.airflow_config_overrides
      pypi_packages            = var.composer_config.software_config.pypi_packages
      env_variables            = local.composer_env_variables
      image_version            = var.composer_config.software_config.image_version
      cloud_data_lineage_integration {
        enabled = var.composer_config.software_config.cloud_data_lineage_integration
      }
    }
    workloads_config {
      scheduler {
        cpu        = var.composer_config.workloads_config.scheduler.cpu
        memory_gb  = var.composer_config.workloads_config.scheduler.memory_gb
        storage_gb = var.composer_config.workloads_config.scheduler.storage_gb
        count      = var.composer_config.workloads_config.scheduler.count
      }
      web_server {
        cpu        = var.composer_config.workloads_config.web_server.cpu
        memory_gb  = var.composer_config.workloads_config.web_server.memory_gb
        storage_gb = var.composer_config.workloads_config.web_server.storage_gb
      }
      worker {
        cpu        = var.composer_config.workloads_config.worker.cpu
        memory_gb  = var.composer_config.workloads_config.worker.memory_gb
        storage_gb = var.composer_config.workloads_config.worker.storage_gb
        min_count  = var.composer_config.workloads_config.worker.min_count
        max_count  = var.composer_config.workloads_config.worker.max_count
      }
    }

    environment_size = var.composer_config.environment_size

    node_config {
      network              = var.composer_config.vpc
      subnetwork           = var.composer_config.subnet
      service_account      = module.composer-service-account[0].email
      enable_ip_masq_agent = true
      tags                 = ["composer-worker"]

    }
    private_environment_config {
      enable_private_endpoint              = "true"
      cloud_sql_ipv4_cidr_block            = var.composer_config.cloud_sql
      master_ipv4_cidr_block               = var.composer_config.gke_master
      cloud_composer_connection_subnetwork = var.composer_config.connection_subnetwork
    }
    dynamic "encryption_config" {
      for_each = var.composer_config.service_encryption_keys != null ? [""] : []
      content {
        kms_key_name = var.composer_config.service_encryption_keys
      }
    }
    web_server_network_access_control {
      dynamic "allowed_ip_range" {
        for_each = var.composer_config.web_server_access_control
        content {
          value       = allowed_ip_range.key
          description = allowed_ip_range.value
        }
      }
    }
  }
  depends_on = [
    module.composer-service-account
  ]
}

module "composer-service-account" {
  count    = var.create_composer_environment == true ? 1 : 0
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric/modules/iam-service-account"
  project_id = var.project
  name       = "aef-composer${var.environment}-sa"
  iam_project_roles = {
    "${var.project}" = [
      "roles/bigquery.jobUser",
      "roles/composer.worker",
      "roles/dataform.admin",
      "roles/dataflow.admin",
      "roles/iam.serviceAccountUser"
    ]
  }
}

resource "google_service_account_iam_member" "custom_service_account" {
  count    = var.create_composer_environment == true ? 1 : 0
  provider = google-beta
  service_account_id = module.composer-service-account[0].name
  role = "roles/composer.ServiceAgentV2Ext"
  member = "serviceAccount:service-${data.google_project.project.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
  depends_on = [module.composer-service-account]
}