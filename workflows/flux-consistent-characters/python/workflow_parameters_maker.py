import json
from workflow_api_parameter_creator import workflow_api_parameters_creator

with open('workflow_api.json', 'r') as f:
    workflow_json = json.load(f)
    
parameters = workflow_api_parameters_creator(workflow_json)

with open('workflow_api_parameters.json', 'w') as f:
    json.dump(parameters, f, indent=4)

