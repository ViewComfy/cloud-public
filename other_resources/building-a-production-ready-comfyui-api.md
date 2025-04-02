---
title: "Building a Production-Ready ComfyUI API: A Complete Guide"
excerpt: "Full guide on how to turn a ComfyUI workflow into a production-ready API, including the best hosting options. "
coverImage: "/assets/blog/build_comfyui_api/build a production ready ComfyUI API.webp"
date: "2025-01-23T05:35:07.322Z"
ogImage:
  url: "/assets/blog/build_comfyui_api/build a production ready ComfyUI API.webp"
---


ComfyUI has emerged as a powerful tool for AI image and video generation. Not only is it a great way to develop and visualise workflow, but it also offers an intuitive interface to develop complex APIs, making it a great tool to speed the development of AI tools. In this guide, we’ll show you how to transform ComfyUI from a visual workflow tool into a production-ready API service that can power your applications at scale.

Because advanced ComfyUI workflow sometimes takes multiple minutes to complete, we use a WebSocket-based API in this guide. The main advantage over a REST API is that it allows for real-time progress updates.

_Note that this is a guide to the ComfyUI API which requires self hosting. If you are looking for a full end-to-end solution, including hosting, we recommend checking out_ [_this_](https://medium.com/@guillaume.bieler/integrate-comfyui-workflows-into-your-apps-a-guide-to-the-viewcomfy-api-981319b16c66) _guide instead._

# **ComfyUI’s Built-in Endpoints**

ComfyUI provides five key endpoints that form the foundation of any APIs:

/ws  
"""WebSocket endpoint for real-time status updates and executing messages"""  
  
/prompt  
"""Queues workflows for execution, returns prompt_id or error"""  
  
/history/{prompt_id}   
"""Retrieves results for a given prompt, returns queue or output"""  
  
/view   
"""return images given a filename, subfolder and type (input, output or temp)"""  
  
/upload/{image_type} # image type can be image or mask  
"""Handles image and mask uploads for workflows that take images as inputs"""

For the full list of ComfyUI endpoints, you can refer to the source code  [here](https://github.com/comfyanonymous/ComfyUI/blob/master/server.py).

# **Implementation**

Before you start, you will need the workflow_api.json file. You can download it from ComfyUI by following these steps:

-   Enable dev mode options in the ComfyUI settings
-   Export your API JSON using the “Save (API format)” button.

![](https://miro.medium.com/v2/resize:fit:700/1*IsDAN4WYVGDo7AEzC9lhwA.png)

This file is what you will need to update with your user’s input parameters and what ComfyUI calls the “prompt”.

1.  **Setting Up the WebSocket Connection**

Start by setting up a connection with the ComfyUI server.

def establish_connection():  
    server_address="127.0.0.1:8188"  
    client_id = str(uuid.uuid4())  
    ws = websocket.WebSocket()  
    ws.connect(f"ws://{server_address}/ws?clientId={client_id}")  
    return ws, server_address, client_id

**2. Core API Functions**

Working with the ComfyUI API boils down to using a few key functions: posting the generation request, getting the generation data back and using that information to get your results. If you plan to use images or videos as input, you will also need a function to send them to the server.

 def queue_prompt(prompt, client_id, server_address):  
    """  
    Queue a workflow for execution.   
    The prompt here is the full workflow_api.json file  
    """  
    data = {"prompt": prompt, "client_id": client_id}  
    headers = {"Content-Type": "application/json"}  
    response = requests.post(f"http://{server_address}/prompt", json=data, headers=headers)  
    return response.json()  
    
 def get_history(prompt_id, server_address):  
    """  
    Fetch the output data for a completed workflow,   
    returns a JSON with generation parameters and results   
    filenames and directories  
    """  
    response = requests.get(f"http://{server_address}/history/{prompt_id}")  
    return response.json()  
  
def get_image(filename, subfolder, folder_type, server_address):  
    """  
    Fetch results. Note that "save image" nodes will save images   
    in the ouptut folder and "preview image" nodes will save images   
    in the temp folder  
    """  
    params = {"filename": filename, "subfolder": subfolder, "type": folder_type}  
    response = requests.get(f"http://{server_address}/view", params=params)  
    return response.content  
  
def upload_image(input_path, filename, server_address, folder_type="input", image_type="image", overwrite=False):  
    """  
    Upload an image or a mask to the ComfyUI server.   
    input_path is the path to the image/mask to upload and   
    image_type is either image or mask  
    """  
    with open(input_path, 'rb') as file:  
        files = {  
            "image": (filename, file, 'image/png')  
        }  
        data = {  
            "type": folder_type,  
            "overwrite": str(overwrite).lower()  
        }  
        url = f"http://{server_address}/upload/{image_type}"  
        response = requests.post(url, files=files, data=data)  
        return response.content

**3. Updating the workflow with user inputs**

Before sending the workflow to the API, you can dynamically update the parameters. In this example, we update the positive prompt, randomise the seed and add an input image:

def update_workflow(prompt, input_path, positive_prompt):  
    id_to_class_type = {id: details["class_type"] for id, details in prompt.items()}  
    k_sampler = [key for key, value in id_to_class_type.items() if value == 'KSampler'][0]  
  
    """Set the seed to random"""  
    prompt.get(k_sampler)["inputs"]["seed"] = random.randint(10**14, 10**15 - 1)  
  
    """Update the positive prompt"""  
    text_prompt = prompt.get(k_sampler)["inputs"]["positive"][0]  
    prompt.get(text_prompt)["inputs"]["text"] = positive_prompt  
  
    """Update the path to the input image"""  
    image_loader = [key for key, value in id_to_class_type.items() if value == "LoadImage"][0]  
    filename = input_path.split("/")[-1]  
    prompt.get(image_loader)["inputs"]["image"] = filename  
  
    return prompt

**4. Progress Tracking**

And finally, to keep track of how your generation is going, we recommend setting up a tracking system like this one.

def track_progress(ws, prompt_id):  
    """Track the progress of image generation"""  
    while True:  
        try:  
            message = json.loads(ws.recv())  
            if message["type"] == "progress":  
                """  
                If the workflow is running,  
                print k-sampler current step over total steps  
                """  
                print(f"Progress: {message["data"]["value"]}/{message["data"]["max"]}")  
              
            elif message["type"] == "executing":  
                """Print the node that is currently being executed"""  
                print(f"Executing node: {message["data"]["node"]}")  
              
            elif message["type"] == "execution_cached":  
                """Print list of nodes that are cached"""  
                print(f"Cached execution: {message['data']}")  
              
            """Check for completion"""  
            if (message["type"] == "executed" and   
                "prompt_id" in message["data"] and   
                message["data"]["prompt_id"] == prompt_id):  
                print("Generation completed")  
                return True  
              
        except Exception as e:  
            print(f"Error processing message: {e}")  
            return False

# **Example: Complete Image Generation Service**

Here’s a complete example of what the full process can look like using the functions from the previous section:

def generate_image(generation_parameters):  
    ws, _, client_id = establish_connection()  
     
    try:  
        """Update the workflow with the generation parameters"""  
        workflow = load_workflow("workflow_api.json")  
        workflow = update_workflow(workflow,   
                                  input_path=generation_parameters["input_path"],  
                                  positive_prompt=generation_parameters["positive_prompt"]  
                                  )  
          
        """Upload the input image to the server"""  
        upload_image(input_path=generation_parameters["input_path"], filename="img.jpg", server_address=server_address)  
          
        """Send the workflow to the server"""  
        prompt_id = queue_prompt(workflow, client_id, server_address)  
        prompt_id = prompt_id["prompt_id"]  
  
        """Track the progress"""  
        completed = track_progress(ws, prompt_id)  
        if not completed:  
            print("Generation failed or interrupted")  
            return None  
  
        """Fetch the output data"""      
        history = get_history(prompt_id, server_address)  
        outputs = history[prompt_id]["outputs"]  
  
        """Get output images"""  
        for node_id in outputs:  
            node_output = outputs[node_id]  
            images_output = []  
            if "images" in node_output:  
                for image in node_output["images"]:  
                    image_data = get_image(image["filename"], image["subfolder"], image["type"], server_address)  
                    images_output.append(image_data)  
        return images_output  
         
    finally:  
        ws.close()

You can download the full implementation  [here](https://github.com/ViewComfy/cloud-public/blob/main/other_resources/ComfyUI_API_call_example.py).

# Deployment

Depending on what you are aiming for, there are a few deployment options. If you need a quick and easy way to deploy a ComfyUI workflow on scalable hardware of your choice, check out  [ViewComfy Cloud](https://app.viewcomfy.com/). This service allows you to skip most of the engineering steps. All you have to do is drop your workflow_api.json file, and the service will take care of installing the nodes, preparing the models, and setting up the infra.

# **Conclusion**

ComfyUI is a great way to design complex image and video generation APIs. When combined with WebSockets for real-time updates and dynamic workflow modification, it offers a powerful foundation for building scalable AI image and video generation services.

Have questions or want to share your implementation? Join the discussion on our  [discord](https://discord.gg/wBuDqGsv)  or reach out to the team team@viewcomfy.com.
