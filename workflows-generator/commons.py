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

import sys
import os

def usage(args_expected, extension):
    """ method to explain usage"""
    if len(sys.argv) < args_expected + 1:
        print('!Error, number of arguments passed=' + str(len(sys.argv) - 1) + ' expected=' + str(
            args_expected))
        print('...Usage: ' + sys.argv[
            0] + ' <workflow_file>.json <parameters-file>.json <result-file>.' + extension + ' '
                 '<gcp-account-number> <deploy-for-pipeline(True|False)')
        sys.exit(0)

def process_config_key_values(config_array):
    """method for config key values"""
    result = {}
    for pair in config_array:
        result[pair.get("ParameterKey")] = pair.get("ParameterValue")
    return result


def read_template(template, generate_for_pipeline, templates_folder, file_extension):
    """method to read templates"""
    try:
        if generate_for_pipeline:
            with open(os.path.dirname(__file__) + "/"+templates_folder+"/" + template + '.'+file_extension, 'r',
                      encoding="utf-8") as file:
                data = file.read()
                return data
        else:
            with open(os.getcwd() + "/"+templates_folder+"/" + template + '.' + file_extension, 'r', encoding="utf-8") \
                    as file:
                data = file.read()
                return data

    except Exception as err:
        print('Error reading template file: ' + str(type(err)))
        raise err


def find_step_by_id(step_id, workflow_config):
    """method to find step by id"""
    for level in workflow_config:
        for thread in level.get("THREADS"):
            for step in thread.get("STEPS"):
                if step.get("JOB_ID") == step_id:
                    return step
    return None

def level_exists(level_number, workflow_config):
    for level in workflow_config:
        if int(level.get("LEVEL_ID")) == level_number:
            return True
    return False

def level_exists_and_is_parallel(level_number, workflow_config):
    for level in workflow_config:
        if int(level.get("LEVEL_ID")) == level_number:
            if len(level.get("THREADS")) > 1:
                return True
    return False



def write_result(output_file, content):
    """
    Function to write result to a file
    :param output_file:
    :param content:
    :return:
    """
    try:
        # Create directories if they don't exist
        dirname = os.path.dirname(output_file)
        if dirname:  # Only create directories if the path isn't just a filename
            os.makedirs(dirname, exist_ok=True)
        file_out = open(output_file, "w", encoding="utf-8")
        file_out.write(content)
        file_out.close()
    except Exception as err:
        print('Error writing on output file: ' + str(type(err)))
        raise err


def assemble_cloud_function_id(name, exec_config):
    """
    Function to assemble cloud function ID
    :param name: name of the Cloud function
    :return: if of the cloud function
    ej: "https://us-central1-dp-111-orc.cloudfunctions.net/async-function"
    """
    project_id = exec_config.get("pProjectID")
    region = exec_config.get("pRegion")
    return f"https://{region}-{project_id}.cloudfunctions.net/{name}"


def assemble_workflows_id(name, exec_config):
    """
    Function to assemble cloud workflows id
    :param name: name of the Cloud Workflow
    :return: workflows id
    """
    project_id = exec_config.get("pProjectID")
    region = exec_config.get("pRegion")
    return f"projects/{project_id}/locations/{region}/workflows/{name}"