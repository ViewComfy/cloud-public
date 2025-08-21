import asyncio
import json
import os

import aiofiles
import httpx
from api import infer


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
    params["52-inputs-image"] = await aiofiles.open("input_folder/input_img.png", "rb")

    override_workflow_api = None
    if override_workflow_api_path:
        if os.path.exists(override_workflow_api_path):
            with open(override_workflow_api_path) as f:
                override_workflow_api = json.load(f)
        else:
            print(f"Error: {override_workflow_api_path} does not exist")

    # Call the API and get the logs of the execution in real time

    try:
        prompt_result = await infer(
            view_comfy_api_url=view_comfy_api_url,
            params=params,
            client_id=client_id,
            client_secret=client_secret,
            override_workflow_api=override_workflow_api,
        )
    except Exception as e:
        msg = f"something went wrong calling the api, Error: {e}"
        print(msg)
        raise

    if not prompt_result:
        message = "No prompt_result generated"
        print(message)
        raise Exception(message)

    for file in prompt_result.outputs:
        try:
            print(f"Downloading file from {file.filepath}")  # noqa: T201
            async with httpx.AsyncClient() as client:
                response = await client.get(file.filepath)
                response.raise_for_status()  # raise exception for bad status codes
                async with aiofiles.open(file.filename, "wb") as f:
                    await f.write(response.content)
            print(f"Successfully saved {file.filename}")  # noqa: T201
        except Exception as e:
            print(f"Error downloading {file.filename} from S3: {e!s}")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(api_examples())
