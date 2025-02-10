export interface IInput {
    value: string | File | number | boolean;
    key: string;
}

export interface IViewComfy {
    inputs: IInput[];
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
