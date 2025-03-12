# Flux Consistent Characters ViewComfy API Call Example

## Adapting the example to your project

This example uses the ViewComfy API to run our Consistent AI Characters templates in ComfyUI.
You can find more details on the specifics of the workflow in this [here](https://www.viewcomfy.com/blog/consistent-ai-characters-with-flux-and-comfyui "Consistent AI Characters using Flux in ComfyUI").

For a full guide on how to deploy a ComfyUI workflow and use the API, you can refer to [this](https://medium.com/@guillaume.bieler/integrate-comfyui-workflows-into-your-apps-a-guide-to-the-viewcomfy-api-981319b16c66) article. 
   
## API

### The API

We have two API examples, in Python and TypeScript. You can adapt the code in the relevant API file (api.ts or api.py) to your workflow.

#### The API has two endpoints:

-   infer: classic request-response where you wait with your request until the infer finishes and you get the result back
-   infer with logs: this endpoint will send real-time updates of the logs of the ComfyUI execution, to make use of this, you need to pass
    a function that will be called each time a log message is sent.

The endpoints can also receive a workflow_api.json as a parameter. This is useful if you want to run a different workflow than the one you deployed with. For an example of how to use it, you can refer to the [Advanced Usage](#advanced-usage) section.

#### When the infer job finishes this will be the result class:

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

To extract all the parameters in your workflow_api.json, you can run the workflow_api_parameter_creator function. This will create a dictionary with all of the parameters inside the workflow.

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

### TypeScript example

Install the dependencies:

```
npm install
```

Add your endpoint:

Deploy the consistent character template and change the view_comfy_api_url value inside `main.ts` to the ViewComfy endpoint from your [ViewComfy Dashboard](https://app.viewcomfy.com). You can also change the parameters of the workflow inside `main.ts` if you want.

Call the API:

```
npm run dev
```

### Python example

Install the dependencies:

```
pip install -r requirements.txt
```

Add your endpoint:

Deploy the consistent character template and change the view_comfy_api_url value inside `main.py` to the ViewComfy endpoint from your [ViewComfy Dashboard](https://app.viewcomfy.com). You can also change the parameters of the workflow inside `main.py` if you want.

Call the API:

```
python main.py
```

the result will be something like this:

![flux consistent characters result](https://raw.githubusercontent.com/ViewComfy/cloud-public/main/workflows/flux-consistent-characters/flux_consistent_characters_result.png "flux consistent characters result")

<a id="advanced-usage"></a>

### Advanced Usage

You can overwrite the default workflow_api.json when sending a request. We recommend not to abuse this functionality, and have one deployment
per workflow. Having too many custom_node packages can create some dependency issues between the Python packages version for each node. This can make workflow breaks, and increase ComfyUI start up time.

To use an updated workflow (that works with your deployment) with your API, you can send the new workflow_api.json as a parameter. For example, using python: 

```python
    override_workflow_api = None
    with open("workflow_api_default.json", "rb") as f:
        override_workflow_api = json.load(f)

    prompt_result = await infer(api_url=view_comfy_api_url, params=params, override_workflow_api=override_workflow_api)

```
