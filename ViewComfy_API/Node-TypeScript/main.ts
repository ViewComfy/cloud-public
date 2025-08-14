import { promises as fs } from "fs";
import * as path from "path";
import { infer } from "../../workflows/flux-consistent-characters/node-typescript/api";
import { workflowApiParametersCreator } from "../../workflows/flux-consistent-characters/node-typescript/workflow_api_parameters_creator";
import { inferWithLogsWS, S3FilesData } from "./api";

const viewComfyUrl = "<ViewComfy api url>";
const clientId = "<ViewComfy client id>";
const clientSecret = "<ViewComfy client secret>";

// Move your main function logic into a route handler
const generate = async () => {
    try {
        const overrideWorkflowApiPath = null;

        const params = {};

        params["6-inputs-text"] = "A cat sorcerer"

        const inputImage = await loadImageFile("<path to image>");
        params["52-inputs-image"] = inputImage;

        params["3-inputs-steps"] = 1


        let overrideWorkflowApi = null;
        if (overrideWorkflowApiPath) {
            try {
                const fileContent = await fs.readFile(overrideWorkflowApiPath, "utf-8");
                overrideWorkflowApi = JSON.parse(fileContent);
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
        const result = await inferWithLogsWS({
            apiUrl: viewComfyUrl,
            params,
            clientId,
            clientSecret,
            overrideWorkflowApi
        });

        const urls = [];
        if (result) {
            for (const file of result.outputs) {
                if (file instanceof File) {
                    await saveBlob(file, file.name);
                } else {
                    const s3File = file as S3FilesData;
                    if (s3File.filepath) {
                        try {
                            const response = await fetch(s3File.filepath);
                            if (!response.ok) {
                                console.error(`Failed to download file: ${s3File.filepath}`);
                                continue;
                            }
                            const blob = await response.blob();
                            await saveBlob(blob, s3File.filename);
                            console.log(`Successfully downloaded and saved ${s3File.filename}`);
                        } catch (error) {
                            console.error(`Error downloading file ${s3File.filepath}:`, error);
                        }
                    }
                }
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