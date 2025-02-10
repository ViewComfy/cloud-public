import { IViewComfy, ResponseError } from "./interfaces";
import { promises as fs } from "fs";
import * as path from "path";

const viewComfyUrl =
    "";

async function main() {
    const viewComfy: IViewComfy = {
        inputs: [],
    };

    // Required parameters
    const videoPrompt =
        "A scene from a Studio Ghibli animated film, featuring a playful girl with wavy red hair, green eyes, and a sunhat, as she runs through a meadow of wildflowers under a clear blue sky, with petals floating in the air, while the camera follows her joyfully, emphasizing the lively and carefree ambiance.";

    viewComfy.inputs.push({ key: "30-inputs-prompt", value: videoPrompt });

    const lora = "fluidart-v1_hunyuanvideo_e28.safetensors";
    viewComfy.inputs.push({ key: "42-inputs-lora", value: lora });

    viewComfy.inputs.push({ key: "42-inputs-strength", value: 1 });

    // Advanced parameters
    const advancedInputs = [
        { key: "3-inputs-width", value: 512 },
        { key: "3-inputs-height", value: 320 },
        { key: "3-inputs-num_frames", value: 41 },
        { key: "3-inputs-steps", value: 30 },
        { key: "3-inputs-embedded_guidance_scale", value: 6 },
        { key: "3-inputs-flow_shift", value: 9 },
        { key: "3-inputs-seed", value: 967396776895755 },
        { key: "34-inputs-frame_rate", value: 16 },
        { key: "34-inputs-loop_count", value: 0 },
        { key: "34-inputs-filename_prefix", value: "1176" },
        { key: "34-inputs-format", value: "video/h264-mp4" },
        { key: "34-inputs-pix_fmt", value: "yuv420p" },
        { key: "34-inputs-crf", value: 19 },
        { key: "34-inputs-save_metadata", value: true },
        { key: "34-inputs-trim_to_audio", value: false },
        { key: "34-inputs-pingpong", value: false },
        { key: "34-inputs-save_output", value: true },
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
                await saveBlob(blob, `output_${i + 1}.mp4`);
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
        formData.append("workflow", JSON.stringify(workflow));
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

const workflow = {
    "1": {
        inputs: {
            model: "hunyuan_video_720_fp8_e4m3fn.safetensors",
            base_precision: "bf16",
            quantization: "fp8_e4m3fn",
            load_device: "offload_device",
            attention_mode: "comfy",
            auto_cpu_offload: false,
            upcast_rope: true,
            lora: ["42", 0],
        },
        class_type: "HyVideoModelLoader",
        _meta: { title: "HunyuanVideo Model Loader" },
    },
    "3": {
        inputs: {
            width: 512,
            height: 320,
            num_frames: 41,
            steps: 30,
            embedded_guidance_scale: 6,
            flow_shift: 9,
            seed: 92504811584026,
            force_offload: 1,
            denoise_strength: 1,
            scheduler: "FlowMatchDiscreteScheduler",
            model: ["1", 0],
            hyvid_embeds: ["30", 0],
        },
        class_type: "HyVideoSampler",
        _meta: { title: "HunyuanVideo Sampler" },
    },
    "5": {
        inputs: {
            enable_vae_tiling: true,
            temporal_tiling_sample_size: 8,
            spatial_tile_sample_min_size: 256,
            auto_tile_size: true,
            vae: ["7", 0],
            samples: ["3", 0],
        },
        class_type: "HyVideoDecode",
        _meta: { title: "HunyuanVideo Decode" },
    },
    "7": {
        inputs: {
            model_name: "hunyuan_video_vae_bf16.safetensors",
            precision: "fp16",
        },
        class_type: "HyVideoVAELoader",
        _meta: { title: "HunyuanVideo VAE Loader" },
    },
    "16": {
        inputs: {
            llm_model: "Kijai/llava-llama-3-8b-text-encoder-tokenizer",
            clip_model: "openai/clip-vit-large-patch14",
            precision: "fp16",
            apply_final_norm: false,
            hidden_state_skip_layer: 2,
            quantization: "disabled",
            load_device: "offload_device",
        },
        class_type: "DownloadAndLoadHyVideoTextEncoder",
        _meta: { title: "(Down)Load HunyuanVideo TextEncoder" },
    },
    "30": {
        inputs: {
            prompt: "A scene from a Studio Ghibli animated film, featuring a playful girl with wavy red hair, green eyes, and a sunhat, as she runs through a meadow of wildflowers under a clear blue sky, with petals floating in the air, while the camera follows her joyfully, emphasizing the lively and carefree ambiance.",
            force_offload: "bad quality video",
            prompt_template: "video",
            text_encoders: ["16", 0],
        },
        class_type: "HyVideoTextEncode",
        _meta: { title: "HunyuanVideo TextEncode" },
    },
    "34": {
        inputs: {
            frame_rate: 16,
            loop_count: 0,
            filename_prefix: "1176",
            format: "video/h264-mp4",
            pix_fmt: "yuv420p",
            crf: 19,
            save_metadata: true,
            trim_to_audio: false,
            pingpong: false,
            save_output: true,
            images: ["5", 0],
        },
        class_type: "VHS_VideoCombine",
        _meta: { title: "Video Combine 🎥🅥🅗🅢" },
    },
    "42": {
        inputs: {
            lora: "fluidart-v1_hunyuanvideo_e28.safetensors",
            strength: 1,
        },
        class_type: "HyVideoLoraSelect",
        _meta: { title: "HunyuanVideo Lora Select" },
    },
};
