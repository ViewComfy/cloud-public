import json
from workflow_api_parameter_creator import workflow_api_parameters_creator
import argparse

parser = argparse.ArgumentParser(description='Process workflow API parameters')
parser.add_argument('--workflow_api_path', 
                    type=str,
                    required=True,
                    help='Path to the workflow API JSON file')

# Parse arguments
args = parser.parse_args()

with open(args.workflow_api_path, 'r') as f:
    workflow_json = json.load(f)
    
parameters = workflow_api_parameters_creator(workflow_json)

with open('workflow_api_parameters.json', 'w') as f:
    json.dump(parameters, f, indent=4)

