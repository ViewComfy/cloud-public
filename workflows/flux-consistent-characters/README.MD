# Flux Consistent Characters ViewComfy API Call Example

## Adapting the example to your project

This example uses the ViewComfy API to run Consistent AI Characters using Flux in ComfyUI,
you can find more details in this [Guide](https://www.viewcomfy.com/blog/consistent-ai-characters-with-flux-and-comfyui "Consistent AI Characters using Flux in ComfyUI")

## API

The API example comes in two flavours python and TypeScript, everything that you need to run any kind of workflow
is abstracted in the api file (api.ts, api.py).

#### The API has two endpoints:

-   infer: classic request response where you wait with your request until the infer finish and you get the result back
-   infer with logs: this endpoint will send real-time updates of the logs of the ComfyUI execution, to make use of this you need to pass
    a function that will be called each time a log message is sent.

#### When the infer job finish the result class will be this:

```
PromptResult:
  prompt_id (str): Unique identifier for the prompt
  status (str): Current status of the prompt execution
  completed (bool): Whether the prompt execution is complete
  execution_time_seconds (float): Time taken to execute the prompt
  prompt (Dict): The original prompt configuration
  outputs (List[Dict], optional): List of output file data. Defaults to empty list.
```

### Get your API parameters

To get the parameter of your workflow_api.json you can run the workflow_api_parameter_creator function, this will create the dictionary of the workflow_api.json as a dictionary of parameters

for python:

```python
  python workflow_parameters_maker.py
```

for typescript: comment the generation function and uncomment the getWorkflowParametersForApi

```typescript
//generate().catch(console.error);
getWorkflowParametersForApi().catch(console.error);
```

### Updating the parameters in the code to call your API

In the example, the parameters are:

```
     const params = {};

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

```

The "key" for each parameter can be found inside the workflow_api_parameters.json and will look like this:

```
  "_626-node-class_type-info": "Character",
  "626-inputs-image": "",

  "_594-node-class_type-info": "CHARACTER PROMPT",
  "594-inputs-string": "a attractive woman, dark long hair, a women weraing a grey wool turtleneck sweater, brown eyes, jeans, brown boots, short medium long hair, chin long hair that looks like she just got up, She has a fair complexion, expressive brown eyes, Her makeup is natural, highlighting her soft features. she has slightly pink cheeks and a healthy skin tone",

```

## Running the example

### TypeScript Install dependencies to run the project

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

### Python Install dependencies to run the project

```
pip install -r requirements.txt
```

### Run the project

Change the viewComfyUrl value to the ViewComfy endpoint from the [ViewComfy Dashboard](https://app.viewcomfy.com)
viewComfyUrl value is inside `main.py` file also you can change the parameters of the workflow
and to make the API call run:

```
python main.py
```

the result will be something like this:

![flux consistent characters result](https://raw.githubusercontent.com/ViewComfy/cloud-public/main/workflows/flux-consistent-characters/flux_consistent_characters_result.png "flux consistent characters result")
