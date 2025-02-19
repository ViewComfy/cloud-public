# Hunyuan Video ViewComfy API Call Example

## Adapting the example to your project

This example uses the ViewComfy API with a simple next.js server to create videos using Hunyuan with custom Loras to make videos with ComfyUI, you can find more details in this [Guide](https://www.viewcomfy.com/blog/using-custom-loras-to-make-videos-with-comfyui "using-custom-loras-to-make-videos-with-comfyui") 

### TypeScript functions

The file you need to pay attention is: 
- main.ts

The main.ts is where the ViewComfy url and parameters are set so send them to the API and returns the results as Blobs. 

### Preparing your API

To adapt this example to your project, you will need to do the following:
1. Create a ViewComfy.json using our open-source [repo](https://github.com/ViewComfy/ViewComfy). The parameters that you decide to expose in the UI are the ones that will be exposed to the API. For more details, you can refer to [this](https://youtu.be/sG2elA1bdrg) video.
2. Include the newly created viewcomfy.json file when deploying your workflow on [viewcomfy cloud](https://app.viewcomfy.com/ ""). For more details, you can refer to [this](https://youtu.be/pIODXFU9sHw) video.
3. Lastly, you will need to edit the parameters in main.ts to match the ones in your viewcomfy.json file. 

### Updating the parameters in the code to call your API

In the example, the parameters are:
```
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

```

The "key" for each parameter can be found inside the viewcomfy.json and will look like this:
``` 
"inputs": [
          {
            "title": "HunyuanVideo Sampler",
            "inputs": [
              {
                "title": "Width",
                ...
                "key": "3-inputs-width"
              }
              {
                "title": "Height",
                ...
                "key": "3-inputs-height"
              }
            ],
          ...
          },
          ...
]
```

## Running the example 


### Install dependencies to run the project

```
npm install
```

### Run the project

Change the viewComfyUrl value to the ViewComfy endpoint from the [ViewComfy Dashboard](https://app.viewcomfy.com)
viewComfyUrl value is inside `main.ts` file also you can change the parameters of the workflow

and to make the API call run:

```
npm run dev
```

the result will be something like this:



![Hunyuan Video characters result](https://raw.githubusercontent.com/ViewComfy/cloud-public/main/workflows/hunyuan-video/hunyuan_video_cover_video.mp4 "Hunyuan Video result")
