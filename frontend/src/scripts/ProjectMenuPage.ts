import { fetchData, RequestMethod } from '../scripts/common'

// Structures.
export enum ProjectTask {
    // Image.
    OBJECT_DETECTION = 'Object Detection',
    IMAGE_CLASSIFICATION = 'Image Classification',
    IMAGE_CAPTION = 'Image Caption',
    OBJECT_CAPTION = 'Object Caption',
    // Text.
    TEXT_CLASSIFICATION = 'Text Classification',
    TEXT_TAGGING = 'Text Tagging',
    // Audio.
    AUDIO_CLASSIFICATION = 'Audio Classification',
    AUDIO_TRANSCRIPTION = 'Audio Transcription',
}

export interface Project {
    _id: string
    name: string
    description: string | null
    task: ProjectTask
    created_at: string
    updated_at: string
}

// Functions.
export async function triggerProjectCreation(): Promise<Project> {
    // Get input values.
    console.debug('Collecting input values for project creation...')
    const createProjectNameInput = document.getElementById('create-project-name-input')
    const createProjectTaskInput = document.getElementById('create-project-task-input')
    if (!createProjectNameInput || !createProjectTaskInput) {
        console.error('Input elements not found.')
        throw new Error('Input elements not found.')
    }

    const projectName = (createProjectNameInput as HTMLInputElement).value
    const projectTask = (createProjectTaskInput as HTMLSelectElement).value as ProjectTask
    console.debug(`Collected input values - Name: ${projectName}, Task: ${projectTask}`)

    // Create project.
    return await createProjectRequest(projectName, projectTask)
}

async function createProjectRequest(name: string, task: ProjectTask): Promise<Project> {
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
