# Style Transfer ViewComfy API Call Example

## Adapting the example to your project

This example uses the ViewComfy API with a simple next.js app to transfer a style from one input image to a second input image. 

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
```

The "key" for each parameter can be found inside the viewcomfy.json and will look like this:
``` 
"inputs": [
          {
            "title": "CLIP Text Encode (Prompt)",
            "inputs": [
              {
                "title": "CLIP Text Encode (Prompt)",
                ...
                "key": "6-inputs-text"
              }
            ],
            "key": "6-CLIPTextEncode"
          },
          {
            "title": "Composition image",
            "inputs": [
              {
                ...
                "key": "12-inputs-image"
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

### Inputs

<img src="https://raw.githubusercontent.com/ViewComfy/cloud-public/main/workflows/style-transfer/composition_image.jpg" alt="composition image" width=50% height=50%>
<img src="https://raw.githubusercontent.com/ViewComfy/cloud-public/main/workflows/style-transfer/style.png" alt="style" width=50% height=50%>

### Output

![style transfer result](https://raw.githubusercontent.com/ViewComfy/cloud-public/main/workflows/style-transfer/style_transfer_result.png "style transfer")
