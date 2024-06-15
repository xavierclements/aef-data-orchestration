# Analytics Engineering Framework - Data Orchestration
[Analytics engineers](https://www.getdbt.com/what-is-analytics-engineering) lay the foundation for others to organize, transform, and document data using software engineering principles. Providing easy to use data platforms that empower data practitioners to independently build data pipelines in a standardized and scalable way, and answer their own data-driven questions.

Data orchestration plays a vital role in enabling efficient data access and analysis, making it critical for data lakes and data warehouses.

This repository automates the creation of [Google Cloud Workflows Definition](https://cloud.google.com/workflows/docs/reference/syntax) files from data pipeline configuration files. 
It's designed for seamless integration into your CI/CD pipeline, using ***LEVEL***, ***THREAD***, and ***STEP*** abstractions to define your batch data pipeline. 
You also have the flexibility to directly execute ***workflows_generator.py*** for manual workflow definition generation.

## Key Features
- ***CI/CD Integration:***  Effortlessly streamline your Google Cloud Workflow generation within your CI/CD pipeline. (Deployed here as a Terraform null_resource as a simple example).
- ***Abstracted Pipeline Definition:*** Conveniently define your batch data pipelines using the intuitive concepts of LEVEL, THREAD, and STEP.
- ***Manual Execution:*** Option to directly run ***workflows_generator.py*** for on-demand workflow creation.

##  Concepts
Most batch data pipelines can be effectively defined using three simple concepts, simplifying  pipeline creation and scheduling for data analysts:
- ***LEVEL:*** The largest aggregation within your pipeline. Levels execute sequentially, and you can have as many as needed. Identify each LEVEL with a unique ID.
- ***STEP:*** The atomic unit of execution. A STEP represents a data transformation process (e.g., Dataflow job, BigQuery job, Dataproc job).
- ***THREAD:*** Allows for complex dependencies and parallel execution within your pipeline. A THREAD groups steps that execute sequentially.  A LEVEL can have multiple THREADs running in parallel.

![level-thread-step.png](level-thread-step.png)

```json
{
  "engine": "cloud_workflows",
  "definition": [
    {
      "LEVEL_ID": "1",
      "THREADS": [
        {
          "THREAD_ID": "1",
          "STEPS": [
            {
              "JOB_ID": "J01",
              "JOB_NAME": "sample_jdbc_dataflow_ingestion",
              "TYPE": "async",
              "FUNCTION_ID_NAME": "dataflow-flextemplate-job-executor",
              "FUNCTION_STATUS_NAME": "dataflow-flextemplate-job-executor",
              "WAIT_TIME_SECONDS": "30",
              "ASYNC_TIMEOUT_LOOP_IN_MINUTES": "12"
            },
            {
              "JOB_ID": "J02",
              "JOB_NAME": "run_dataform_tag",
              "TYPE": "async",
              "FUNCTION_ID_NAME": "dataform-tag-executor",
              "FUNCTION_STATUS_NAME": "dataform-tag-executor",
              "WAIT_TIME_SECONDS": "20",
              "ASYNC_TIMEOUT_LOOP_IN_MINUTES": "12"
            }
          ]
        }
      ]
    }
  ]
}
```

This approach enables data analysts to build intricate data pipelines and reliably orchestrate them without writing  code. Configuration is handled through simple JSON definition files containing levels, threads, and steps.
## Usage
### Manual Execution
1. The following script will read a simple JSON data pipeline definition (levels, threads, and steps) and generate a Cloud Workflows configuration file ready for deployment. This configuration manages retries, cycles, errors, and calls step executors as Cloud Functions that should exist in the project. Typically, those Cloud Functions are deployed using the Orchestration framework repository.
```shell
python3 workflows_generator.py \
../workflow-definitions/etl_example_1.json \
../workflow-definitions/platform-parameters-dev.json \
workflows_etl_example_1.json \
False
```
### Terraform
The provided Terraform code enables reading defined JSON data pipelines definitions and managing the deployment of the resulting Cloud Workflows. In addition to the example using Terraform's *null_resource* to generate Cloud Workflows, these workflows can also be generated and deployed as a separate step within your CI/CD pipeline.
1. Locate your JSON data pipeline definition files in the repository.
```
├── workflow-definitions
│   ├── demo_pipeline.json
│   └── ...
```
2. Define your terraform variables.
<!-- BEGIN TFDTFOC -->
| name                                     | description                                                                                                                                                           | type        | required | default     |
|------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|----------|-------------|
| [project](variables.tf#L16)             | Project where the cloud workflows or Composer DAGs (TODO) will be created.                                                                                            | string      | true     | -           |
| [data_transformation_project](variables.tf#L24) | Project where the data transformation jobs definitions reside (will be used to infer bucket storing job parameter json files).                                        | string      | true     | -           |
| [region](variables.tf#L32)              | Region where the Cloud Workflows will be created.                                                                                                                     | string      | true     | -           |
| [environment](variables.tf#L40)         | AEF environment. Will be used to create the parameters file for Cloud Workflows: platform-parameters-$ENVIRONMENT.json                                                | string      | true     | -           |
| [deploy_cloud_workflows](variables.tf#L48) | Controls whether cloud workflows is generated and deployed alongside Terraform resources. If false cloud workflows can be deployed as a next step in a CICD pipeline. | bool        | true     | -           |
| [workflows_log_level](variables.tf#L56) | Describes the level of platform logging to apply to calls and call responses during executions of cloud workflows                                                     | string      | false    | LOG_ERRORS_ONLY |
<!-- END TFDOC -->

2.Run the Terraform Plan / Apply using the variables you defined.
```bash
terraform plan -var 'project=<PROJECT>' -var 'data_transformation_project=<PROJECT>' -var 'environment=dev' -var 'region=<REGION>' -var 'deploy_cloud_workflows=true' 
```

## Integration with Analytics Engineering Framework

While usable independently, this tool is optimized as a component within a comprehensive Analytics Engineering Framework comprising:

1. **Orchestration Framework**: Maintained by Analytics Engineers to provide seamless, extensible orchestration and execution infrastructure.
1. **Data Model**: Directly used by end data practitioners to manage data models, schemas, and Dataplex metadata.
1. **(This repository) Data Orchestration**: Directly used by end data practitioners to define and deploy data pipelines using levels, threads, and steps.
1. **Data Transformation**: Directly used by end data practitioners to define, store, and deploy data transformations.
