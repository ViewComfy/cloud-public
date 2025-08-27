import asyncio
import itertools
import json
import sys
import uuid
from enum import Enum
from io import BufferedReader
from typing import Any

import httpx
import socketio

API_URL = "https://api.viewcomfy.com"


class S3FileOutput:
    """Represents a file output with its content with an S3 bucket link."""

    def __init__(
        self,
        filename: str,
        content_type: str,
        size: int,
        filepath: str,
    ) -> None:
        """Initialize a FileOutput object.

        Args:
            filename (str): Name of the output file
            content_type (str): MIME type of the file
            filepath (str): the s3 path file content
            size (int): Size of the file in bytes

        """
        self.filename = filename
        self.content_type = content_type
        self.size = size
        self.filepath = filepath


class PromptResult:
    def __init__(
        self,
        prompt_id: str,
        status: str,
        completed: bool,
        execution_time_seconds: float,
        prompt: dict,
        outputs: list[dict[str, Any]],
    ) -> None:
        """Initialize a PromptResult object.

        Args:
            prompt_id (str): Unique identifier for the prompt
            status (str): Current status of the prompt execution
            completed (bool): Whether the prompt execution is complete
            execution_time_seconds (float): Time taken to execute the prompt
            prompt (dict): The original prompt configuration
            outputs (list[S3FileOutput], optional): List of output file data. Defaults to empty list.

        """
        self.prompt_id = prompt_id
        self.status = status
        self.completed = completed
        self.execution_time_seconds = execution_time_seconds
        self.prompt = prompt

        self.outputs = []
        if outputs:
            for output_data in outputs:
                self.outputs.append(
                    S3FileOutput(
                        filename=output_data.get("filename", ""),
                        content_type=output_data.get("content_type", ""),
                        size=output_data.get("size", 0),
                        filepath=output_data.get("filepath", ""),
                    ),
                )


class InferEmitEventEnum(str, Enum):
    LogMessage = "infer_log_message"
    ErrorMessage = "infer_error_message"
    ExecutedMessage = "infer_executed_message"
    JoinRoom = "infer_join_room"
    ResultMessage = "infer_result_message"
    CanceledInference = "infer_canceled_message"


class ComfyAPIClient:
    def __init__(
        self,
        *,
        infer_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        """Initialize the ComfyAPI client with the server URL.

        Args:
            base_url (str): The base URL of the API server

        """
        if infer_url is None:
            raise Exception("infer_url is required")
        self.infer_url = infer_url

        if client_id is None:
            raise Exception("client_id is required")

        if client_secret is None:
            raise Exception("client_secret is required")

        self.client_id = client_id
        self.client_secret = client_secret
        self.sio = socketio.AsyncClient()
        self.is_ws_connected = False
        self.prompt_result: PromptResult | None = None
        self.is_workflow_loading = True

        @self.sio.on(InferEmitEventEnum.LogMessage)  # pyright: ignore[reportOptionalCall]
        async def log_message(data: dict[str, Any]) -> None:
            self.is_workflow_loading = False
            print(f"logs: {data}")

        @self.sio.on(InferEmitEventEnum.ErrorMessage)  # pyright: ignore[reportOptionalCall]
        async def error_message(data: dict[str, Any]) -> None:
            print(f"Error: {data}")
            self.is_ws_connected = False

        @self.sio.on(InferEmitEventEnum.ExecutedMessage)  # pyright: ignore[reportOptionalCall]
        async def executed_message(data: dict[str, Any]) -> None:
            print(f"prompt executed: {data}")

        @self.sio.on(InferEmitEventEnum.ResultMessage)  # pyright: ignore[reportOptionalCall]
        async def result_message(data: dict[str, Any]) -> None:
            if data:
                self.prompt_result = PromptResult(**data)
            self.is_ws_connected = False

        @self.sio.on(InferEmitEventEnum.CanceledInference)  # pyright: ignore[reportOptionalCall]
        async def canceled_message(data: dict[str, Any]) -> None:
            print(f"the workflow has been canceled: {data}")
            self.is_ws_connected = False

        @self.sio.event
        def disconnect(reason):
            # if reason == self.sio.reason.CLIENT_DISCONNECT:
            #     print('the client disconnected')
            # elif reason == self.sio.reason.SERVER_DISCONNECT:
            #     print('the server disconnected the client')
            # else:
            #     print('disconnect reason:', reason)
            self.is_ws_connected = False

    async def infer(
        self,
        *,
        params: dict[str, Any],
        view_comfy_api_url: str,
        override_workflow_api: dict[str, Any] | None = None,
    ) -> PromptResult | None:
        override_workflow_api_param: str | None = None
        if override_workflow_api:
            override_workflow_api_param = json.dumps(override_workflow_api)

        params_parsed, files = parse_parameters(params)
        prompt_id = str(uuid.uuid4())

        try:
            auth = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            await self.sio.connect(API_URL, auth=auth, transports=["websocket"])
            self.is_ws_connected = True
        except Exception as e:
            err = Exception(f"Unable to connect to to websocket server, e: {e}")
            raise err from e

        data = {
            "prompt_id": prompt_id,
            "view_comfy_api_url": view_comfy_api_url,
            "params": json.dumps(params_parsed),
            "workflow_api": override_workflow_api_param,
            "sid": self.sio.get_sid(namespace="/"),
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{API_URL}/api/workflow/infer",
                    data=data,
                    files=files,
                    timeout=httpx.Timeout(2400.0),
                    follow_redirects=True,
                    headers=auth,
                )

                if response.status_code == 201:
                    response_json = response.json()
                else:
                    error_text = response.text
                    err_msg = f"API request failed with status {response.status_code}: {error_text}"
                    raise Exception(err_msg)

            except httpx.HTTPError as e:
                msg = f"Connection error: {e!s}"
                raise Exception(msg) from e
            except Exception as e:
                msg = f"Error during API call: {e!s}"
                raise Exception(msg) from e

        print(response_json.get("data", None))

        loading_animation = itertools.cycle(
            ["Loading.  ", "Loading.. ", "Loading..."],
        )
        while self.is_ws_connected:
            if self.is_workflow_loading:
                sys.stdout.write(f"\r{next(loading_animation)}")
                sys.stdout.flush()
            await asyncio.sleep(0.3)

        await self.sio.disconnect()
        return self.prompt_result

    async def _cancel_infer(self, *, prompt_id: str, view_comfy_api_url: str):
        auth = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        data = {"prompt_id": prompt_id, "view_comfy_api_url": view_comfy_api_url}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{API_URL}/api/workflow/infer/cancel",
                    json=data,
                    timeout=httpx.Timeout(2400.0),
                    headers=auth,
                )

                if response.status_code == 201:
                    return response.json()
                error_text = response.text
                err_msg = f"API request failed with status {response.status_code}: {error_text}"
                raise Exception(err_msg)

            except httpx.HTTPError as e:
                msg = f"Connection error: {e!s}"
                raise Exception(msg) from e
            except Exception as e:
                msg = f"Error during API call: {e!s}"
                raise Exception(msg) from e


def parse_parameters(params: dict):
    """Parse parameters from a dictionary to a format suitable for the API call.

    Args:
        params (dict): Dictionary of parameters

    Returns:
        dict: Parsed parameters

    """
    parsed_params = {}
    files = []
    for key, value in params.items():
        if isinstance(value, BufferedReader):
            files.append((key, value))
        else:
            parsed_params[key] = value
    return parsed_params, files


async def infer(
    *,
    params: dict[str, Any],
    view_comfy_api_url: str,
    override_workflow_api: dict[str, Any] | None = None,
    client_id: str,
    client_secret: str,
) -> PromptResult | None:
    client = ComfyAPIClient(
        infer_url=view_comfy_api_url,
        client_id=client_id,
        client_secret=client_secret,
    )

    # Make the API call
    return await client.infer(
        params=params,
        view_comfy_api_url=view_comfy_api_url,
        override_workflow_api=override_workflow_api,
    )


async def infer_cancel(
    *,
    prompt_id: str,
    view_comfy_api_url: str,
    client_id: str,
    client_secret: str,
):
    client = ComfyAPIClient(
        infer_url=view_comfy_api_url,
        client_id=client_id,
        client_secret=client_secret,
    )

    return await client._cancel_infer(
        prompt_id=prompt_id,
        view_comfy_api_url=view_comfy_api_url,
    )
