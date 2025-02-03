import { promises as fs } from "fs";
import { doPost } from "./style_transfer_api";
import * as path from "path";

async function loadImageFile(filepath: string): Promise<File> {
  const buffer = await fs.readFile(filepath);
  return new File([buffer], path.basename(filepath), { type: "image/png" });
}

async function saveBlob(blob: Blob, filename: string): Promise<void> {
  const arrayBuffer = await blob.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);
  await fs.writeFile(filename, buffer);
}

interface IViewComfy {
  inputs: { key: string; value: string | File | number }[];
}

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

main().catch(console.error);
