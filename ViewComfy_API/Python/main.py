import asyncio
import json
from pathlib import Path

import aiofiles
import httpx
from api import infer, infer_cancel, infer_info, infer_with_logs

view_comfy_api_url = "<Your_ViewComfy_endpoint>"
client_id = "<Your_ViewComfy_client_id>"
client_secret = "<Your_ViewComfy_client_secret>"


async def api_realtime(params: dict) -> None:
    # Advanced feature: overwrite default workflow with a new one:
    # https://github.com/ViewComfy/cloud-public/tree/main/ViewComfy_API#using-the-api-with-a-different-workflow
    override_workflow_api_path = None

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
        prompt_result = await infer_with_logs(
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


async def api_batch(params: dict) -> str:
    # Advanced feature: overwrite default workflow with a new one:
    # https://github.com/ViewComfy/cloud-public/tree/main/ViewComfy_API#using-the-api-with-a-different-workflow
    override_workflow_api_path = None

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

    return prompt_result.prompt_id


async def get_results() -> None:
    prompt_ids = ["<prompt_id>"]
    try:
        prompt_results = await infer_info(
            view_comfy_api_url=view_comfy_api_url,
            prompt_ids=prompt_ids,
            client_id=client_id,
            client_secret=client_secret,
        )
    except Exception as e:
        msg = f"something went wrong calling the api, Error: {e}"
        print(msg)
        raise

    if not prompt_results:
        message = "No prompt_result generated"
        print(message)
        raise Exception(message)

    for result in prompt_results:
        if result.status != "success":
            print(f"{result.prompt_id} is still running")
            continue
        for file in result.outputs:
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


async def api_with_realtime_logs():
    params = {}

    params["6-inputs-text"] = "A cat sorcerer"
    params["10-inputs-image"] = Path("input_folder/input_img.png").open("rb")
    await api_realtime(params)


async def api_in_batch():
    job_params: list[dict] = []
    params1 = {}
    params1["6-inputs-text"] = "A cat sorcerer"
    params1["10-inputs-image"] = Path("input_folder/input_img.png").open("rb")

    job_params.append(params1)

    async def main_tasks() -> None:
        prompt_ids = []
        for params in job_params:
            try:
                result = await api_batch(params)
                prompt_ids.append(result)
            except Exception as e:
                print(f"Task failed with exception: {e}")

        print(prompt_ids)

    await main_tasks()


if __name__ == "__main__":
    asyncio.run(api_with_realtime_logs())

# if __name__ == "__main__":
#     asyncio.run(api_in_batch())

# if __name__ == "__main__":
#     asyncio.run(cancel())


# if __name__ == "__main__":
#     asyncio.run(get_results())
