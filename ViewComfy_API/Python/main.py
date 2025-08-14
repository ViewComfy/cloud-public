import asyncio
import base64
import json
import os

import httpx
from api import FileOutput, S3FileOutput, infer_with_logs_ws


async def api_examples():
    view_comfy_api_url = "<Your_ViewComfy_endpoint>"
    client_id = "<Your_ViewComfy_client_id>"
    client_secret = "<Your_ViewComfy_client_secret>"

    override_workflow_api_path = (
        None  # Advanced feature: overwrite default workflow with a new one
    )

    # Set parameters
    params = {}

    params["6-inputs-text"] = "A cat sorcerer"
    params["52-inputs-image"] = open("input_folder/input_img.png", "rb")

    override_workflow_api = None
    if override_workflow_api_path:
        if os.path.exists(override_workflow_api_path):
            with open(override_workflow_api_path) as f:
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
    # Call the API and wait for the results
    try:
        prompt_result = await infer_with_logs_ws(
            view_comfy_api_url=view_comfy_api_url,
            params=params,
            client_id=client_id,
            client_secret=client_secret,
            override_workflow_api=override_workflow_api,
        )
    except Exception as e:
        print("something went wrong calling the api")
        print(f"Error: {e}")
        return

    if not prompt_result:
        message = "No prompt_result generated"
        print(message)
        raise Exception(message)

    for file in prompt_result.outputs:
        if isinstance(file, S3FileOutput):
            try:
                print(f"Downloading file from {file.filepath}")
                async with httpx.AsyncClient() as client:
                    response = await client.get(file.filepath)
                    response.raise_for_status()  # raise exception for bad status codes
                    with open(file.filename, "wb") as f:
                        f.write(response.content)
                print(f"Successfully saved {file.filename}")
            except Exception as e:
                print(f"Error downloading {file.filename} from S3: {e!s}")
        elif isinstance(file, FileOutput):
            try:
                # Decode the base64 data before writing to file
                print(file.content_type)
                print(file.size)
                print(file.filename)
                binary_data = base64.b64decode(file.data)
                with open(file.filename, "wb") as f:
                    f.write(binary_data)
                print(f"Successfully saved {file.filename}")
            except Exception as e:
                print(f"Error saving {file.filename}: {e!s}")


if __name__ == "__main__":
    asyncio.run(api_examples())
