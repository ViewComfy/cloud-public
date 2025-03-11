import json
from io import BufferedReader
from typing import Any, Callable, Dict, List
import httpx


class FileOutput:
    """Represents a file output with its content encoded in base64"""

    def __init__(self, filename: str, content_type: str, data: str, size: int):
        """
        Initialize a FileOutput object.

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


class PromptResult:
    def __init__(
        self,
        prompt_id: str,
        status: str,
        completed: bool,
        execution_time_seconds: float,
        prompt: Dict,
        outputs: List[Dict] | None = None,
    ):
        """
        Initialize a PromptResult object.

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
                self.outputs.append(
                    FileOutput(
                        filename=output_data.get("filename", ""),
                        content_type=output_data.get("content_type", ""),
                        data=output_data.get("data", ""),
                        size=output_data.get("size", 0),
                    )
                )


class ComfyAPIClient:
    def __init__(self, infer_url: str = "http://localhost:8000/api/infer"):
        """
        Initialize the ComfyAPI client with the server URL.

        Args:
            base_url (str): The base URL of the API server
        """
        self.infer_url = infer_url

    async def infer(
        self, *, data: Dict[str, Any], files: list[tuple[str, BufferedReader]] = []
    ) -> Dict[str, Any]:
        """
        Make a POST request to the /api/infer-files endpoint with files encoded in form data.

        Args:
            data: Dictionary of form fields (logs, params, etc.)
            files: Dictionary mapping file keys to tuples of (filename, content, content_type)
                   Example: {"composition_image": ("image.jpg", file_content, "image/jpeg")}

        Returns:
            Dict[str, Any]: Response from the server
        """

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.infer_url,
                    data=data,
                    files=files,
                    timeout=httpx.Timeout(2400.0),
                    follow_redirects=True,
                )

                if response.status_code == 201:
                    return response.json()
                else:
                    error_text = response.text
                    raise Exception(
                        f"API request failed with status {response.status_code}: {error_text}"
                    )
            except httpx.HTTPError as e:
                raise Exception(f"Connection error: {str(e)}")
            except Exception as e:
                raise Exception(f"Error during API call: {str(e)}")

    async def consume_event_source(
        self, *, response, logging_callback: Callable[[str], None]
    ) -> Dict[str, Any] | None:
        """
        Process a streaming Server-Sent Events (SSE) response.

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
                                f"Unknown event: {current_event}, data: {current_data}"
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
        data: Dict[str, Any],
        logging_callback: Callable[[str], None],
        files: list[tuple[str, BufferedReader]] = [],
    ) -> Dict[str, Any] | None:
        """
        Make an inference with real-time logs from the execution prompt

        Args:
            view_comfy_api_url (str): The ViewComfy endpoint to send the request to
            data (dict): The parameter to send to the workflow
            logging_callback (Callable[[str], None]): The callback function to handle logging messages
            files (list[tuple[str, BufferedReader]]): The files to send to the workflow
        Returns:
            PromptResult: The result of the inference containing outputs and execution details
        """
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
                ) as response:
                    if response.status_code == 201:
                        # Check if it's actually a server-sent event stream
                        if "text/event-stream" in response.headers.get(
                            "content-type", ""
                        ):
                            prompt_result = await self.consume_event_source(
                                response=response, logging_callback=logging_callback
                            )
                            return prompt_result
                        else:
                            # For non-SSE responses, read the content normally
                            raise Exception(
                                "Set the logs to True for streaming the process logs"
                            )
                    else:
                        print(f"Error response: {await response.aread()}")
            except Exception as e:
                print(f"Error with streaming request: {str(e)}")


def parse_parameters(params: dict):
    """
    Parse parameters from a dictionary to a format suitable for the API call.

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
    params: Dict[str, Any],
    api_url: str,
    override_workflow_api: Dict[str, Any] | None = None,
):
    """
    Make an inference with real-time logs from the execution prompt

    Args:
        api_url (str): The URL to send the request to
        params (dict): The parameter to send to the workflow
        override_workflow_api (dict): Optional override the default workflow_api of the deployment

    Returns:
        PromptResult: The result of the inference containing outputs and execution details
    """
    client = ComfyAPIClient(api_url)

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
    params: Dict[str, Any],
    logging_callback: Callable[[str], None],
    api_url: str,
    override_workflow_api: Dict[str, Any] | None = None,
):
    """
    Make an inference with real-time logs from the execution prompt

    Args:
        api_url (str): The URL to send the request to
        params (dict): The parameter to send to the workflow
        override_workflow_api (dict): Optional override the default workflow_api of the deployment
        logging_callback (Callable[[str], None]): The callback function to handle logging messages

    Returns:
        PromptResult: The result of the inference containing outputs and execution details
    """

    client = ComfyAPIClient(api_url)

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
        data=data, files=files, logging_callback=logging_callback
    )

    if result:
        return PromptResult(**result)
