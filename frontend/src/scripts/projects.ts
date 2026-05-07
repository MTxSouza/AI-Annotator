import { fetchData, RequestMethod, APIErrorResponse } from '../scripts/common'

// Constants.
const ACCESS_TOKEN_KEY = 'current_project_access_token'

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
    is_private: boolean
    created_at: string
    updated_at: string
}

// Functions.
function validateProjectName(name: string): string {
    // Trim whitespace from the name.
    name = name.trim()

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

    return name
}

export async function createProjectRequest(
    name: string,
    task: string,
    password: string | null = null,
): Promise<Project> {
    // Check input validity.
    console.debug(`Creating project with name: ${name}, task: ${task}`)

    // Validate fields.
    name = validateProjectName(name)

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

export async function authenticateProjectRequest(projectId: string, password: string): Promise<void> {
    console.debug(`Authenticating project with ID: ${projectId}`)

    // Check if project ID and password are provided.
    if (!projectId) {
        console.error('Project ID is required for authentication.')
        throw new APIErrorResponse('Project ID is required for authentication.', 400)
    }
    if (!password) {
        console.error('Password is required for authentication.')
        throw new APIErrorResponse('Password is required for authentication.', 400)
    }

    // Authenticate to fetch the access token.
    const tokenResponse = await fetchData(
        '/auth/token',
        RequestMethod.POST,
        undefined,
        {
            username: projectId,
            password: password,
        },
        { 'Content-Type': 'application/x-www-form-urlencoded' },
    )
    localStorage.setItem(ACCESS_TOKEN_KEY, tokenResponse.access_token)
    console.debug('Project authenticated successfully. Access token stored.')
}

export function getCurrentProjectAccessToken(): string | null {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY)
    console.debug('Retrieved current project access token')
    if (token === null) {
        console.warn('No current project access token found.')
    }
    return token
}

export function removeCurrentProjectAccessToken(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    console.debug('Removed current project access token.')
}

export async function getProjectRequest(projectId: string, password: string | null = null): Promise<Project> {
    console.debug(`Fetching project with ID: ${projectId}`)

    // Check if project ID is provided.
    if (!projectId) {
        console.error('Project ID is required for fetching.')
        throw new APIErrorResponse('Project ID is required for fetching.', 400)
    }

    // Check if password is provided.
    if (password === null) {
        console.debug('No password provided. Trying to fetch project without password...')
        return await fetchData(`/projects/${projectId}/`, RequestMethod.GET)
    }

    // Check current access token.
    let accessToken = getCurrentProjectAccessToken()
    if (accessToken !== password) {
        // Authenticate to fetch the access token.
        await authenticateProjectRequest(projectId, password)
        accessToken = getCurrentProjectAccessToken()
    }

    // Authenticate with password and fetch project.
    console.debug('Password provided. Trying to fetch project with authentication...')
    return await fetchData(`/projects/${projectId}/`, RequestMethod.GET, undefined, undefined, {
        Authorization: `Bearer ${accessToken}`,
    })
}

export async function deleteProjectRequest(projectId: string): Promise<void> {
    console.debug(`Deleting project with ID: ${projectId}`)
    if (!projectId) {
        console.error('Project ID is required for deletion.')
        throw new APIErrorResponse('Project ID is required for deletion.', 400)
    }

    // Check if access token exists for the project. If it does, include it in the request to allow deletion of private projects.
    const accessToken = getCurrentProjectAccessToken()
    let headers = undefined
    if (accessToken) {
        headers = {
            Authorization: `Bearer ${accessToken}`,
        }
    }

    await fetchData(`/projects/${projectId}/`, RequestMethod.DELETE, undefined, undefined, headers)
    console.debug(`Project with ID: ${projectId} deleted successfully.`)

    // Remove access token from local storage after project deletion.
    removeCurrentProjectAccessToken()
}
