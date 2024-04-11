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
from commons import *
from ComposerDagGenerator import ComposerDagGenerator
from WorkflowsGenerator import WorkflowsGenerator

def main():
    """
    Main function for workflows generator

    :param workflow_file: Json definition file in the form of THREADS and STEPS
    :param config_file: Json parameters file
    :param output_file: Cloud Workflows generated file
    :param generate_for_pipeline: Boolean to identify if the run is part of a CICD pipeline
    :return: NA
    """
    encoding = "utf-8"
    workflow_file = sys.argv[1]
    with open(workflow_file, encoding=encoding) as json_file:
        workflow_config = json.load(json_file)
    if workflow_config.get("engine") == 'cloud_workflows':
        usage(4,'json')
    else:
        usage(4,'py')
    json_file_name = workflow_file.split("/")[-1].split(".")[0]
    config_file = sys.argv[2]
    output_file = sys.argv[3]
    generate_for_pipeline = bool(sys.argv[4])

    if generate_for_pipeline:
        with open(os.path.dirname(__file__) + '/' + config_file, encoding=encoding) as json_file:
            exec_config = json.load(json_file)
    else:
        with open(os.getcwd() + '/' + config_file, encoding=encoding) as json_file:
            exec_config = json.load(json_file)
    exec_config = process_config_key_values(exec_config)
    generator = None
    if workflow_config.get("engine") == 'cloud_workflows':
        workflow_config = workflow_config.get("definition")
        generator = WorkflowsGenerator(workflow_config, exec_config, generate_for_pipeline, config_file)
        generator.load_templates()
    elif workflow_config.get("engine") == 'composer':
        workflow_config = workflow_config.get("definition")
        generator = ComposerDagGenerator(workflow_config, exec_config,
                                         generate_for_pipeline, config_file, json_file_name)
        generator.load_templates()
    workflow_body = generator.generate_workflows_body()
    write_result(output_file, workflow_body)


main()