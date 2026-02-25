import { fetchData, RequestMethod } from '../scripts/common'

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
export async function createProjectRequest(name: string, task: string): Promise<Project> {
    // Check input validity.
    console.debug(`Creating project with name: ${name}, task: ${task}`)
    if (!name || !task) {
        console.error('Project name and task are required.')
        throw new Error('Project name and task are required.')
    }

    if (name.length < 3) {
        console.error('Project name must be at least 3 characters long.')
        throw new Error('Project name must be at least 3 characters long.')
    }

    // Create body for the request.
    const body = {
        name: name,
        task: task,
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
        throw new Error('Project ID is required for deletion.')
    }

    await fetchData(`/projects/${projectId}/`, RequestMethod.DELETE)
    console.debug(`Project with ID: ${projectId} deleted successfully.`)
}
