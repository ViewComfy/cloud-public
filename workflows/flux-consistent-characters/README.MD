# Flux Consistent Characters ViewComfy API Call Example

## Adapting the example to your project

This example uses the ViewComfy API with a simple next.js app to transfer a style from one input image to a second input image. 

### TypeScript functions

The two files you need to pay attention to are: 
- flux_consistent_characters_api.ts
- flux_consistent_characters_call.ts

The flux_consistent_characters_api file defines all the functions that you will need to run the API and shouldn't need to be changed. 

The flux_consistent_characters_call file takes in the parameters from the UI, sends them to the API and returns the results as Blobs. 

### Preparing your API

To adapt this example to your project, you will need to do the following:
1. Create a ViewComfy.json using our open-source [repo](https://github.com/ViewComfy/ViewComfy). The parameters that you decide to expose in the UI are the ones that will be exposed to the API. For more details, you can refer to [this](https://youtu.be/sG2elA1bdrg) video.
2. Include the newly created viewcomfy.json file when deploying your workflow on [viewcomfy cloud](https://app.viewcomfy.com/ ""). For more details, you can refer to [this](https://youtu.be/pIODXFU9sHw) video.
3. Lastly, you will need to edit the parameters in flux_consistent_characters_call.ts to match the ones in your viewcomfy.json file. 

### Updating the parameters in the code to call your API

In the example, the parameters are:
```
const poseSheet = await loadImageFile("pose_sheet.png");
  viewComfy.inputs.push({ key: "625-inputs-image", value: poseSheet });

  const character = await loadImageFile("character.png");
  viewComfy.inputs.push({ key: "626-inputs-image", value: character });

  const characterPrompt =
    "an attractive woman, dark long hair, a woman wearing a grey wool turtleneck sweater, brown eyes, jeans, brown boots, short medium long hair, chin long hair that looks like she just got up, She has a fair complexion, expressive brown eyes, Her makeup is natural, highlighting her soft features. she has slightly pink cheeks and a healthy skin tone";

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

```

The "key" for each parameter can be found inside the viewcomfy.json and will look like this:
``` 
"inputs": [
          {
            "title": "CHARACTER PROMPT",
            "inputs": [
              {
                "title": "String",
                ...
                "key": "594-inputs-string"
              }
            ],
            "key": "594-String Literal"
          },
          {
            "title": "Character",
            "inputs": [
              {
                "title": "Character",
                ...
                "key": "626-inputs-image"
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

Change the viewComfyUrl value to the ViewComfy endpoint from the app.viewcomfy.com
viewComfyUrl value is inside `flux_consistent_characters_api.ts` file

In the `flux_consistent_characters_call.ts` file, you can change the parameters of the workflow

and to make the API call run:

```
npm run dev
```

the result will be something like this:

![flux consistent characters result](https://raw.githubusercontent.com/ViewComfy/cloud-public/main/workflows/flux-consistent-characters/flux_consistent_characters_result.png "flux consistent characters result")
