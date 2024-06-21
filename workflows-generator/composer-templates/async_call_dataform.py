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

                           # compilation
                           create_compilation_result_for_{JOB_ID} = DataformCreateCompilationResultOperator(
                               task_id="compilation_task_{JOB_ID}",
                               compilation_result={
                                   "git_commitish": "main",
                                   "code_compilation_config": {
                                       "vars": {
                                            "start_date": "{{ params.start_date_str }}",
                                            "end_date": "{{ params.end_date_str }}"
                                       }
                                   }
                               }
                           )

                           # workflow invocation in dataform
                           create_workflow_{JOB_ID}_invocation = DataformCreateWorkflowInvocationOperator(
                               task_id='workflow_inv_{JOB_ID}',
                               asynchronous=True,
                               workflow_invocation={
                                   "compilation_result": "{{ task_instance.xcom_pull('Level_{LEVEL_ID}.Level_{LEVEL_ID}_Thread_{THREAD_ID}.{JOB_ID}.compilation_task_{JOB_ID}')['name'] }}",
                                   "invocation_config": { "included_tags": ["{JOB_ID}"],
                                                          "transitive_dependencies_included": True
                                                        }
                               },
                               trigger_rule='all_success'
                           )

                           is_workflow_{JOB_ID}_invocation_done = DataformWorkflowInvocationStateSensor(
                               task_id="is_workflow_{JOB_ID}_invocation_done",
                               workflow_invocation_id=("{{ task_instance.xcom_pull('Level_{LEVEL_ID}.Level_{LEVEL_ID}_Thread_{THREAD_ID}.{JOB_ID}.workflow_inv_{JOB_ID}')['name'].split('/')[-1] }}"),
                               expected_statuses={WorkflowInvocation.State.SUCCEEDED},
                               failure_statuses={WorkflowInvocation.State.FAILED, WorkflowInvocation.State.CANCELLED},
                           )

                           create_compilation_result_for_{JOB_ID} >> create_workflow_{JOB_ID}_invocation >> is_workflow_{JOB_ID}_invocation_done

