export interface IInput {
  value: unknown;
  key: string;
}

export interface IViewComfy {
  inputs: IInput[];
  textOutputEnabled?: boolean;
}

export enum ErrorTypes {
  COMFY_WORKFLOW = "ComfyWorkflowError",
  COMFY = "ComfyError",
  UNKNOWN = "UnknownError",
  VIEW_MODE_MISSING_FILES = "ViewModeMissingFilesError",
}

export class ResponseError {
  public errorMsg: string;
  public errorDetails: string | string[];
  public errorType: ErrorTypes;

  constructor(args: {
    errorMsg: string;
    error: string | string[];
    errorType: ErrorTypes;
  }) {
    this.errorMsg = args.errorMsg;
    this.errorDetails = args.error;
    this.errorType = args.errorType;
  }
}

const viewComfyUrl = "";

export const doPost = async ({ viewComfy }: { viewComfy: IViewComfy }) => {
  if (!viewComfyUrl) {
    throw new Error("viewComfyUrl is not set");
  }

  const url = `${viewComfyUrl}/api/comfy`;

  try {
    const formData = new FormData();
    const viewComfyJSON: IViewComfy = {
      inputs: [],
    };
    for (const { key, value } of viewComfy.inputs) {
      if (value instanceof File) {
        formData.append(key, value);
      } else {
        viewComfyJSON.inputs.push({ key, value });
      }
    }

    formData.append("viewComfy", JSON.stringify(viewComfyJSON));
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const responseError: ResponseError =
        (await response.json()) as ResponseError;
      throw responseError;
    }

    if (!response.body) {
      throw new Error("No response body");
    }

    const reader = response.body.getReader();
    let buffer = new Uint8Array(0);
    const output: Blob[] = [];
    const separator = new TextEncoder().encode("--BLOB_SEPARATOR--");

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer = concatUint8Arrays(buffer, value);

      let separatorIndex: number;

      while ((separatorIndex = findSubarray(buffer, separator)) !== -1) {
        const outputPart = buffer.slice(0, separatorIndex);
        buffer = buffer.slice(separatorIndex + separator.length);

        const mimeEndIndex = findSubarray(
          outputPart,
          new TextEncoder().encode("\r\n\r\n")
        );
        if (mimeEndIndex !== -1) {
          const mimeType = new TextDecoder()
            .decode(outputPart.slice(0, mimeEndIndex))
            .split(": ")[1];
          const outputData = outputPart.slice(mimeEndIndex + 4);
          const blob = new Blob([outputData], { type: mimeType });
          output.push(blob);
        }
      }
    }

    return output;
  } catch (error) {
    throw error;
  }
};

function concatUint8Arrays(a: Uint8Array, b: Uint8Array): Uint8Array {
  const c = new Uint8Array(a.length + b.length);
  c.set(a);
  c.set(b, a.length);
  return c;
}

function findSubarray(arr: Uint8Array, separator: Uint8Array): number {
  outer: for (let i = 0; i <= arr.length - separator.length; i++) {
    for (let j = 0; j < separator.length; j++) {
      if (arr[i + j] !== separator[j]) {
        continue outer;
      }
    }
    return i;
  }
  return -1;
}
