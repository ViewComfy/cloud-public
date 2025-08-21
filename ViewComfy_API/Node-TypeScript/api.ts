import io, { Socket } from "socket.io-client"
import { v4 as uuidv4 } from 'uuid';


function buildFormData(data: {
    params: Record<string, any>;
    overrideWorkflowApi?: Record<string, any> | undefined;
    prompt_id: string;
    viewComfyApiUrl: string;
    sid: string;
}): FormData {
    const { params, overrideWorkflowApi, prompt_id, viewComfyApiUrl, sid } = data;
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
    formData.set("view_comfy_api_url", viewComfyApiUrl);
    formData.set("sid", sid);

    if (overrideWorkflowApi) {
        formData.set("workflow_api", JSON.stringify(overrideWorkflowApi));
    }

    return formData;
}

interface Infer {
    viewComfyApiUrl: string;
    params: Record<string, any>;
    overrideWorkflowApi?: Record<string, any> | undefined;
    clientId: string;
    clientSecret: string;
}

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
 * @param viewComfyApiUrl - The URL to send the request to
 * @param params - The parameter to send to the workflow
 * @param overrideWorkflowApi - Optional override the default workflow_api of the deployment
 * @returns The parsed prompt result or null
 */
export const infer = ({
    viewComfyApiUrl,
    params,
    overrideWorkflowApi,
    clientId,
    clientSecret,
}: Infer): Promise<PromptResult | undefined> => {

    if (!viewComfyApiUrl) {
        throw new Error("viewComfyApiUrl is not set");
    }
    if (!clientId) {
        throw new Error("clientId is not set");
    }
    if (!clientSecret) {
        throw new Error("clientSecret is not set");
    }

    const API_URL = "https://api.viewcomfy.com"

    const auth = {
        "client_id": clientId,
        "client_secret": clientSecret,
    };

    return new Promise((resolve, reject) => {
        const prompt_id: string = uuidv4();
        let socket: Socket;

        try {
            socket = io(API_URL, { auth, transports: ["websocket"] });
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
            const formData = buildFormData({
                params,
                overrideWorkflowApi,
                viewComfyApiUrl,
                sid: socket.id!,
                prompt_id,
            });

            try {
                const response = await fetch(`${API_URL}/api/workflow/infer`, {
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
            console.log(JSON.stringify(data));
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
 * Represents the output file with a link to download the data from a prompt execution
 */
export class S3FileData {
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
    outputs: S3FileData[];

    constructor(data: {
        prompt_id: string;
        status: string;
        completed: boolean;
        execution_time_seconds: number;
        prompt: Record<string, any>;
        outputs?: S3FileData[];
    }) {
        const {
            prompt_id,
            status,
            completed,
            execution_time_seconds,
            prompt,
            outputs = [],
        } = data;


        this.prompt_id = prompt_id;
        this.status = status;
        this.completed = completed;
        this.execution_time_seconds = execution_time_seconds;
        this.prompt = prompt;
        this.outputs = outputs;
    }
}
