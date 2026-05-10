import { fetchData, RequestMethod, APIErrorResponse } from '../scripts/common'

// Structures.
export interface Task {
    name: string
    description: string | null
    file_format_list: string[]
}

interface ProjectDetails {
    number_of_files: number
    number_of_samples: number
    file_format: string[]
}

export interface Project {
    _id: string
    name: string
    description: string | null
    task: Task['name']
    details: ProjectDetails
    is_private: boolean
    created_at: string
    updated_at: string
}

export interface ProjectUpdate {
    name?: string
    description?: string
    password?: string | null
}

// Functions.
function validateProjectName(name: string): string {
    name = name.trim()

    // Check for empty name.
    if (!name) {
        console.error('Project name cannot be empty.')
        throw new APIErrorResponse('Project name cannot be empty.', 400)
    }

    // Check for invalid characters.
    const invalidChars = /[.<>:"/\\|?*]/g
    if (invalidChars.test(name)) {
        console.error('Project name contains invalid characters: . < > : " / \\ | ? *')
        throw new APIErrorResponse('Project name contains invalid characters: . < > : " / \\ | ? *', 400)
    }

    return name
}

function validateProjectPassword(password: string | null): string | null {
    if (password === null) {
        return null
    }

    password = password.trim()

    // Check for empty password.
    if (!password) {
        console.error('Project password cannot be empty.')
        throw new APIErrorResponse('Project password cannot be empty.', 400)
    }

    return password
}

export async function createProjectRequest(
    name: string,
    task: string,
    password: string | null = null,
): Promise<Project> {
    console.debug(`Creating project with name: ${name}, task: ${task}`)

    // Validate input.
    name = validateProjectName(name)
    password = validateProjectPassword(password)

    // Build request body.
    const body = { name, task, password }
    console.debug('Project body:', body)

    // Request project creation.
    const responseData = await fetchData('/projects/', RequestMethod.POST, undefined, body)
    console.debug('Project created successfully:', responseData)
    return responseData
}

export async function authenticateProjectRequest(projectId: string, password: string): Promise<void> {
    console.debug(`Authenticating project with ID: ${projectId}`)

    // Validate input.
    if (!projectId) {
        throw new APIErrorResponse('Project ID is required for authentication.', 400)
    }
    if (!password) {
        throw new APIErrorResponse('Password is required for authentication.', 400)
    }

    // The backend sets the access_token and refresh_token cookies on success.
    await fetchData(
        '/auth/token',
        RequestMethod.POST,
        undefined,
        { username: projectId, password: password },
        { 'Content-Type': 'application/x-www-form-urlencoded' },
    )
    console.debug('Project authenticated successfully. Auth cookies set by the server.')
}

export async function logoutProjectRequest(): Promise<void> {
    console.debug('Logging out of current project...')

    // Clear auth cookies.
    await fetchData('/auth/logout', RequestMethod.POST)
    console.debug('Logged out. Auth cookies cleared by the server.')
}

export async function getProjectRequest(projectId: string, password: string | null = null): Promise<Project> {
    console.debug(`Fetching project with ID: ${projectId}`)

    // Validate input.
    if (!projectId) {
        throw new APIErrorResponse('Project ID is required for fetching.', 400)
    }
    if (password !== null) {
        // Authenticate first; the server will set the access_token cookie.
        await authenticateProjectRequest(projectId, password)
    }

    // Cookie is sent automatically via credentials: 'include' in fetchData.
    return await fetchData(`/projects/${projectId}/`, RequestMethod.GET)
}

export async function updateProjectRequest(projectId: string, updates: Partial<ProjectUpdate>): Promise<Project> {
    console.debug(`Updating project with ID: ${projectId}`, updates)

    // Check if all fields are empty.
    if (Object.keys(updates).length === 0) {
        console.warn('No updates provided for project.')
        throw new APIErrorResponse('No updates provided for project.', 400)
    }

    // Validate input.
    if (!projectId) {
        throw new APIErrorResponse('Project ID is required for updating.', 400)
    }
    if (updates.name !== undefined) {
        updates.name = validateProjectName(updates.name)
    }
    if (updates.password !== undefined) {
        updates.password = validateProjectPassword(updates.password)
    }

    // Request project update.
    return await fetchData(`/projects/${projectId}/`, RequestMethod.PUT, undefined, updates)
}

export async function deleteProjectRequest(projectId: string): Promise<void> {
    console.debug(`Deleting project with ID: ${projectId}`)

    // Validate input.
    if (!projectId) {
        throw new APIErrorResponse('Project ID is required for deletion.', 400)
    }

    // Cookie is sent automatically; no manual Authorization header needed.
    await fetchData(`/projects/${projectId}/`, RequestMethod.DELETE)
    console.debug(`Project ${projectId} deleted successfully.`)
}
