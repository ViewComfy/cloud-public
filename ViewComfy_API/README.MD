# ViewComfy API Example

For a detailed guide on how to deploy a ComfyUI workflow and use the API, you can refer to [this](https://medium.com/@guillaume.bieler/integrate-comfyui-workflows-into-your-apps-a-guide-to-the-viewcomfy-api-981319b16c66) article.

## API

We have two API examples, one in Python and one TypeScript. All the functions to call the API and handle the responses are in the api files (api.ts and api.py). The main files (main.ts and main.py) take in the parameters that are specific to your workflow and in most cases will be the only files you need to edit.

#### The API file has two endpoints:

- infer: classic request-response endpoint where you wait for your request to finish before getting results back. 

- infer_with_logs: receives real-time updates with the ComfyUI logs (eg. progress bar). To make use of this endpoint, you need to pass a function that will be called each time a log message is received.

The endpoints can also take a workflow_api.json as a parameter. This is useful if you want to run a different workflow than the one you used when deploying. For an example of how to use this functionality, you can refer to the [Advanced Usage](#advanced-usage) section.

  
#### The results are stored inside a class with this format (for the full definition refer to the api files):

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

**For python**

  

```python

python workflow_parameters_maker.py --workflow_api_path "<Path to your workflow_api.json file>"

```
**For typescript** 


Comment the generation function inside main.ts and uncomment the getWorkflowParametersForApi.

```typescript
async function getWorkflowParametersForApi() {
   const workflowPath = "<path to your workflow_api.json file>";
   ...
}
// generate().catch(console.error);
getWorkflowParametersForApi().catch(console.error);

```

Then run the script:
```typescript
npm run dev
```
  

### Updating the parameters to call your API

In the Python example, the parameters are:
  

```
params = {}

params["6-inputs-text"] = "A cat sorcerer"
params["52-inputs-image"] = open("input_folder/input_img.png", "rb")

```

The "key" for each parameter can be found inside the workflow_api_parameters.json you create using workflow_parameters_maker.py. They will look like this:

```
{  
"_3-node-class_type-info": "KSampler",  
"3-inputs-cfg": 6,  
  
…  
  
"_6-node-class_type-info": "CLIP Text Encode (Positive Prompt)",  
"6-inputs-clip": [  
"38",  
0  
],  
"6-inputs-text": "A woman raising her head with hair blowing in the wind",  
  
…  
  
"_52-node-class_type-info": "Load Image",  
"52-inputs-image": "<path_to_my_image>",  
  
…  
}

```


## Running the example

 ### Python example

Install the dependencies:

```

pip install -r requirements.txt

```

Add your endpoint and set your API keys:

  

Change the view_comfy_api_url value inside `main.py` to the ViewComfy endpoint from your [ViewComfy Dashboard](https://app.viewcomfy.com). Do the same with the "client_id" and "client_secret" values using your API keys (you can also get them from your dashboard). If you want, you can change the parameters of the workflow inside `main.py` at the same time.

Call the API:

```

python main.py

```


### TypeScript example

Install the dependencies:

```

npm install

```

  

Add your endpoint and set your API keys:

  

Change the view_comfy_api_url value inside `main.ts` to the ViewComfy endpoint from your [ViewComfy Dashboard](https://app.viewcomfy.com). Do the same with the "client_id" and "client_secret" values using your API keys (you can also get them from your dashboard). If you want, you can change the parameters of the workflow inside `main.ts` at the same time.

  

Call the API:

  

```

npm run dev

```
  

<a  id="advanced-usage"></a>

### Advanced Usage

  

You can overwrite the default workflow_api.json when sending a request. Be careful if you need to install new node packs to run the new workflow. Having too many custom node packages can create some issues between the Python packages. This can increase ComfyUI start up time and in some cases break the ComfyUI installation.

To use an updated workflow (that works with your deployment) with the API, you can send the new workflow_api.json as a parameter by changing the override_workflow_api_path value. For example, using python:

```python

override_workflow_api_path = "<path_to_your_new_workflow_api_file>"

```
