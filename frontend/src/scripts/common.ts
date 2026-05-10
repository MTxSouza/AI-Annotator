import { NavigateFunction } from 'react-router-dom'
import { Task } from '../scripts/projects'

// Environment variables.
const VITE_API_PORT = import.meta.env.VITE_API_PORT

// Global variables.
export const API_BASE_URL = `http://localhost:${VITE_API_PORT}/api/v1`
export const PROJECT_MENU_URL = '/'
export const PROJECT_DATASET_URL = '/:projectId'
export const PROJECT_ANALYTICS_URL = '/:projectId/analytics'
export const PROJECT_SETTINGS_URL = '/:projectId/settings'

// Structures.
export enum RequestMethod {
    GET = 'GET',
    POST = 'POST',
    PUT = 'PUT',
    DELETE = 'DELETE',
}

export class APIErrorResponse extends Error {
    status_code: number

    constructor(message: string, status_code: number) {
        super(message)
        this.status_code = status_code
        this.name = 'APIErrorResponse'
    }
}

// Functions.
export function redirectTo(url: string, navigate: NavigateFunction): void {
    console.info(`Redirecting to ${url}...`)
    navigate(url)
}

async function tryRefreshToken(): Promise<boolean> {
    try {
        const response = await fetch(new URL('/auth/refresh', API_BASE_URL).toString(), {
            method: 'POST',
            credentials: 'include',
        })
        return response.ok
    } catch {
        return false
    }
}

async function parseErrorResponse(response: Response): Promise<string> {
    const errorText = await response.text()
    try {
        const errorJson = JSON.parse(errorText)
        if (errorJson.detail && errorJson.detail instanceof Array && errorJson.detail.length > 0) {
            return errorJson.detail[0].msg
        }
        if (errorJson.detail && typeof errorJson.detail === 'string') {
            return errorJson.detail
        }
    } catch {
        console.warn('Failed to parse error response as JSON.')
    }
    return errorText || 'Unknown error occurred.'
}

export async function fetchData(
    url: string,
    method: RequestMethod,
    params?: any,
    body?: any,
    headers?: Record<string, string>,
): Promise<any | void> {
    // Set up the full URL.
    let fullUrl: string = new URL(url, API_BASE_URL).toString()
    console.debug(
        `Fetching data from ${fullUrl} with method ${method}, params: ${JSON.stringify(params)}, body: ${JSON.stringify(body)}, headers: ${JSON.stringify(headers)}`,
    )

    // Add params to the URL if provided.
    if (params) {
        const queryParams = new URLSearchParams(params).toString()
        fullUrl += `?${queryParams}`
    }

    // Set up the request options.
    const options: RequestInit = {
        method: method,
        credentials: 'include',
    }

    // Add headers.
    const defaultHeaders: Record<string, string> = {}
    if (headers) {
        Object.assign(defaultHeaders, headers)
    }

    // Add body if provided.
    if (body) {
        console.trace('Adding body to the request.')
        if (body instanceof FormData) {
            // Let the browser set Content-Type with the correct multipart boundary.
            console.trace('Using FormData for body. Letting browser set Content-Type header.')
            options.body = body
        } else if (defaultHeaders['Content-Type'] === 'application/x-www-form-urlencoded') {
            console.trace('Encoding body as URL-encoded form data.')
            options.body = new URLSearchParams(body).toString()
        } else {
            if (!defaultHeaders['Content-Type']) {
                defaultHeaders['Content-Type'] = 'application/json'
            }
            console.trace('Encoding body as JSON.')
            options.body = JSON.stringify(body)
        }
    } else if (!defaultHeaders['Content-Type']) {
        defaultHeaders['Content-Type'] = 'application/json'
    }
    options.headers = defaultHeaders

    console.debug(`Final options for fetch: ${JSON.stringify(options)}`)
    let response = await fetch(fullUrl, options)

    // On 401, attempt a silent token refresh and retry once.
    if (response.status === 401 && !url.includes('auth/')) {
        console.debug('Access token expired. Attempting silent refresh...')
        const refreshed = await tryRefreshToken()
        if (refreshed) {
            console.debug('Token refreshed. Retrying original request...')
            response = await fetch(fullUrl, options)
        }
    }

    if (!response.ok) {
        const errorMessage = await parseErrorResponse(response)
        console.error('HTTP error:', response.status, 'Response:', errorMessage)
        throw new APIErrorResponse(errorMessage, response.status)
    }

    console.debug(`Fetched data from ${fullUrl} successfully.`)

    if (response.status === 204) {
        return
    }
    return await response.json()
}

export async function getProjectsRequest(): Promise<any> {
    console.debug('Fetching projects from the backend...')
    return await fetchData('/projects/', RequestMethod.GET)
}

export async function getTasksRequest(): Promise<Task[]> {
    console.debug('Fetching tasks from the backend...')
    return await fetchData('/tasks/', RequestMethod.GET)
}
