import asyncio
import json
from pathlib import Path

import aiofiles
import httpx
from api import infer, infer_cancel

view_comfy_api_url = "<Your_ViewComfy_endpoint>"
client_id = "<Your_ViewComfy_client_id>"
client_secret = "<Your_ViewComfy_client_secret>"


async def api() -> None:
    # Advanced feature: overwrite default workflow with a new one:
    # https://github.com/ViewComfy/cloud-public/tree/main/ViewComfy_API#using-the-api-with-a-different-workflow
    override_workflow_api_path = None

    # Set parameters
    params = {}

    params["6-inputs-text"] = "A cat sorcerer"
    params["10-inputs-image"] = Path("input_folder/input_img.png").open("rb")

    override_workflow_api = None
    if override_workflow_api_path:
        if Path(override_workflow_api_path).exists():
            with open(override_workflow_api_path) as f:
                override_workflow_api = json.load(f)
        else:
            msg = f"Error: {override_workflow_api_path} does not exist"
            print(msg)
            raise Exception(msg)

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
            print(f"Downloading file from {file.filepath}")
            async with httpx.AsyncClient() as client:
                response = await client.get(file.filepath)
                response.raise_for_status()
                async with aiofiles.open(file.filename, "wb") as f:
                    await f.write(response.content)
            print(f"Successfully saved {file.filename}")
        except Exception as e:
            print(f"Error downloading {file.filename} from S3: {e!s}")


async def cancel() -> None:
    prompt_id = "<Prompt Id that you got from calling the generate function>"
    try:
        cancel_result = await infer_cancel(
            view_comfy_api_url=view_comfy_api_url,
            prompt_id=prompt_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        print(cancel_result)
    except Exception as e:
        msg = f"something went wrong calling the api, Error: {e}"
        print(msg)
        raise


if __name__ == "__main__":
    asyncio.run(api())


# if __name__ == "__main__":
#     asyncio.run(cancel())
