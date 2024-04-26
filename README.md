# Converter


Converter is a reasoning tool designed for the cloud language known as CEAML. [CEAML](application_models/) is an extension of [TOSCA](https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.3/TOSCA-Simple-Profile-YAML-v1.3.html) capable to describe deployment and runtime adaptation for platforms that utilize both Cloud and Edge resources. It can parse CEAML entities and translate them into configuration files for K3s or Kubevirt. Additionally, it generates action models, workflow models, and matchmaking models that can simplify deployment and runtime adaptation for distributed orchestrators across multiple K3s clusters. CEAML and Converter have been utilized by the ACCORDION EU project to aid the orchestrator and lifecycle manager of the system.

1. [Installation](#installation)
2. [Deploy an application](#deploy-an-application)
3. [Terminate an application](#terminate-an-application)
4. [Scale out an application](#scale-out-an-application)

## Installation
Converter is packaged as a Python library, it can be installed it with the following command:
```bash
pip3 install converter-package==3.3
```
## Deploy an application
To deploy an application described in CEAML in Kubernetes or Kubevirt developers should have the following required inputs:

1. Provide access tokens for the private registry housing their images and encode them in base64.
   The following code snippet provides on how you could generate the base64 encoding of token name and password.
2. Provide the path of the model written in CEAML

Here's an example demonstrating how to provide inputs 1. and 2. In this scenario, there's a function called "selector" that requires the application's name as input. If the name matches one of the predefined ones, it retrieves the access tokens and creates the base64-encoded version of the access token. Additionally, the function defines the path of the model written in CEAML. Finally, the function outputs the base64 access token, the application's name, and the model's path.

```python
def selector(name):
    if name == 'plexus':
        token_name = "token_name"
        token_pass = "password"
        file_path = 'application_models/tosca_plexus.yaml'
    if name == 'orbk':
        token_name = "token_name"
        token_pass = "password"
        file_path = 'application_models/tosca_orbk.yaml'
    if name == 'ovr':
        token_name = "token_name"
        token_pass = "password"
        file_path = 'application_models/tosca_ovr.yaml'
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
```
3. Provide the version of their application as a whole
4. Provide external IPs that could potentially be used by a component
5. Provide the cluster ID that the application should be deployed to
6. Provide a GPU list that is available on that cluster. If there are no GPUs on the cluster, provide an empty list

An example follows that presents way to provide inputs 3.,4.,5. and 6. The code snippet presents
a function named deployment that retrieves the outputs of the previously mentioned selector function.
The application version, cluster ID, external IP and GPU list are hardcoded in order to simplify the example.
```python
def deployment(json_base64_string, name, file_path):
    nodelist, imagelist = Parser.ReadFile(file_path)
    application_version='v5'
    # Create the namespace with a unique ID
    application_instance = ID.generate_k3s_namespace(name, application_version, randomApplicationIntanceID())

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
                                                                               application_instance, cluster,
                                                                               externalIP, gpu_list)

    # model for lifecycle manager that has actions, their order and related components
    actions_set = ActionModel.generate(nodelist, application_instance)

    print(actions_set)
    # workflows for lifecycle manager
    workflows_set = WorkflowModel.generate(nodelist, application_instance)
    print(workflows_set)
    print(namespace_yaml)
    print(secret_yaml)
    print(deployment_files)
    print(yaml.dump(deployment_files))
    print(matchmaking_model)

    print(persistent_files)
    print(service_files)
```
All of the above information of course could be either provided manually of by a mechanism. It clearly depends on how developers plan to use the Converter

By combining both examples mentioned above we have a complete example ([DeployInterface.py](DeployInterface.py)) on how to generate the deployment files with Converter. The code is also available below as a snippet.
```python
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
    application_instance = ID.generate_k3s_namespace(name, application_version, randomApplicationIntanceID())

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
                                                                               application_instance, cluster,
                                                                               externalIP, gpu_list)

    # model for lifecycle manager that has actions, their order and related components
    actions_set = ActionModel.generate(nodelist, application_instance)

    print(actions_set)
    # workflows for lifecycle manager
    workflows_set = WorkflowModel.generate(nodelist, application_instance)
    print(workflows_set)
    print(namespace_yaml)
    print(secret_yaml)
    print(deployment_files)
    print(yaml.dump(deployment_files))
    print(matchmaking_model)

    print(persistent_files)
    print(service_files)

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
        file_path = 'application_models/tosca_plexus.yaml'
    if name == 'orbk':
        token_name = "token_name"
        token_pass = "password"
        file_path = 'application_models/tosca_orbk.yaml'
    if name == 'ovr':
        token_name = "token_name"
        token_pass = "password"
        file_path = 'application_models/tosca_ovr.yaml'
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
```
As it shown in the above code, the steps to generate Kubernetes or Kubevirt files for deployement are:
1. Call **ID.generate_k3s_namespace(name, application_version, randomApplicationIntanceID())** and **Converter.namespace(application_instance)** to generate a namespace with unique ID. 
   The **ID.generate_k3s_namespace** function in order to generate unique ID requires to know the name of the application, the version of the application and a random alphanumeric. After the creation of this unique ID you call **Converter.namespace()** and pass the uniqueID as a parameter in order to generate the K3s namespace.(Required)
2. Call **MatchingModel.generate(nodelist, application_instance)** to generate model for orchestrator that has the hardware requirements of components.
   This function requires to know the list that contains all the instances of CEAML entities (nodeList) and the unique ID of the instance to be deployed (application_instance). (Optional)
3. Call **Converter.secret_generation(json_base64_string, application_instance)** to generate the required secrets. This function requires to know the base64 version of the access tokens and the unique ID of the instance to be deployed.  (Required)
4. Call **Converter.tosca_to_k8s(nodelist, application_instance, cluster, externalIP, gpu_list)** to generate deployment files, persistent volumes and services. This function requires to know the list that contains all the instances of CEAML entities (nodeList) and the unique ID of the instance to be deployed (application_instance), the cluster ID, potential external IP and potential GPU list (Required)
5. Call **ActionModel.generate(nodelist, application_instance)** to generate a model that includes components and the related actions that may be performed on them. This function requires to know the list that contains all the instances of CEAML entities (nodeList) and the unique ID of the instance to be deployed (application_instance). (Optional)
6. Call **WorkflowModel.generate(nodelist, application_instance)** to generate a model that includes worklows that include runtime adaptation actions that should be performed under certain conditions. This function requires to know the list that contains all the instances of CEAML entities (nodeList) and the unique ID of the instance to be deployed (application_instance). (Optional)

In case developers want to use a conventional deployment on Kubernetes or Kubevirt they should just perform the required steps. Although, in case they have generated a distributed orchestrator that operates above clusters they could potentially use also the steps that are marked as optional to assist the orchestration process.


All the outputs of methods are stored in memory, and developers have the freedom to either save them as files or use them as they are. To apply the outputs, developers should utilize the kubectl apply -f command or its equivalent in the Kubernetes API to the respective cluster master.

## Terminate an application
To undeploy an application described in CEAML in Kubernetes or Kubevirt developers should have the following required inputs:
1. The name of the running instance, for example acc-uc2orbk-0-0-4-00036-gameserver-7reio-min1
2. Provide the path of the model written in CEAML

All of the above information of course could be either provided manually of by a mechanism. It clearly depends on how developers plan to use the Converter

A usage example on how to generate the deployment files to perform termination with Converter is the [TerminateInterface.py](TerminateInterface.py). The code is also available below as a snippet.
```python
from DeployInterface import selector
from converter_package import Converter

componentInfo = "acc-uc2orbk-0-0-4-00036-gameserver-7reio-min1""
if 'orbk' in componentInfo:
    json_base64_string, url, name = selector('orbk')
    file_path = 'application_models/tosca_orbk.yaml'

deployment = Converter.undeploy(componentInfo, file_path)
print(deployment)

 ```
As it shown in the above code snippet only  the Converter.undeploy(componentInfo, file_path) should be called. This method will call the Parser by its own it will parse the CEAML model and generate the termination plan for the running instance.

All the outputs of methods are stored in memory, and developers have the freedom to either save them as files or use them as they are. To apply the outputs, developers should utilize the kubectl delete -f command or its equivalent in the Kubernetes API to the respective cluster master.
## Scale out an application

Scaling out an application described in CEAML in Kubernetes or Kubevirt involves deploying a second instance of the application component with the same running instance ID to a separate cluster. This scenario is exclusive to distributed orchestrators. Developers should have the following required inputs:
1. The name of the running instance, for example acc-uc2orbk-0-0-4-00036-gameserver-7reio-min1
2. Provide the path of the model written in CEAML

A usage example on how to generate the deployment files to perform scale out with Converter is the [ScaleOutInterface.py](ScaleOutInterface.py). The code is also available below as a snippet.
```python
from DeployInterface import selector
from converter_package import Converter

componentInfo = "acc-uc2orbk-0-0-4-00036-gameserver-7reio-min1"
if 'orbk' in componentInfo:
    json_base64_string, url, name = selector('orbk')
    file_path = 'application_models/tosca_orbk.yaml'

deployment = Converter.scale_out_to_k8s(componentInfo, file_path)
print(deployment)
 ```
As it shown in the above code snippet only  the Converter.scale_out_to_k8s(componentInfo, file_path) should be called. This method will call the Parser by its own it will parse the CEAML model and generate the scale out plan for the running instance.

All the outputs of methods are stored in memory, and developers have the freedom to either save them as files or use them as they are. To apply the outputs, developers should utilize the kubectl apply -f command or its equivalent in the Kubernetes API to the respective cluster master.