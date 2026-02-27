import { fetchData, RequestMethod, APIErrorResponse } from '../scripts/common'

// Structures.
export interface Task {
    name: string
    description: string | null
    file_format_list: string[]
}

export interface Project {
    _id: string
    name: string
    description: string | null
    task: Task['name']
    created_at: string
    updated_at: string
}

// Functions.
function validateProjectName(name: string): void {
    // Check if the name is empty.
    if (!name) {
        console.error('Project name cannot be empty.')
        throw new APIErrorResponse('Project name cannot be empty.', 400)
    }

    // Check characters.
    const invalidChars = /[.<>:"/\\|?*]/g
    if (invalidChars.test(name)) {
        console.error('Project name contains invalid characters: . < > : " / \\ | ? *')
        throw new APIErrorResponse('Project name contains invalid characters: . < > : " / \\ | ? *', 400)
    }
}

export async function createProjectRequest(
    name: string,
    task: string,
    password: string | null = null,
): Promise<Project> {
    // Check input validity.
    console.debug(`Creating project with name: ${name}, task: ${task}`)

    // Validate fields.
    validateProjectName(name.trim())

    // Create body for the request.
    const body = {
        name: name,
        task: task,
        password: password,
    }
    console.debug('Project body:', body)

    // Send request to the backend.
    const responseData = await fetchData('/projects/', RequestMethod.POST, undefined, body)
    console.debug('Project created successfully:', responseData)
    return await responseData
}

export async function deleteProjectRequest(projectId: string): Promise<void> {
    console.debug(`Deleting project with ID: ${projectId}`)
    if (!projectId) {
        console.error('Project ID is required for deletion.')
        throw new APIErrorResponse('Project ID is required for deletion.', 400)
    }

    await fetchData(`/projects/${projectId}/`, RequestMethod.DELETE)
    console.debug(`Project with ID: ${projectId} deleted successfully.`)
}
