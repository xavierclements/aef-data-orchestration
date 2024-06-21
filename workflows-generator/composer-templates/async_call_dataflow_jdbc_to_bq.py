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



