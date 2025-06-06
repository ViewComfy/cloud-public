import { promises as fs } from "fs";
import * as path from "path";
import { infer, inferWithLogsStream } from "../../workflows/flux-consistent-characters/node-typescript/api";
import { workflowApiParametersCreator } from "../../workflows/flux-consistent-characters/node-typescript/workflow_api_parameters_creator";

const viewComfyUrl = "<ViewComfy api url>";
const clientId = "<ViewComfy client id>";
const clientSecret = "<ViewComfy client secret>";

// Move your main function logic into a route handler
const generate = async () => {
    try {
        const override_workflow_api_path = null;

        const params = {};

        params["6-inputs-text"] = "A cat sorcerer"

        const inputImage = await loadImageFile("<path to image>");
        params["52-inputs-image"] = inputImage;

        params["3-inputs-steps"] = 1


        let override_workflow_api = null;
        if (override_workflow_api_path) {
            try {
                const fileContent = await fs.readFile(override_workflow_api_path, "utf-8");
                override_workflow_api = JSON.parse(fileContent);
            } catch (error) {
                console.error("Override workflow API path does not exist");
            }
        }

        // Call the API and wait for the results
        // const result = await infer({
        //     apiUrl: viewComfyUrl,
        //     params,
        //     clientId,
        //     clientSecret,
        //     override_workflow_api: override_workflow_api
        // });

        // Call the API and get the logs of the execution in real time
        // the console.log is the function that will be use to log the messages
        // you can use any function that you want
        const result = await inferWithLogsStream({
            apiUrl: viewComfyUrl,
            params,
            loggingCallback: console.log,
            clientId,
            clientSecret,
            override_workflow_api: override_workflow_api
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

async function getWorkflowParametersForApi() {
    // Example usage with a workflow file
    const workflowPath = "workflow_api.json";
    const workflowJson = JSON.parse(await fs.readFile(workflowPath, "utf-8"));
    const flattened = workflowApiParametersCreator(workflowJson);

    await fs.writeFile(
        "workflow_api_parameters.json",
        JSON.stringify(flattened, null, 2)
    );
}

generate().catch(console.error);
// getWorkflowParametersForApi().catch(console.error);