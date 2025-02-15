import { promises as fs } from "fs";
import * as path from "path";
import { ResponseError, IViewComfy } from "./interfaces";

const viewComfyUrl = "";

async function main() {
    const viewComfy: IViewComfy = {
        inputs: [],
    };

    // Required parameters
    const composition = await loadImageFile("composition_image.jpg");
    viewComfy.inputs.push({ key: "12-inputs-image", value: composition });

    const style = await loadImageFile("style.png");
    viewComfy.inputs.push({ key: "17-inputs-image", value: style });

    const prompt =
        "A mountain, high quality, highly detailed, high quality, highly detailed";

    viewComfy.inputs.push({ key: "6-inputs-text", value: prompt });

    // Advanced parameters
    const advancedInputs = [
        { key: "3-inputs-seed", value: 461631196608471 },
        { key: "3-inputs-steps", value: 30 },
        { key: "3-inputs-cfg", value: 6.5 },
        { key: "15-inputs-strength", value: 0.8 },
        { key: "31-inputs-strength", value: 0.6 },
    ];

    viewComfy.inputs.push(...advancedInputs);

    // Call the API
    try {
        const result = await doPost({ viewComfy });
        console.log("Processing completed:", result);

        // Save result blobs
        if (result && result.length > 0) {
            for (let i = 0; i < result.length; i++) {
                const blob = result[i];
                await saveBlob(blob, `output_${i + 1}.png`);
            }
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

export const doPost = async ({ viewComfy }: { viewComfy: IViewComfy }) => {
    if (!viewComfyUrl) {
        throw new Error("viewComfyUrl is not set");
    }

    const url = `${viewComfyUrl}/api/comfy`;

    try {
        const formData = new FormData();
        const viewComfyJSON: IViewComfy = {
            inputs: [],
        };
        for (const { key, value } of viewComfy.inputs) {
            if (value instanceof File) {
                formData.append(key, value);
            } else {
                viewComfyJSON.inputs.push({ key, value });
            }
        }

        formData.append("viewComfy", JSON.stringify(viewComfyJSON));
        const response = await fetch(url, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const responseError: ResponseError =
                (await response.json()) as ResponseError;
            throw responseError;
        }

        if (!response.body) {
            throw new Error("No response body");
        }

        const reader = response.body.getReader();
        let buffer = new Uint8Array(0);
        const output: Blob[] = [];
        const separator = new TextEncoder().encode("--BLOB_SEPARATOR--");

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer = concatUint8Arrays(buffer, value);

            let separatorIndex: number;

            while ((separatorIndex = findSubarray(buffer, separator)) !== -1) {
                const outputPart = buffer.slice(0, separatorIndex);
                buffer = buffer.slice(separatorIndex + separator.length);

                const mimeEndIndex = findSubarray(
                    outputPart,
                    new TextEncoder().encode("\r\n\r\n")
                );
                if (mimeEndIndex !== -1) {
                    const mimeType = new TextDecoder()
                        .decode(outputPart.slice(0, mimeEndIndex))
                        .split(": ")[1];
                    const outputData = outputPart.slice(mimeEndIndex + 4);
                    const blob = new Blob([outputData], { type: mimeType });
                    output.push(blob);
                }
            }
        }

        return output;
    } catch (error) {
        throw error;
    }
};

function concatUint8Arrays(a: Uint8Array, b: Uint8Array): Uint8Array {
    const c = new Uint8Array(a.length + b.length);
    c.set(a);
    c.set(b, a.length);
    return c;
}

function findSubarray(arr: Uint8Array, separator: Uint8Array): number {
    outer: for (let i = 0; i <= arr.length - separator.length; i++) {
        for (let j = 0; j < separator.length; j++) {
            if (arr[i + j] !== separator[j]) {
                continue outer;
            }
        }
        return i;
    }
    return -1;
}

async function loadImageFile(filepath: string): Promise<File> {
    const buffer = await fs.readFile(filepath);
    return new File([buffer], path.basename(filepath), { type: "image/png" });
}

async function saveBlob(blob: Blob, filename: string): Promise<void> {
    const arrayBuffer = await blob.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    await fs.writeFile(filename, buffer);
}

main().catch(console.error);
