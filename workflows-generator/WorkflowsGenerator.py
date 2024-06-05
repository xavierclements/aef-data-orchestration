# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from commons import *

class WorkflowsGenerator:
    def __init__(self, workflow_config, exec_config, generate_for_pipeline, config_file ):
        self.workflow_config = workflow_config
        self.exec_config = exec_config
        self.generate_for_pipeline = generate_for_pipeline
        self.config_file = config_file
        self.workflow_template = ''
        self.level_template = ''
        self.thread_template = ''
        self.cloud_function_async_template = ''
        self.workflows_sync_template = ''
        self.cloud_function_sync_template = ''
        self.workflows_folder = "workflows-templates"


    def load_templates(self):
        """method for loading templates"""
        self.workflow_template = read_template("workflow",self.generate_for_pipeline, self.workflows_folder, "json")
        self.level_template = read_template("level",self.generate_for_pipeline, self.workflows_folder, "json")
        self.thread_template = read_template("thread",self.generate_for_pipeline, self.workflows_folder, "json")
        self.cloud_function_async_template = read_template("async_call",self.generate_for_pipeline, self.workflows_folder, "json")


    def get_unidented_template(self,template):
        new_template_lines = []
        lines = template.splitlines()
        for line in lines:
            line = line[12:]
            new_template_lines.append(line)
        return '\n'.join(new_template_lines)



    def generate_workflows_body(self):
        """method to generate cloud workflows body"""
        levels = self.process_levels(self.workflow_config)
        workflow_body = self.workflow_template.replace("<<LEVELS>>", "".join(levels))
        return workflow_body



    def process_levels(self,config):
        """method to process levels"""
        levels = []
        for index, level in enumerate(config):
            threads = self.process_threads(level.get("THREADS"), level.get("LEVEL_ID"))
            if len(threads) == 1:
                level_body = "               <<THREADS>>"
            else:
                level_body = self.level_template.replace("{LEVEL_ID}", level.get("LEVEL_ID"))
            level_body = level_body.replace("<<THREADS>>", "".join(threads))
            if len(level.get("THREADS")) == 1:
                level_body = self.get_unidented_template(level_body)
            levels.append(level_body)
        return levels


    def process_threads(self,threads, level_id):
        """method to process threads"""
        thread_bodies = []
        single_thread = len(threads) == 1
        for index, thread in enumerate(threads):
            thread_body = self.thread_template.replace("{LEVEL_ID}", level_id)
            thread_body = thread_body.replace("{THREAD_ID}", thread.get("THREAD_ID"))
            #first_step_in_thread = thread.get("STEPS")[0].get("JOB_ID") + "_" + thread.get("STEPS")[0].get("JOB_NAME")
            first_step_in_thread = thread.get("STEPS")[0].get("JOB_NAME")
            thread_body = thread_body.replace("{STARTING_JOB_ID}", first_step_in_thread)
            steps = self.process_steps(thread.get("STEPS"), level_id, thread.get("THREAD_ID"), single_thread)
            thread_body = thread_body.replace("<<THREAD_STEPS>>", "".join(steps))
            thread_bodies.append(thread_body)
        return thread_bodies


    def process_steps(self,steps, level_id, thread_id, single_thread):
        """method to process steps"""
        step_bodies = []
        cloud_function_intermediate_name = self.exec_config.get("pFunctionIntermediateName")
        jobs_definitions_bucket = self.exec_config.get("pJobsDefinitionsBucket")

        for index, step in enumerate(steps):
            step_body = ''
            if step.get("TYPE") == 'sync':
                step_body = self.process_step_sync(
                    assemble_cloud_function_id(cloud_function_intermediate_name, self.exec_config), step,
                    step.get("FUNCTION_NAME"))
            elif step.get("TYPE") == 'async':
                step_body = self.process_step_async(level_id,
                    assemble_cloud_function_id(cloud_function_intermediate_name, self.exec_config), step,
                    step.get("FUNCTION_ID_NAME"),
                    step.get("FUNCTION_STATUS_NAME"),jobs_definitions_bucket)
            #TODO workflows functionality
            elif step.get("TYPE") == 'workflows':
                workflows_name = step.get("workflows_name")
                workflows_id = assemble_workflows_id(workflows_name)
                step_body = self.process_step_workflows(workflows_id, step)

            step_body = step_body.replace("{LEVEL_ID}", level_id)
            step_body = step_body.replace("{THREAD_ID}", thread_id)
            step_body = self.process_next_step(steps, step, index, level_id, thread_id, step_body,single_thread)
            step_bodies.append(step_body)
        return step_bodies


    def process_step_sync(self,cloud_function_level_1_id, step, cloud_function_name):
        """method to process sync step"""
        #step_name = step.get("JOB_ID") + "_" + step.get("JOB_NAME")
        step_name = step.get("JOB_NAME")
        step_body = self.cloud_function_sync_template.replace("{JOB_ID}", step_name)
        step_body = step_body.replace("{CLOUD_FUNCITON_ID}", cloud_function_level_1_id)
        step_body = step_body.replace("{CLOUD_FUNCTION_TO_INVOKE}", cloud_function_name)
        step_body = step_body.replace("{ENVIRONMENT}", self.environment)
        step_body = step_body.replace("{JOB_IDENTIFIER}", step.get("JOB_ID"))
        step_body = step_body.replace("{JOB_NAME}", step.get("JOB_NAME"))
        if "TIMEOUT_SECONDS" in step.keys():
            step_body = step_body.replace("{TIMEOUT_SECONDS_BLOCK}",
                                          '"TimeoutSeconds": ' + step.get("TIMEOUT_SECONDS") + ',')
        else:
            step_body = step_body.replace("{TIMEOUT_SECONDS_BLOCK}", '')

        #TODO continue if fail logic
        if "CONTINUE_IF_FAIL" in step.keys():
            step_body = step_body.replace("{CONTINUE_IF_FAIL_BLOCK}", ',"PcontinueIfFail": "True"')
        else:
            step_body = step_body.replace("{CONTINUE_IF_FAIL_BLOCK}", '')

        return step_body


    def process_step_async(self,level_id, cloud_funciton_level_1_id, step, FUNCTION_ID_NAME, FUNCTION_STATUS_NAME, jobs_definitions_bucket):
        """method to process async step"""
        #step_name = step.get("JOB_ID") + "_" + step.get("JOB_NAME")
        step_name = step.get("JOB_NAME")
        step_body = self.cloud_function_async_template.replace("{JOB_ID}", step_name)
        step_body = step_body.replace("{LEVEL_ID}", level_id)
        step_body = step_body.replace("{CLOUD_FUNCTION_ID}", cloud_funciton_level_1_id)
        step_body = step_body.replace("{CLOUD_FUNCTION_ID_TO_INVOKE}", assemble_cloud_function_id(FUNCTION_ID_NAME,self.exec_config))
        step_body = step_body.replace("{CLOUD_FUNCTION_STATUS_TO_INVOKE}",assemble_cloud_function_id(FUNCTION_STATUS_NAME,self.exec_config))
        step_body = step_body.replace("{JOB_IDENTIFIER}", step.get("JOB_ID"))
        step_body = step_body.replace("{JOB_NAME}", step.get("JOB_NAME"))
        step_body = step_body.replace("{WAIT_TIME_SECONDS}", step.get("WAIT_TIME_SECONDS"))
        step_body = step_body.replace("{WAIT_TIME_SECONDS}", step.get("WAIT_TIME_SECONDS"))
        step_body = step_body.replace("{ASYNC_JOB_ID_VARIABLE_NAME}", step.get("JOB_ID") +
                                      "_async_job_id")
        step_body = step_body.replace("{ASYNC_JOB_STATUS_VARIABLE_NAME}", step.get("JOB_ID") +
                                      "_async_job_status")
        if "READ_INPUT_FROM" in step.keys():
            step_body = step_body.replace("{READ_INPUT_FROM}", step.get("READ_INPUT_FROM"))
        else:
            step_body = step_body.replace("{READ_INPUT_FROM}", "ENV")
        if "TIMEOUT_SECONDS" in step.keys():
            step_body = step_body.replace("{TIMEOUT_SECONDS_BLOCK}",
                                          '"TimeoutSeconds": ' + step.get("TIMEOUT_SECONDS") + ',')
        else:
            step_body = step_body.replace("{TIMEOUT_SECONDS_BLOCK}", '')
        if "ASYNC_TIMEOUT_LOOP_IN_MINUTES" in step.keys():
            step_body = step_body.replace("{ASYNC_TIMEOUT_LOOP_BLOCK}",
                                          ',"PtimeoutMinutes": ' + step.get(
                                              "ASYNC_TIMEOUT_LOOP_IN_MINUTES"))
        else:
            step_body = step_body.replace("{ASYNC_TIMEOUT_LOOP_BLOCK}", '')
        if "CONTINUE_IF_FAIL" in step.keys():
            step_body = step_body.replace("{CONTINUE_IF_FAIL_BLOCK}", ',"PcontinueIfFail": "True"')
        else:
            step_body = step_body.replace("{CONTINUE_IF_FAIL_BLOCK}", '')
        if "STEP_PROPERTIES" in step.keys():
            step_body = step_body.replace("{STEP_PROPERTIES_BLOCK}", "step_properties: > \n"
                                          + "                                                                 "
                                          + step.get("STEP_PROPERTIES"))
        else:
            step_body = step_body.replace("{STEP_PROPERTIES_BLOCK}", "step_properties: > \n"
                                          + "                                                                 "
                                          + str(f'{{"jobs_definitions_bucket":"{jobs_definitions_bucket}"}}'))
        return step_body


    def process_step_workflows(self,workflows_id, step):
        """method to process step of workflows type"""
        #step_name = step.get("JOB_ID") + "_" + step.get("JOB_NAME")
        step_name = step.get("JOB_NAME")
        step_body = self.workflows_sync_template.replace("{JOB_ID}", step_name)
        step_body = step_body.replace("{workflows_id}", workflows_id)
        return step_body



    def process_next_step(self,steps, step, index, level_id, thread_id, step_body, single_thread):
        """method to process next step"""
        if step.get("TYPE") in ('sync', 'async', 'workflows'):
            if "NEXT" not in step.keys():
                try:
                    next_step = steps[index + 1]
                    #next_step_name = next_step.get("JOB_ID") + "_" + next_step.get("JOB_NAME")
                    next_step_name = next_step.get("JOB_NAME")
                    step_body = step_body.replace("{NEXT_JOB_ID}", next_step_name)
                except (KeyError, IndexError):
                    if level_exists(int(level_id) + 1, self.workflow_config) and single_thread:
                        if level_exists_and_is_parallel(int(level_id) + 1, self.workflow_config):
                            step_body = step_body.replace("{NEXT_JOB_ID}",
                                                     "Level_" + str(int(level_id) + 1))
                        else:
                            step_body = step_body.replace("{NEXT_JOB_ID}",
                                                          "Level_" + str(int(level_id) + 1) + "_Thread_" + thread_id)
                    else:
                        if single_thread:
                            step_body = step_body.replace("{NEXT_JOB_ID}","end")
                        else:
                            step_body = step_body.replace("{NEXT_JOB_ID}","continue")
            else:
                next_step = find_step_by_id(step.get("NEXT"))
                #next_step_name = next_step.get("JOB_ID") + "_" + next_step.get("JOB_NAME")
                next_step_name = next_step.get("JOB_NAME")
                step_body = step_body.replace("{NEXT_JOB_ID}", next_step_name)

        return step_body

