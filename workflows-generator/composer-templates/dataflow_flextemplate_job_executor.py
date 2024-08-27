                    with TaskGroup(group_id="{JOB_ID}") as {JOB_ID}:
                        dataflow_job_name = re.sub(r"^\d+", "",re.sub(r"[^a-z0-9+]", "", "{JOB_ID}"))
                        dataflow_job_name = re.sub(r"^\d+", "", dataflow_job_name)
                        gcs_path = "gs://dataflow-templates-{region}/{version}/flex/{template}".format(region=default_args['{JOB_ID}'+'dataflow_location'],
                                                                                                       version=default_args['{JOB_ID}'+'dataflow_template_version'],
                                                                                                       template=default_args['{JOB_ID}'+'dataflow_template_name'])
                        body = {
                            "launchParameter": {
                                "jobName": dataflow_job_name,
                                "parameters": default_args['{JOB_ID}'+'dataflow_job_params'],
                                "containerSpecGcsPath": gcs_path,
                                "environment": {
                                    "tempLocation": "gs://{bucket}/dataflow/temp".format(bucket=default_args['{JOB_ID}' + 'dataflow_temp_bucket']),
                                    "maxWorkers": str(default_args['{JOB_ID}' + 'dataflow_max_workers']),
                                    "network": str(default_args['{JOB_ID}' + 'network']),
                                    "subnetwork": str(default_args['{JOB_ID}' + 'subnetwork'])}
                            }
                        }
                        dataflow_job_{JOB_ID} = DataflowStartFlexTemplateOperator(
                            task_id="dataflow_flex_template_{JOB_ID}",
                            location=default_args['{JOB_ID}'+'dataflow_location'],
                            body=body
                        )

                        dataflow_job_{JOB_ID}