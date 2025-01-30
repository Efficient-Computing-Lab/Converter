from DeployInterface import selector
from converter_package import Converter

componentInfo = "acc-uc2orbk-0-0-4-00036-gameserver-7reio-min1"
if 'orbk' in componentInfo:
    json_base64_string, url, name = selector('orbk')
    file_path = 'application_models/v1/tosca_orbk.yaml'

deployment = Converter.scale_out_to_k8s(componentInfo, file_path)
print(deployment)
