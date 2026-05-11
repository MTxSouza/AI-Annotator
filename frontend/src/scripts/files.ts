import { RequestMethod, fetchData } from './common'

// Interfaces.
export interface File {
    _id: string
    project_id_list: string[]
    file_hash: string
    filename: string
    file_format: string
    size_in_bytes: number
    created_at: string
    updated_at: string
}

export interface FileUploadWorkerResult {
    task_id: string
    message: string
}

export interface FileUploadWorkerStatus {
    status: string
    result: any | null
}

// Functions.
export async function uploadFileToProject(files: FileList | null, projectId: string): Promise<FileUploadWorkerResult> {
    // Ignore if no files are selected.
    if (!files || files.length === 0) {
        throw new Error('No files selected for upload.')
    }

    // Create form data for file upload.
    const formData = new FormData()
    for (let i = 0; i < files.length; i++) {
        formData.append('file_list', files[i])
    }
    console.debug(`Uploading ${files.length} files to project ${projectId}`)

    // Send upload request to the server.
    const fileUploadWorkerResult = await fetchData(
        `/projects/${projectId}/files`,
        RequestMethod.POST,
        undefined,
        formData,
    )
    console.debug('Upload worker response:', fileUploadWorkerResult)
    return fileUploadWorkerResult
}
