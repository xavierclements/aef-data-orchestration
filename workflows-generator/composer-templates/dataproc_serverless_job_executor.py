                    with TaskGroup(group_id="{JOB_ID}") as {JOB_ID}:

                           def push_batch_id_to_xcom(**context):
                               context['task_instance'].xcom_push(key='batch-id', value=batch_id)

                           push_batch_id_to_xcom_{JOB_ID} = PythonOperator(
                               task_id='batch_id',
                               python_callable=push_batch_id_to_xcom,
                               provide_context=True
                           )

                           # create batch
                           create_batch_for_{JOB_ID} = DataprocCreateBatchOperator(
                               task_id="create_batch_for_{JOB_ID}",
                               batch={
                                   "spark_batch": {
                                       "jar_file_uris": [default_args['{JOB_ID}' + 'jar_file_location']],
                                       "main_class": default_args['{JOB_ID}' + 'spark_app_main_class'],
                                       "args": default_args['{JOB_ID}' + 'spark_args'],
                                   },
                                   "runtime_config": {
                                       "version": default_args['{JOB_ID}' + 'dataproc_serverless_runtime_version'],
                                       "properties": default_args['{JOB_ID}' + 'spark_app_properties'],
                                   },
                                   "environment_config": {
                                       "execution_config": {
                                           "service_account": default_args['{JOB_ID}' + 'dataproc_service_account'],
                                           "subnetwork_uri": f"projects/{default_args['{JOB_ID}' + 'dataproc_serverless_project_id']}/{default_args['{JOB_ID}' + 'subnetwork']}"
                                       }
                                   }
                               },
                               batch_id="{{ task_instance.xcom_pull(task_ids='Level_{LEVEL_ID}.Level_{LEVEL_ID}_Thread_{THREAD_ID}.{JOB_ID}.batch_id', key='batch-id') }}",
                               project_id=default_args['{JOB_ID}' + 'dataproc_serverless_project_id'],
                               region=default_args['{JOB_ID}' + 'dataproc_serverless_region'],
                               deferrable=True
                           )

                           wait_for_batch_completion_for_{JOB_ID} = DataprocBatchSensor(
                               task_id='wait_for_batch_completion_for_{JOB_ID}',
                               batch_id="{{ task_instance.xcom_pull(task_ids='Level_{LEVEL_ID}.Level_{LEVEL_ID}_Thread_{THREAD_ID}.{JOB_ID}.batch_id', key='batch-id') }}",
                               region=default_args['{JOB_ID}' + 'dataproc_serverless_region'],
                               poke_interval=400,
                               timeout=3600,
                               soft_fail=True
                           )

                           get_batch_for_{JOB_ID} = DataprocGetBatchOperator(
                               task_id="get_batch_for_{JOB_ID}",
                               batch_id="{{ task_instance.xcom_pull(task_ids='Level_{LEVEL_ID}.Level_{LEVEL_ID}_Thread_{THREAD_ID}.{JOB_ID}.batch_id', key='batch-id') }}",
                               region=default_args['{JOB_ID}' + 'dataproc_serverless_region']
                           )

                           push_batch_id_to_xcom_{JOB_ID} >> create_batch_for_{JOB_ID} >> wait_for_batch_completion_for_{JOB_ID} >> get_batch_for_{JOB_ID}
