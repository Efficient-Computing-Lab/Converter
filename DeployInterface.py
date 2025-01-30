import os
import random
import string
import json
import requests
import base64
from requests.exceptions import HTTPError
from converter_package import Converter
from converter_package import Parser
from converter_package import MatchingModel
from converter_package import ActionModel
from converter_package import ID
from converter_package import WorkflowModel
import yaml


def deployment(json_base64_string, name, file_path):
    nodelist = Parser.ReadFile(file_path)
    application_version='v5'
    # Create the namespace with a unique ID
    application_instance = ID.generate_k3s_namespace(name, application_version,
                                                     randomApplicationIntanceID())
    # cluster that is decided through matchmaking process
    cluster = "min5"
    externalIP = "195.212.4.114"
    # model for orchestrator that has the hardware requirements of components
    matchmaking_model = MatchingModel.generate(nodelist, application_instance)
    gpu_list = []
    if name == 'ovr':
        # name of the GPU model should be retrieved from a resource indexing mechanism
        gpu_models = ["nvidia.com/TU117_GEFORCE_GTX_1650"]
        matchmaking_components = matchmaking_model.get(application_instance)
        for component in matchmaking_components:
            component_name = component.get('component')
            host = component.get('host')
            requirements = host.get('requirements')
            hardware_requirements = requirements.get('hardware_requirements')
            if hardware_requirements.get('gpu'):
                gpu = hardware_requirements.get('gpu')
                gpu_brand = gpu.get('brand')
                for gpu_model in gpu_models:
                    if gpu_brand in gpu_model:
                        gpu_dict = {'component': component_name, 'gpu_model': gpu_model}
                        gpu_list.append(gpu_dict)

    # Generate configuration files for Orchestrator
    namespace_yaml = Converter.namespace(application_instance)
    secret_yaml = Converter.secret_generation(json_base64_string, application_instance)
    # gpu_model is an optional parameter
    deployment_files, persistent_files, service_files = Converter.tosca_to_k8s(nodelist,
                                                                               application_instance,
                                                                               cluster,
                                                                               externalIP, gpu_list)

    # model for lifecycle manager that has actions, their order and related components
    actions_set = ActionModel.generate(nodelist, application_instance)
    # workflows for lifecycle manager
    workflows_set = WorkflowModel.generate(nodelist, application_instance)

# Generate a random ID to emulate the application instance ID
def randomApplicationIntanceID():
    S = 5  # number of characters in the string.
    # call random.choices() string module to find the string in Uppercase + numeric data.
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
    return str(ran.lower())



def selector(name):
    if name == 'plexus':
        token_name = "token_name"
        token_pass = "password"
        file_path = 'application_models/v1/tosca_plexus.yaml'
    if name == 'orbk':
        token_name = "token_name"
        token_pass = "password"
        file_path = 'application_models/v1/tosca_orbk.yaml'
    if name == 'ovr':
        token_name = "token_name"
        token_pass = "password"
        file_path = 'application_models/v1/tosca_ovr.yaml'
    sample_string = token_name + ":" + token_pass
    sample_string_bytes = sample_string.encode("ascii")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    print(base64_string)
    json_file = {
        "auths": {
            "https://docker-registry:4444": {
                "auth": base64_string
            }
        }
    }
    json_string = json.dumps(json_file)
    json_base64 = base64.b64encode(json_string.encode('utf-8'))
    json_base64_string = json_base64.decode("utf-8")
    return json_base64_string, name, file_path


json_base64_string, name, file_path = selector("orbk")

deployment(json_base64_string, name, file_path)
