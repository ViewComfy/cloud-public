from typing import Dict, Any


def workflow_api_parameters_creator(workflow: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Flattens the workflow API JSON structure into a simple key-value object
    
    Args:
        workflow: The workflow API JSON object
    
    Returns:
        A flattened object with keys in the format "nodeId-inputs-paramName" or "nodeId-class_type-info"
    """
    flattened: Dict[str, Any] = {}
    
    # Iterate through each node in the workflow
    for node_id, node in workflow.items():
        # Add the class_type-info key, preferring _meta.title if available
        class_type_info = node.get("_meta", {}).get("title") or node.get("class_type")
        flattened[f"_{node_id}-node-class_type-info"] = class_type_info
        
        # Process all inputs
        if "inputs" in node:
            for input_key, input_value in node["inputs"].items():
                flattened[f"{node_id}-inputs-{input_key}"] = input_value
    
    return flattened


"""
Example usage:

import json

with open('workflow_api.json', 'r') as f:
    workflow_json = json.load(f)
    
flattened = create_workflow_api_parameters(workflow_json)
print(flattened)
"""
