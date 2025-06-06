
# Flux Consistent Characters ViewComfy API Call Example

This example uses the ViewComfy API to run our Consistent AI Characters workflow template.

You can find more details on the specifics of the workflow in [here](https://www.viewcomfy.com/blog/consistent-ai-characters-with-flux-and-comfyui  "Consistent AI Characters using Flux in ComfyUI").

  

For a full guide on how to deploy a ComfyUI workflow and use the API, you can refer to [this](https://medium.com/@guillaume.bieler/integrate-comfyui-workflows-into-your-apps-a-guide-to-the-viewcomfy-api-981319b16c66) article.

## API

We have two API examples, one in Python and one TypeScript. All the functions to call the API and handle the responses are in the api files (api.ts and api.py). The main files (main.ts and main.py) take in the parameters that are specific to your workflow and in most cases will be the only files you need to edit.

  

#### The API file has two endpoints:

- infer: classic request-response endpoint where you wait for your request to finish before getting results back. 

- infer_with_logs: receives real-time updates with the ComfyUI logs (eg. progress bar). To make use of this endpoint, you need to pass a function that will be called each time a log message is received.

The endpoints can also take a workflow_api.json as a parameter. This is useful if you want to run a different workflow than the one you used when deploying. For an example of how to use it, you can refer to the [Advanced Usage](#advanced-usage) section.

  
#### The resutls are stored inside a class with this format (for the full definition refer to the api files):

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

To extract all the parameters from your workflow_api.json, you can run the workflow_api_parameter_creator function. This will create a dictionary with all of the parameters inside the workflow.

for python:

  

```python

python workflow_parameters_maker.py

```
for typescript: comment the generation function and uncomment the getWorkflowParametersForApi

  

```typescript

//generate().catch(console.error);

getWorkflowParametersForApi().catch(console.error);

```

  

### Updating the parameters to call your API

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

"a modern city during sunset, the sky is adorned by epic cloud formations, frontal close up, walking through the city, hard sunlight on face, Side lit, candid photography, dslr, evening, silhouette, moody, autumn, warm orange atmosphere, natural smile, amateur photography, shot on iphone, candid photo, winking with one eye closed";

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

  

Add your endpoint and set your API keys:

Change the view_comfy_api_url value inside main.ts to the ViewComfy endpoint from your ViewComfy Dashboard. Do the same with the "client_id" and "client_secret" values using your API keys (you can also get them from your dashboard). If you want, you can change the parameters of the workflow inside main.py at the same time.

  

Call the API:

  

```

npm run dev

```

  

### Python example

  

Install the dependencies:

  

```

pip install -r requirements.txt

```

  

Add your endpoint and set your API keys:

Change the view_comfy_api_url value inside main.py to the ViewComfy endpoint from your ViewComfy Dashboard. Do the same with the "client_id" and "client_secret" values using your API keys (you can also get them from your dashboard). If you want, you can change the parameters of the workflow inside main.py at the same time.

  

Call the API:

  

```

python main.py

```

  

the result will be something like this:

  

![flux consistent characters result](https://raw.githubusercontent.com/ViewComfy/cloud-public/main/workflows/flux-consistent-characters/flux_consistent_characters_result.png  "flux consistent characters result")

  

<a  id="advanced-usage"></a>

  

### Advanced Usage

  

You can overwrite the default workflow_api.json when sending a request. Be careful if you need to install new node packs to run the new workflow. Having too many custom_node packages can create some dependency issues between the Python packages. This can increase ComfyUI start-up time and, in some cases, break the ComfyUI installation.

To use an updated workflow (that works with your deployment) with the API, you can send the new workflow_api.json as a parameter. For example, using python:

```python

override_workflow_api = None

with  open("workflow_api_default.json", "rb") as f:

override_workflow_api = json.load(f)

prompt_result = await  infer(api_url=view_comfy_api_url, params=params, override_workflow_api=override_workflow_api)

```
