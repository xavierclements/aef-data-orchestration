project = "<PROJECT>"
region  = "us-central1"

data_transformation_project = "<PROJECT>"
environment                 = "dev"

deploy_cloud_workflows      = true
workflows_log_level         = "LOG_ERRORS_ONLY"

deploy_composer_dags        = true
create_composer_environment = true
composer_config             = {
  vpc              = "projects/<PROJECT>/global/networks/sample-vpc"
  subnet           = "projects/<PROJECT>/regions/us-central1/subnetworks/default-us-central1"
  cloud_sql        = "10.0.10.0/24"
  gke_master       = "10.0.11.0/28"
  environment_size = "ENVIRONMENT_SIZE_SMALL"
  software_config  = {
    image_version = "composer-2-airflow-2"
    cloud_data_lineage_integration = true
  }
  workloads_config = {
    scheduler = {
      cpu        = 0.5
      memory_gb  = 1.875
      storage_gb = 1
      count      = 1
    }
    web_server = {
      cpu        = 0.5
      memory_gb  = 1.875
      storage_gb = 1
    }
    worker = {
      cpu        = 0.5
      memory_gb  = 1.875
      storage_gb = 1
      min_count  = 1
      max_count  = 3
    }
  }
}