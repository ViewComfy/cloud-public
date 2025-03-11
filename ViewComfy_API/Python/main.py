import asyncio
import base64
import json
import os
from api import infer, infer_with_logs

async def api_examples():

    view_comfy_api_url = "<Your_ViewComfy_endpoint>"
    output_directory = "output"
    override_workflow_api_path = None # Advanced feature: overwrite default workflow with a new one

    # Set parameters
    params = {}

    params["6-inputs-text"] = "A cat sorcerer"
    params["52-inputs-image"] = open("input_folder/input_img.png", "rb")


    if  override_workflow_api_path:  
        with open(override_workflow_api_path, "r") as f:
            override_workflow_api = json.load(f)
    else:
        override_workflow_api = None

    # Call the API and wait for the results
    # prompt_result = await infer(api_url=view_comfy_api_url, params=params, override_workflow_api=override_workflow_api)

    
    def logging_callback(log_message: str):
        """
        Handle logging of messages from ComfyUI. Only required for streaming responses.

        Args:
            log_message (str): The message to log
        """
        print(log_message)
    # Call the API and get the logs of the execution in real time
    # the console.log is the function that will be use to log the messages
    # you can use this function to build logics using the ComfyUI logs
    prompt_result = await infer_with_logs(
        api_url=view_comfy_api_url,
        params=params,
        logging_callback=logging_callback,
        override_workflow_api=override_workflow_api
    )
    for file in prompt_result.outputs:
        try:
            # Decode the base64 data before writing to file
            binary_data = base64.b64decode(file.data)
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            with open(f"{output_directory}/{file.filename}", "wb") as f:
                f.write(binary_data)
            print(f"Successfully saved {file.filename}")
        except Exception as e:
            print(f"Error saving {file.filename}: {str(e)}")


if __name__ == "__main__":
    asyncio.run(api_examples())
