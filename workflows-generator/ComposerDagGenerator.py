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


class ComposerDagGenerator:
    def __init__(self, workflow_config, exec_config, generate_for_pipeline, config_file, json_file_name):
        self.workflow_config = workflow_config
        self.exec_config = exec_config
        self.generate_for_pipeline = generate_for_pipeline
        self.config_file = config_file
        self.json_file_name = json_file_name
        self.workflow_template = ''
        self.level_template = ''
        self.thread_template = ''
        self.dataform_tag_executor_template = ''
        self.dataflow_flextemplate_job_executor_template = ''
        self.dataproc_serverless_job_executor_template = ''

    def load_templates(self):
        """method for loading templates"""
        self.workflow_template = read_template("workflow", self.generate_for_pipeline, "composer-templates", "py")
        self.level_template = read_template("level", self.generate_for_pipeline, "composer-templates", "py")
        self.thread_template = read_template("thread", self.generate_for_pipeline, "composer-templates", "py")
        # add new templates for other executors here
        self.dataform_tag_executor_template = read_template("dataform_tag_executor", self.generate_for_pipeline,
                                                            "composer-templates", "py")
        self.dataflow_flextemplate_job_executor_template = read_template("dataflow_flextemplate_job_executor",
                                                                         self.generate_for_pipeline,
                                                                         "composer-templates", "py")
        self.dataproc_serverless_job_executor_template = read_template("dataproc_serverless_job_executor",
                                                                       self.generate_for_pipeline, "composer-templates",
                                                                       "py")

    def generate_workflows_body(self):
        """method to generate Airflow body"""
        levels = self.process_levels(self.workflow_config)
        workflow_body = self.workflow_template.replace("<<LEVELS>>", "".join(levels))
        workflow_body = workflow_body.replace("<<LEVEL_DEPENDENCIES>>",
                                              self.get_level_dependency_string(self.workflow_config))
        workflow_body = workflow_body.replace("<<DAG_NAME>>", self.json_file_name)
        workflow_body = workflow_body.replace("<<STEPS_ARGS>>", self.process_steps_vars(self.workflow_config))
        return workflow_body

    def process_steps_vars(self, config):
        """Method to process steps vars"""
        string_code = "{JOB_ID} = extract_job_params('{JOB_ID}','{FUNCTION_NAME}')\nfor key, value in {JOB_ID}.items():\n\tdefault_args['{JOB_ID}'+key] = value\n"
        vars = [
            string_code.format(
                JOB_ID=step.get("JOB_NAME"), FUNCTION_NAME=step.get("COMPOSER_STEP")
            )
            for level in config
            for thread in level.get("THREADS", [])
            for step in thread.get("STEPS", [])
        ]
        return '\n'.join(vars)

    def get_level_dependency_string(self, config):
        level_names = []
        for level in config:
            level_name = "tg_Level_" + level.get("LEVEL_ID")
            level_names.append(level_name)
        return " >> ".join(level_names)

    def process_levels(self, config):
        """method to process levels"""
        levels = []
        for index, level in enumerate(config):
            threads = self.process_threads(level.get("THREADS"), level.get("LEVEL_ID"))
            level_body = self.level_template.replace("{LEVEL_ID}", level.get("LEVEL_ID"))
            level_body = level_body.replace("<<THREADS>>", "".join(threads))
            level_body = level_body.replace("<<THREAD_DEPENDENCIES>>",
                                            self.get_thread_dependency_string(level.get("THREADS"),
                                                                              level.get("LEVEL_ID")))
            levels.append(level_body)

        return levels

    def get_thread_dependency_string(self, threads, level_id):
        thread_names = []
        for thread in threads:
            thread_name = "tg_level_" + level_id + "_Thread_" + thread.get("THREAD_ID")
            thread_names.append(thread_name)
        return "\n           ".join(thread_names)

    def process_threads(self, threads, level_id):
        """method to process threads"""
        thread_bodies = []
        for index, thread in enumerate(threads):
            thread_body = self.thread_template.replace("{LEVEL_ID}", level_id)
            thread_body = thread_body.replace("{THREAD_ID}", thread.get("THREAD_ID"))
            steps = self.process_steps(thread.get("STEPS"), level_id, thread.get("THREAD_ID"))
            thread_body = thread_body.replace("<<THREAD_STEPS>>", "".join(steps))
            thread_body = thread_body.replace("<<THREAD_STEPS_DEPENDENCIES>>",
                                              self.get_steps_dependency_string(thread.get("STEPS")))
            thread_bodies.append(thread_body)
        return thread_bodies

    def get_steps_dependency_string(self, steps):
        step_names = []
        for step in steps:
            step_name = step.get("JOB_NAME")
            step_names.append(step_name)
        return " >> ".join(step_names)

    def process_steps(self, steps, level_id, thread_id):
        """method to process steps"""
        step_bodies = []

        for index, step in enumerate(steps):
            step_body = self.process_step_async(level_id, thread_id, step)
            step_body = step_body.replace("{LEVEL_ID}", level_id)
            step_body = step_body.replace("{THREAD_ID}", thread_id)
            step_bodies.append(step_body)
        return step_bodies

    def process_step_async(self, level_id, thread_id, step):
        """method to process async step"""
        step_name = step.get("JOB_NAME")
        step_body = ''
        ##Add new templates here
        if "dataform-tag-executor" in step.get("COMPOSER_STEP"):
            step_body = self.dataform_tag_executor_template.replace("{JOB_ID}", step_name)
        if "dataflow-flextemplate-job-executor" in step.get("COMPOSER_STEP"):
            step_body = self.dataflow_flextemplate_job_executor_template.replace("{JOB_ID}", step_name)
        if "dataproc-serverless-job-executor" in step.get("COMPOSER_STEP"):
            step_body = self.dataproc_serverless_job_executor_template.replace("{JOB_ID}", step_name)
        step_body = step_body.replace("{LEVEL_ID}", level_id)
        step_body = step_body.replace("{THREAD_ID}", thread_id)
        step_body = step_body.replace("{JOB_IDENTIFIER}", step.get("JOB_ID"))
        step_body = step_body.replace("{JOB_NAME}", step.get("JOB_NAME"))

        return step_body
