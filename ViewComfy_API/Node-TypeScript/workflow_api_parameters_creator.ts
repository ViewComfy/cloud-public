interface IWorkflowNode {
    inputs: Record<string, any>;
    class_type: string;
    _meta?: {
        title?: string;
    };
}

interface IWorkflowApi {
    [key: string]: IWorkflowNode;
}

/**
 * Flattens the workflow API JSON structure into a simple key-value object
 * @param workflow The workflow API JSON object
 * @returns A flattened object with keys in the format "nodeId-inputs-paramName" or "_nodeId-node-class_type-info"
 */
export function workflowApiParametersCreator(
    workflow: IWorkflowApi
): Record<string, any> {
    const flattened: Record<string, any> = {};

    // Iterate through each node in the workflow
    Object.entries(workflow).forEach(([nodeId, node]) => {
        // Add the class_type-info key, preferring _meta.title if available
        const classTypeInfo = node._meta?.title || node.class_type;
        flattened[`_${nodeId}-node-class_type-info`] = classTypeInfo;

        // Process all inputs
        if (node.inputs) {
            Object.entries(node.inputs).forEach(([inputKey, inputValue]) => {
                flattened[`${nodeId}-inputs-${inputKey}`] = inputValue;
            });
        }
    });

    return flattened;
}

/**
 * Example usage:
 *
 * import { readFileSync } from 'fs';
 *
 * const workflowJson = JSON.parse(readFileSync('workflow_api.json', 'utf-8'));
 * const flattened = flattenWorkflowApi(workflowJson);
 * console.log(flattened);
 */
