import asyncio
import base64
import json
import os
from api import infer, infer_with_logs

async def api_examples():

    view_comfy_api_url = "<Your_ViewComfy_endpoint>"
    client_id = "<Your_ViewComfy_client_id>"
    client_secret = "<Your_ViewComfy_client_secret>"

    override_workflow_api_path = None # Advanced feature: overwrite default workflow with a new one

    # Set parameters
    params = {}

    params["6-inputs-text"] = "A cat sorcerer"
    params["52-inputs-image"] = open("input_folder/input_img.png", "rb")

    override_workflow_api = None
    if  override_workflow_api_path:
        if os.path.exists(override_workflow_api_path):  
            with open(override_workflow_api_path, "r") as f:
                override_workflow_api = json.load(f)
        else:
            print(f"Error: {override_workflow_api_path} does not exist")

    def logging_callback(log_message: str):
        print(log_message)

    # Call the API and wait for the results
    # try:
    #     prompt_result = await infer(
    #         api_url=view_comfy_api_url,
    #         params=params,
    #         client_id=client_id,
    #         client_secret=client_secret,
    #     )
    # except Exception as e:
    #     print("something went wrong calling the api")
    #     print(f"Error: {e}")
    #     return

    # Call the API and get the logs of the execution in real time
    # the console.log is the function that will be use to log the messages
    # you can use any function that you want
    try:
        prompt_result = await infer_with_logs(
            api_url=view_comfy_api_url,
            params=params,
            logging_callback=logging_callback,
            client_id=client_id,
            client_secret=client_secret,
            override_workflow_api=override_workflow_api,
        )
    except Exception as e:
        print("something went wrong calling the api")
        print(f"Error: {e}")
        return

    if not prompt_result:
        print("No prompt_result generated")
        return

    for file in prompt_result.outputs:
        try:
            # Decode the base64 data before writing to file
            binary_data = base64.b64decode(file.data)
            with open(file.filename, "wb") as f:
                f.write(binary_data)
            print(f"Successfully saved {file.filename}")
        except Exception as e:
            print(f"Error saving {file.filename}: {str(e)}")


if __name__ == "__main__":
    asyncio.run(api_examples())
