import { promises as fs } from "fs";
import * as path from "path";
import { infer, inferWithLogsStream } from "./api";
import { workflowApiParametersCreator } from "./workflow_api_parameters_creator";

const viewComfyUrl = "";

// Move your main function logic into a route handler
const generate = async () => {
    try {
        const params = {};

        const clientId = ""
        const clientSecret = ""

        const poseSheet = await loadImageFile("pose_sheet.png");
        params["625-inputs-image"] = poseSheet;

        const character = await loadImageFile("character.png");
        params["626-inputs-image"] = character;

        const characterPrompt =
            "a attractive woman, dark long hair, a women wearing a grey wool turtleneck sweater, brown eyes, jeans, brown boots, short medium long hair, chin long hair that looks like she just got up, She has a fair complexion, expressive brown eyes, Her makeup is natural, highlighting her soft features. she has slightly pink cheeks and a healthy skin tone";
        params["594-inputs-string"] = characterPrompt;

        params["82-inputs-upscale_by"] = 2;
        params["426-inputs-string"] =
            "a deep forest with oaks and pine trees ferns and bushes, national park, close up, overcast, close up, amateur photography, shot on iphone, candid photo";
        params["436-inputs-string"] =
            "a modern city during sunset, the sky is adorned by epic cloud formations, frontal close up, walking through the city, hard sunlight on face, Side lit, candid photography, dslr, evening, silhouette, moody, autumn, warm orange atmosphere, natural smile, amateur photography, shot on iphone, candid photo,  winking with one eye closed";
        params["443-inputs-string"] =
            "music video, color gel lighting, dark background, fog, colorful lighting, looking away from camera, stage lighting, concert stage, neon colors, silhouette, darkness, moody, amateur photography, shot on iphone, candid photo";
        params["458-inputs-string"] =
            "a vast desert landscape with distant mountains, the hard sunlight is illuminating the person from the side and casting shadows on to the white sand, blue sky, shadows, waving, close up, candid photography, shocked expression, side lit face, shocked expression with an open mouth, surprised face, amateur photography, shot on iphone, candid photo";
        params["499-inputs-noise_seed"] = 384340151733840;
        params["594-inputs-string"] =
            "a attractive woman, dark long hair, a women wearing a grey wool turtleneck sweater, brown eyes, jeans, brown boots, short medium long hair, chin long hair that looks like she just got up, She has a fair complexion, expressive brown eyes, Her makeup is natural, highlighting her soft features. she has slightly pink cheeks and a healthy skin tone";
        params["608-inputs-string"] =
            "it is a masterpiece, amateur photography, shot on iphone";

        // Call the API and wait for the results
        // const result = await infer({
        //     apiUrl: viewComfyUrl,
        //     params,
        //     clientId,
        //     clientSecret,
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
