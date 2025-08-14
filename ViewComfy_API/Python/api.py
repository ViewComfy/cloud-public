import asyncio
import itertools
import json
import sys
import uuid
from enum import Enum
from io import BufferedReader
from typing import Any, Callable

import httpx
import socketio

SERVER_URL = "https://api.viewcomfy.com"


class FileOutput:
    """Represents a file output with its content encoded in base64."""

    def __init__(self, filename: str, content_type: str, data: str, size: int) -> None:
        """Initialize a FileOutput object.

        Args:
            filename (str): Name of the output file
            content_type (str): MIME type of the file
            data (str): Base64 encoded file content
            size (int): Size of the file in bytes

        """
        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.size = size


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
            prompt (Dict): The original prompt configuration
            outputs (List[Dict], optional): List of output file data. Defaults to empty list.

        """
        self.prompt_id = prompt_id
        self.status = status
        self.completed = completed
        self.execution_time_seconds = execution_time_seconds
        self.prompt = prompt

        # Initialize outputs as FileOutput objects
        self.outputs = []
        if outputs:
            for output_data in outputs:
                if output_data.get("data", ""):
                    self.outputs.append(
                        FileOutput(
                            filename=output_data.get("filename", ""),
                            content_type=output_data.get("content_type", ""),
                            data=output_data.get("data", ""),
                            size=output_data.get("size", 0),
                        ),
                    )
                else:
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

        @self.sio.on(InferEmitEventEnum.LogMessage)
        async def log_message(data: dict[str, Any]) -> None:
            self.is_workflow_loading = False
            print(f"logs: {data}")

        @self.sio.on(InferEmitEventEnum.ErrorMessage)
        async def error_message(data: dict[str, Any]) -> None:
            print(f"Error: {data}")
            self.is_ws_connected = False

        @self.sio.on(InferEmitEventEnum.ExecutedMessage)
        async def executed_message(data: dict[str, Any]) -> None:
            print(f"prompt executed: {data}")

        @self.sio.on(InferEmitEventEnum.ResultMessage)
        async def result_message(data: dict[str, Any]) -> None:
            if data:
                self.prompt_result = PromptResult(**data)
            self.is_ws_connected = False

        # @self.sio.event
        # def connect():
        # print(f"I'm connected: {self.sio.sid}")
        # self.is_ws_connected = False

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
        data: dict[str, Any],
        files: list[tuple[str, BufferedReader]] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request to the /api/infer-files endpoint with files encoded in form data.

        Args:
            data: Dictionary of form fields (logs, params, etc.)
            files: Dictionary mapping file keys to tuples of (filename, content, content_type)
                   Example: {"composition_image": ("image.jpg", file_content, "image/jpeg")}

        Returns:
            Dict[str, Any]: Response from the server

        """
        if files is None:
            files = []

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.infer_url,
                    data=data,
                    files=files,
                    timeout=httpx.Timeout(2400.0),
                    follow_redirects=True,
                    headers={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                )

                if response.status_code == 201:
                    return response.json()
                error_text = response.text
                msg = f"API request failed with status {response.status_code}: {error_text}"
                raise Exception(
                    msg,
                )
            except httpx.HTTPError as e:
                raise Exception(f"Connection error: {e!s}")
            except Exception as e:
                raise Exception(f"Error during API call: {e!s}")

    async def consume_event_source(
        self,
        *,
        response,
        logging_callback: Callable[[str], None],
    ) -> dict[str, Any] | None:
        """Process a streaming Server-Sent Events (SSE) response.

        Args:
            response: An active httpx streaming response object

        Returns:
            List of parsed event objects

        """
        current_data = ""
        current_event = "message"  # Default event type

        prompt_result = None
        # Process the response as it streams in
        async for line in response.aiter_lines():
            line = line.strip()
            if prompt_result:
                break
            # Empty line signals the end of an event
            if not line:
                if current_data:
                    try:
                        if current_event in ["log_message", "error"]:
                            logging_callback(f"{current_event}: {current_data}")
                        elif current_event == "prompt_result":
                            prompt_result = json.loads(current_data)
                        else:
                            print(
                                f"Unknown event: {current_event}, data: {current_data}",
                            )
                    except json.JSONDecodeError as e:
                        print("Invalid JSON: ...")
                        print(e)
                    # Reset for next event
                    current_data = ""
                    current_event = "message"
                continue

            # Parse SSE fields
            if line.startswith("event:"):
                current_event = line[6:].strip()
            elif line.startswith("data:"):
                current_data = line[5:].strip()
            elif line.startswith("id:"):
                # Handle event ID if needed
                pass
            elif line.startswith("retry:"):
                # Handle retry directive if needed
                pass
        return prompt_result

    async def infer_with_logs(
        self,
        *,
        data: dict[str, Any],
        logging_callback: Callable[[str], None],
        files: list[tuple[str, BufferedReader]] | None = None,
    ) -> dict[str, Any] | None:
        if files is None:
            files = []

        if data.get("logs") is not True:
            raise Exception("Set the logs to True for streaming the process logs")

        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    self.infer_url,
                    data=data,
                    files=files,
                    timeout=24000,
                    follow_redirects=True,
                    headers={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                ) as response:
                    if response.status_code == 201:
                        # Check if it's actually a server-sent event stream
                        if "text/event-stream" in response.headers.get(
                            "content-type",
                            "",
                        ):
                            prompt_result = await self.consume_event_source(
                                response=response,
                                logging_callback=logging_callback,
                            )
                            return prompt_result
                        # For non-SSE responses, read the content normally
                        raise Exception(
                            "Set the logs to True for streaming the process logs",
                        )
                    error_response = await response.aread()
                    error_data = json.loads(error_response)
                    raise Exception(
                        f"API request failed with status {response.status_code}: {error_data}",
                    )
            except Exception as e:
                raise Exception(f"Error with streaming request: {e!s}")

    async def infer_with_ws(
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
            await self.sio.connect(SERVER_URL, auth=auth)
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
                    f"{SERVER_URL}/api/workflow/infer",
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
    api_url: str,
    override_workflow_api: dict[str, Any] | None = None,
    client_id: str,
    client_secret: str,
):
    """Make an inference with real-time logs from the execution prompt.

    Args:
        api_url (str): The URL to send the request to
        params (dict): The parameter to send to the workflow
        override_workflow_api (dict): Optional override the default workflow_api of the deployment

    Returns:
        PromptResult: The result of the inference containing outputs and execution details

    """
    client = ComfyAPIClient(
        infer_url=api_url,
        client_id=client_id,
        client_secret=client_secret,
    )

    params_parsed, files = parse_parameters(params)
    data = {
        "logs": False,
        "params": json.dumps(params_parsed),
        "workflow_api": json.dumps(override_workflow_api)
        if override_workflow_api
        else None,
    }

    # Make the API call
    result = await client.infer(data=data, files=files)

    return PromptResult(**result)


async def infer_with_logs(
    *,
    params: dict[str, Any],
    logging_callback: Callable[[str], None],
    api_url: str,
    override_workflow_api: dict[str, Any] | None = None,
    client_id: str,
    client_secret: str,
):
    """Make an inference with real-time logs from the execution prompt.

    Args:
        api_url (str): The URL to send the request to
        params (dict): The parameter to send to the workflow
        override_workflow_api (dict): Optional override the default workflow_api of the deployment
        logging_callback (Callable[[str], None]): The callback function to handle logging messages

    Returns:
        PromptResult: The result of the inference containing outputs and execution details

    """
    client = ComfyAPIClient(
        infer_url=api_url,
        client_id=client_id,
        client_secret=client_secret,
    )

    params_parsed, files = parse_parameters(params)
    data = {
        "logs": True,
        "params": json.dumps(params_parsed),
        "workflow_api": json.dumps(override_workflow_api)
        if override_workflow_api
        else None,
    }

    # Make the API call
    result = await client.infer_with_logs(
        data=data,
        files=files,
        logging_callback=logging_callback,
    )

    if result:
        return PromptResult(**result)

    return None


async def infer_with_logs_ws(
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
    return await client.infer_with_ws(
        params=params,
        view_comfy_api_url=view_comfy_api_url,
        override_workflow_api=override_workflow_api,
    )
