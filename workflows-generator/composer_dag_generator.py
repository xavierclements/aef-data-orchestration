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

import json
import sys
import os
from commons import *

def main():
    """
    Main function for workflows generator

    :param workflow_file: Json definition file in the form of THREADS and STEPS
    :param config_file: Json parameters file
    :param output_file: Cloud Workflows generated file
    :param generate_for_pipeline: Boolean to identify if the run is part of a CICD pipeline
    :return: NA
    """
    global workflow_config, exec_config, generate_for_pipeline, environment, config_file
    usage(4,'py')
    workflow_file = sys.argv[1]
    config_file = sys.argv[2]
    output_file = sys.argv[3]
    generate_for_pipeline = bool(sys.argv[4])
    encoding = "utf-8"
    with open(workflow_file, encoding=encoding) as json_file:
        workflow_config = json.load(json_file)
    if generate_for_pipeline:
        with open(os.path.dirname(__file__) + '/' + config_file, encoding=encoding) as json_file:
            exec_config = json.load(json_file)
    else:
        with open(os.getcwd() + '/' + config_file, encoding=encoding) as json_file:
            exec_config = json.load(json_file)
    exec_config = process_config_key_values(exec_config)
    load_templates()
    workflow_body = generate_workflows_body(workflow_config)
    write_result(output_file, workflow_body)





def load_templates():
    """method for loading templates"""
    global workflow_template, level_template, thread_template, \
        cloud_function_sync_template, cloud_function_async_template
    workflow_template = read_template("workflow",generate_for_pipeline, "composer-templates", "py")
    level_template = read_template("level",generate_for_pipeline, "composer-templates", "py")
    thread_template = read_template("thread",generate_for_pipeline, "composer-templates", "py")
    cloud_function_async_template = read_template("async_call_dataform",generate_for_pipeline, "composer-templates", "py")



def generate_workflows_body(config):
    """method to generate cloud workflows body"""
    levels = process_levels(config)
    workflow_body = workflow_template.replace("<<LEVELS>>", "".join(levels))
    workflow_body = workflow_body.replace("<<LEVEL_DEPENDENCIES>>", get_level_dependency_string(config))
    return workflow_body


def get_level_dependency_string(config):
    level_names = []
    for level in config:
        level_name = "tg_Level_" + level.get("LEVEL_ID")
        level_names.append(level_name)
    return " >> ".join(level_names)

def process_levels(config):
    """method to process levels"""
    levels = []
    for index, level in enumerate(config):
        threads = process_threads(level.get("THREADS"), level.get("LEVEL_ID"))
        level_body = level_template.replace("{LEVEL_ID}", level.get("LEVEL_ID"))
        level_body = level_body.replace("<<THREADS>>", "".join(threads))
        level_body = level_body.replace("<<THREAD_DEPENDENCIES>>",
                                        get_thread_dependency_string(level.get("THREADS"), level.get("LEVEL_ID")))
        levels.append(level_body)

    return levels


def get_thread_dependency_string(threads, level_id):
    thread_names = []
    for thread in threads:
        thread_name = "tg_level_" + level_id + "_Thread_" + thread.get("THREAD_ID")
        thread_names.append(thread_name)
    return "\n           ".join(thread_names)


def process_threads(threads, level_id):
    """method to process threads"""
    thread_bodies = []
    for index, thread in enumerate(threads):
        thread_body = thread_template.replace("{LEVEL_ID}", level_id)
        thread_body = thread_body.replace("{THREAD_ID}", thread.get("THREAD_ID"))
        steps = process_steps(thread.get("STEPS"), level_id, thread.get("THREAD_ID"))
        thread_body = thread_body.replace("<<THREAD_STEPS>>", "".join(steps))
        thread_body = thread_body.replace("<<THREAD_STEPS_DEPENDENCIES>>",
                                          get_steps_dependency_string(thread.get("STEPS")))
        thread_bodies.append(thread_body)
    return thread_bodies


def get_steps_dependency_string(steps):
    step_names = []
    for step in steps:
        step_name = "task_" + step.get("JOB_ID") + "_" + step.get("JOB_NAME")
        step_names.append(step_name)
    return " >> ".join(step_names)

def process_steps(steps, level_id, thread_id):
    """method to process steps"""
    step_bodies = []

    for index, step in enumerate(steps):
        step_body = process_step_async(level_id, thread_id, step)
        step_body = step_body.replace("{LEVEL_ID}", level_id)
        step_body = step_body.replace("{THREAD_ID}", thread_id)
        step_bodies.append(step_body)
    return step_bodies


def process_step_async(level_id, thread_id, step):
    """method to process async step"""
    step_name = step.get("JOB_ID") + "_" + step.get("JOB_NAME")
    step_body = cloud_function_async_template.replace("{JOB_ID}", step_name)
    step_body = step_body.replace("{LEVEL_ID}", level_id)
    step_body = step_body.replace("{THREAD_ID}", thread_id)
    step_body = step_body.replace("{JOB_IDENTIFIER}", step.get("JOB_ID"))
    step_body = step_body.replace("{JOB_NAME}", step.get("JOB_NAME"))

    if "READ_INPUT_FROM" in step.keys():
        step_body = step_body.replace("{READ_INPUT_FROM}", step.get("READ_INPUT_FROM"))
    else:
        step_body = step_body.replace("{READ_INPUT_FROM}", "ENV")

    return step_body


main()
