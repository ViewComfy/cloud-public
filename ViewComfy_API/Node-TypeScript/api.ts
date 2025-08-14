import io, { Socket } from "socket.io-client"
import { v4 as uuidv4 } from 'uuid';

function buildFormData(data: {
    logs: boolean;
    params: Record<string, any>;
    overrideWorkflowApi?: Record<string, any> | undefined;
}): FormData {
    const { params, overrideWorkflowApi, logs } = data;
    const formData = new FormData();
    let params_str = {};
    for (const key in params) {
        const value = params[key];
        if (value instanceof File) {
            formData.set(key, value);
        } else {
            params_str[key] = value;
        }
    }

    if (overrideWorkflowApi) {
        formData.set("workflow_api", JSON.stringify(overrideWorkflowApi));
    }

    formData.set("params", JSON.stringify(params_str));

    formData.set("logs", logs.toString());

    return formData;
}

function buildFormDataWS(data: {
    params: Record<string, any>;
    overrideWorkflowApi?: Record<string, any> | undefined;
    prompt_id: string;
    view_comfy_api_url: string;
    sid: string;
}): FormData {
    const { params, overrideWorkflowApi, prompt_id, view_comfy_api_url, sid } = data;
    const formData = new FormData();
    let params_str = {};
    for (const key in params) {
        const value = params[key];
        if (value instanceof File) {
            formData.set(key, value);
        } else {
            params_str[key] = value;
        }
    }

    formData.set("params", JSON.stringify(params_str));
    formData.set("prompt_id", prompt_id);
    formData.set("view_comfy_api_url", view_comfy_api_url);
    formData.set("sid", sid);

    if (overrideWorkflowApi) {
        formData.set("workflow_api", JSON.stringify(overrideWorkflowApi));
    }

    return formData;
}

interface Infer {
    apiUrl: string;
    params: Record<string, any>;
    overrideWorkflowApi?: Record<string, any> | undefined;
    clientId: string;
    clientSecret: string;
}

interface InferWithLogs extends Infer {
    loggingCallback: (message: string) => void;
}

/**
 * Make an inference request to the viewComfy API
 *
 * @param apiUrl - The URL to send the request to
 * @param params - The parameter to send to the workflow
 * @param overrideWorkflowApi - Optional override the default workflow_api of the deployment
 * @returns The parsed prompt result or null
 */
export const infer = async ({
    apiUrl,
    params,
    overrideWorkflowApi,
    clientId,
    clientSecret,
}: Infer) => {
    if (!apiUrl) {
        throw new Error("viewComfyUrl is not set");
    }
    if (!clientId) {
        throw new Error("clientId is not set");
    }
    if (!clientSecret) {
        throw new Error("clientSecret is not set");
    }

    try {
        const formData = buildFormData({
            logs: false,
            params,
            overrideWorkflowApi,
        });

        const response = await fetch(apiUrl, {
            method: "POST",
            body: formData,
            redirect: "follow",
            headers: {
                "client_id": clientId,
                "client_secret": clientSecret,
            },
        });

        if (!response.ok) {
            const errMsg = `Failed to fetch viewComfy: ${response.statusText
                }, ${await response.text()}`;
            console.error(errMsg);
            throw new Error(errMsg);
        }

        const data = await response.json();
        return new PromptResult(data);
    } catch (error) {
        throw error;
    }
};

enum InferEmitEventEnum {
    LogMessage = "infer_log_message",
    ErrorMessage = "infer_error_message",
    ExecutedMessage = "infer_executed_message",
    JoinRoom = "infer_join_room",
    ResultMessage = "infer_result_message",
}

/**
 * Make an inference request to the viewComfy API
 *
 * @param apiUrl - The URL to send the request to
 * @param params - The parameter to send to the workflow
 * @param overrideWorkflowApi - Optional override the default workflow_api of the deployment
 * @returns The parsed prompt result or null
 */
export const inferWithLogsWS = ({
    apiUrl,
    params,
    overrideWorkflowApi,
    clientId,
    clientSecret,
}: Infer): Promise<PromptResult | undefined> => {

    if (!apiUrl) {
        throw new Error("viewComfyUrl is not set");
    }
    if (!clientId) {
        throw new Error("clientId is not set");
    }
    if (!clientSecret) {
        throw new Error("clientSecret is not set");
    }

    const SERVER_URL = "https://api.viewcomfy.com"

    const auth = {
        "client_id": clientId,
        "client_secret": clientSecret,
    };

    return new Promise((resolve, reject) => {
        const prompt_id: string = uuidv4();
        let socket: Socket;

        try {
            socket = io(SERVER_URL, { auth });
            console.log("Socket initialized. Waiting for connection...");
        } catch (error) {
            console.log("Something went wrong trying to initialize socket.")
            return reject(error);
        }

        let loading_interval: NodeJS.Timeout;
        let isWorkflowExecuted = false;

        const cleanup = (result?: PromptResult) => {
            clearInterval(loading_interval);
            socket.disconnect();
            resolve(result);
        };

        socket.on('connect', async () => {
            const formData = buildFormDataWS({
                params,
                overrideWorkflowApi,
                view_comfy_api_url: apiUrl,
                sid: socket.id!,
                prompt_id,
            });

            try {
                const response = await fetch(`${SERVER_URL}/api/workflow/infer`, {
                    method: "POST",
                    body: formData,
                    redirect: "follow",
                    headers: auth,
                });

                if (!response.ok) {
                    const errMsg = `Failed to fetch viewComfy: ${response.statusText}, ${await response.text()}`;
                    console.error(errMsg);
                    socket.disconnect();
                    return reject(new Error(errMsg));
                }

                const res = await response.json();
                console.log(res["data"]);

                let dots = 0;
                loading_interval = setInterval(() => {
                    dots = (dots % 3) + 1;
                    const message = "Loading" + ".".repeat(dots);
                    process.stdout.write(`\r${message.padEnd(20)}`);
                }, 500);

            } catch (error) {
                console.error("Error during fetch:", error);
                socket.disconnect();
                reject(error);
            }
        });

        socket.on('connect_error', (err) => {
            console.error('Socket connection error:', err);
            clearInterval(loading_interval);
            socket.disconnect();
            reject(err);
        });

        socket.on('disconnect', (reason) => {
            if (reason !== "io client disconnect") {
                console.log(`Socket disconnected: ${reason}`);
                clearInterval(loading_interval);
                // If the disconnect was not initiated by a result or error, it's unexpected.
                // We can reject the promise to avoid the script hanging.
                reject(new Error(`Socket disconnected unexpectedly: ${reason}`));
            }
        });

        socket.on(InferEmitEventEnum.LogMessage, (data: any) => {
            clearInterval(loading_interval);
            process.stdout.write(data as string);
        });

        socket.on(InferEmitEventEnum.ErrorMessage, (data: { [key: string]: any }) => {
            console.error(`error: ${JSON.stringify(data)}`);
            clearInterval(loading_interval);
            socket.disconnect();
            if (!isWorkflowExecuted) {
                reject(new Error(JSON.stringify(data)));
            }
        });

        socket.on(InferEmitEventEnum.ExecutedMessage, (data: { [key: string]: any }) => {
            console.log(`prompt executed: ${JSON.stringify(data)}`);
        });

        socket.on(InferEmitEventEnum.ResultMessage, (data: any) => {
            console.log("Result message received.");
            isWorkflowExecuted = true;
            if (data) {
                cleanup(new PromptResult(data));
            } else {
                cleanup();
            }
        });
    });
};

/**
 * Process a streaming Server-Sent Events (SSE) response.
 *
 * @param response - An active fetch response with a readable stream
 * @param loggingCallback - Function to handle log messages
 * @returns The parsed prompt result or null
 */
async function consumeEventSource(
    response: Response,
    loggingCallback: (message: string) => void
): Promise<PromptResult | null> {
    if (!response.body) {
        throw new Error("Response body is null");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let currentData = "";
    let currentEvent = "message"; // Default event type
    let promptResult: PromptResult | null = null;
    let buffer = "";

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // Process complete lines in the buffer
            const lines = buffer.split("\n");
            buffer = lines.pop() || ""; // Keep the last incomplete line in the buffer

            for (const line of lines) {
                const trimmedLine = line.trim();
                if (promptResult) break;

                // Empty line signals the end of an event
                if (!trimmedLine) {
                    if (currentData) {
                        try {
                            if (
                                currentEvent === "log_message" ||
                                currentEvent === "error"
                            ) {
                                loggingCallback(
                                    `${currentEvent}: ${currentData}`
                                );
                            } else if (currentEvent === "prompt_result") {
                                promptResult = new PromptResult(
                                    JSON.parse(currentData)
                                );
                            } else {
                                console.log(
                                    `Unknown event: ${currentEvent}, data: ${currentData}`
                                );
                            }
                        } catch (e) {
                            console.log("Invalid JSON: ...");
                            console.error(e);
                        }
                        // Reset for next event
                        currentData = "";
                        currentEvent = "message";
                    }
                    continue;
                }

                // Parse SSE fields
                if (trimmedLine.startsWith("event:")) {
                    currentEvent = trimmedLine.substring(6).trim();
                } else if (trimmedLine.startsWith("data:")) {
                    currentData = trimmedLine.substring(5).trim();
                } else if (trimmedLine.startsWith("id:")) {
                    // Handle event ID if needed
                } else if (trimmedLine.startsWith("retry:")) {
                    // Handle retry directive if needed
                }
            }

            if (promptResult) break;
        }
    } catch (error) {
        console.error("Error reading stream:", error);
        throw error;
    }

    return promptResult;
}

/**
 * Make an inference with real-time logs from the execution prompt
 *
 * @param apiUrl - The URL to send the request to
 * @param params - The parameter to send to the workflow
 * @param loggingCallback - Function to handle log messages
 * @param override_workflow_api - Optional override the default workflow_api of the deployment
 * @returns The parsed prompt result or null
 */
export const inferWithLogsStream = async ({
    apiUrl,
    params,
    loggingCallback,
    overrideWorkflowApi: override_workflow_api,
    clientId,
    clientSecret,
}: InferWithLogs): Promise<PromptResult | null> => {
    if (!apiUrl) {
        throw new Error("url is not set");
    }
    if (!clientId) {
        throw new Error("clientId is not set");
    }
    if (!clientSecret) {
        throw new Error("clientSecret is not set");
    }

    try {
        const formData = buildFormData({
            logs: true,
            overrideWorkflowApi: override_workflow_api,
            params,
        });

        const response = await fetch(apiUrl, {
            method: "POST",
            body: formData,
            headers: {
                "client_id": clientId,
                "client_secret": clientSecret,
            },
        });

        if (response.status === 201) {
            // Check if it's actually a server-sent event stream
            const contentType = response.headers.get("content-type") || "";
            if (contentType.includes("text/event-stream")) {
                return await consumeEventSource(response, loggingCallback);
            } else {
                throw new Error(
                    "Set the logs to True for streaming the process logs"
                );
            }
        } else {
            const errorText = await response.text();
            console.error(`Error response: ${errorText}`);
            throw new Error(errorText);
        }
    } catch (e) {
        console.error(
            `Error with streaming request: ${e instanceof Error ? e.message : String(e)
            }`
        );
        throw e;
    }
};

/**
 * Represents the output file data from a prompt execution
 */
export interface FilesData {
    filename: string;
    content_type: string;
    data: string;
    size: number;
}

/**
 * Represents the output file with a link to download the data from a prompt execution
 */
export class S3FilesData {
    filename: string;
    content_type: string;
    filepath: string;
    size: number;
}

/**
 * Creates a PromptResult object from the response
 *
 * @param data Raw prompt result data
 * @returns A properly formatted PromptResult with File objects
 */
export class PromptResult {
    /** Unique identifier for the prompt */
    prompt_id: string;

    /** Current status of the prompt execution */
    status: string;

    /** Whether the prompt execution is complete */
    completed: boolean;

    /** Time taken to execute the prompt in seconds */
    execution_time_seconds: number;

    /** The original prompt configuration */
    prompt: Record<string, any>;

    /** List of output files */
    outputs: File[] | S3FilesData[];

    constructor(data: {
        prompt_id: string;
        status: string;
        completed: boolean;
        execution_time_seconds: number;
        prompt: Record<string, any>;
        outputs?: FilesData[] | S3FilesData[];
    }) {
        const {
            prompt_id,
            status,
            completed,
            execution_time_seconds,
            prompt,
            outputs = [],
        } = data;

        // Convert output data to File objects
        const fileOutputs = outputs.map((output) => {
            if (output.hasOwnProperty("filepath")) {
                return output;
            } else {
                // Convert base64 data to Blob
                const binaryData = atob(output.data);
                const arrayBuffer = new ArrayBuffer(binaryData.length);
                const uint8Array = new Uint8Array(arrayBuffer);

                for (let i = 0; i < binaryData.length; i++) {
                    uint8Array[i] = binaryData.charCodeAt(i);
                }

                const blob = new Blob([arrayBuffer], { type: output.content_type });

                // Create File object from Blob
                return new File([blob], output.filename, {
                    type: output.content_type,
                    lastModified: new Date().getTime(),
                });
            }

        });

        this.prompt_id = prompt_id;
        this.status = status;
        this.completed = completed;
        this.execution_time_seconds = execution_time_seconds;
        this.prompt = prompt;
        this.outputs = fileOutputs;
    }
}
