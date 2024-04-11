                    with TaskGroup(group_id="{JOB_ID}") as task_{JOB_ID}:

                        #execute_dataflow_job_{JOB_ID} = DataflowTemplatedJobStartOperator(
                        #    task_id="dataflow_jdbc_to_bq_{JOB_ID}",
                        #    template="gs://dataflow-templates/latest/Jdbc_to_BigQuery",
                        #    parameters={
                        #        "driverJars": "gs://your-bucket/driver_jar1.jar,gs://your-bucket/driver_jar2.jar",
                        #        "driverClassName": "com.mysql.jdbc.Driver",
                        #        "connectionURL": "connectionURL",
                        #        "outputTable": "<project>:<dataset>.<table_name>",
                        #        "connectionProperties": "unicode=true;characterEncoding=UTF-8",
                        #        "username": "",
                        #        "password": "",
                        #        "query": "",
                        #        "useColumnAlias":"True"
                        #    },
                        #)

                        execute_dataflow_job_{JOB_ID} = empty.EmptyOperator(
                            task_id="dataflow_jdbc_to_bq_{JOB_ID}",
                            trigger_rule='all_success'
                        )

                        execute_dataflow_job_{JOB_ID}



