import { promises as fs } from "fs";
import * as path from "path";
import { infer, inferWithLogsStream } from "../../workflows/flux-consistent-characters/node-typescript/api";
import { workflowApiParametersCreator } from "../../workflows/flux-consistent-characters/node-typescript/workflow_api_parameters_creator";

const viewComfyUrl = "<ViewComfy api url>";

// Move your main function logic into a route handler
const generate = async () => {
    try {
        const params = {};

        params["6-inputs-text"] = "A cat sorcerer"

        const inputImage = await loadImageFile("<path to image>");
        params["52-inputs-image"] = inputImage;

        params["3-inputs-steps"] = 1

        // Call the API and wait for the results
        // const result = await infer({
        //     apiUrl: viewComfyUrl,
        //     params,
        // });

        // Call the API and get the logs of the execution in real time
        // the console.log is the function that will be use to log the messages
        // you can use any function that you want
        const result = await inferWithLogsStream({
            apiUrl: viewComfyUrl,
            params,
            loggingCallback: console.log,
        });

        const urls = [];
        if (result) {
            for (const file of result.outputs) {
                await saveBlob(file, file.name);
            }
        }

        return { success: true, urls };
    } catch (error: any) {
        console.error("Error:", error);
    }
};

async function loadImageFile(filepath: string): Promise<File> {
    const buffer = await fs.readFile(filepath);
    return new File([buffer], path.basename(filepath), { type: "image/png" });
}

async function saveBlob(blob: Blob, filename: string): Promise<void> {
    const arrayBuffer = await blob.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    await fs.writeFile(filename, buffer);
}

async function getWorkflowParametersForApi(workflowPath: string) {
    // Example usage with a workflow file
    const workflowJson = JSON.parse(await fs.readFile(workflowPath, "utf-8"));
    const flattened = workflowApiParametersCreator(workflowJson);

    await fs.writeFile(
        "workflow_api_parameters.json",
        JSON.stringify(flattened, null, 2)
    );
}

generate().catch(console.error);
// const workflowPath = "/home/gbieler/GitHub/cloud-public/workflow_api.json";
// getWorkflowParametersForApi(workflowPath).catch(console.error);
