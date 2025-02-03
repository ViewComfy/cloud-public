import { promises as fs } from "fs";
import { doPost } from "./flux_consistent_characters_api";
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
  const poseSheet = await loadImageFile("pose_sheet.png");
  viewComfy.inputs.push({ key: "625-inputs-image", value: poseSheet });

  const character = await loadImageFile("character.png");
  viewComfy.inputs.push({ key: "626-inputs-image", value: character });

  const characterPrompt =
    "a attractive woman, dark long hair, a women wearing a grey wool turtleneck sweater, brown eyes, jeans, brown boots, short medium long hair, chin long hair that looks like she just got up, She has a fair complexion, expressive brown eyes, Her makeup is natural, highlighting her soft features. she has slightly pink cheeks and a healthy skin tone";

  viewComfy.inputs.push({ key: "594-inputs-string", value: characterPrompt });

  // Advanced parameters
  const advancedInputs = [
    { key: "82-inputs-upscale_by", value: 2 },
    {
      key: "426-inputs-string",
      value:
        "a deep forest with oaks and pine trees ferns and bushes, national park, close up, overcast, close up, amateur photography, shot on iphone, candid photo",
    },
    {
      key: "436-inputs-string",
      value:
        "a modern city during sunset, the sky is adorned by epic cloud formations, frontal close up, walking through the city, hard sunlight on face, Side lit, candid photography, dslr, evening, silhouette, moody, autumn, warm orange atmosphere, natural smile, amateur photography, shot on iphone, candid photo,  winking with one eye closed",
    },
    {
      key: "443-inputs-string",
      value:
        "music video, color gel lighting, dark background, fog, colorful lighting, looking away from camera, stage lighting, concert stage, neon colors, silhouette, darkness, moody, amateur photography, shot on iphone, candid photo",
    },
    {
      key: "458-inputs-string",
      value:
        "a vast desert landscape with distant mountains, the hard sunlight is illuminating the person from the side and casting shadows on to the white sand, blue sky, shadows, waving, close up, candid photography, shocked expression, side lit face, shocked expression with an open mouth, surprised face, amateur photography, shot on iphone, candid photo",
    },
    { key: "499-inputs-noise_seed", value: 384340151733840 },
    {
      key: "594-inputs-string",
      value:
        "a attractive woman, dark long hair, a women wearing a grey wool turtleneck sweater, brown eyes, jeans, brown boots, short medium long hair, chin long hair that looks like she just got up, She has a fair complexion, expressive brown eyes, Her makeup is natural, highlighting her soft features. she has slightly pink cheeks and a healthy skin tone",
    },
    {
      key: "608-inputs-string",
      value: "it is a masterpiece, amateur photography, shot on iphone",
    },
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
