// Global variables.
export const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'
export const PROJECT_MENU_URL = '/'
export const PROJECT_HOME_URL = '/:projectId'

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
        this.message = message
        this.status_code = status_code
    }
}

// Functions.
export async function fetchData(
    url: string,
    method: RequestMethod,
    params?: any,
    body?: any,
    headers?: any,
    contentType: string = 'application/json',
): Promise<any | void> {
    // Set up the full URL.
    let fullUrl: string = new URL(url, API_BASE_URL).toString()
    console.debug(
        `Fetching data from ${fullUrl} with method ${method}, params: ${JSON.stringify(params)}, body: ${JSON.stringify(body)}, headers: ${JSON.stringify(headers)}, Content-Type: ${contentType}`,
    )

    // Set up the request options.
    const options: RequestInit = {
        method: method,
        headers: {
            'Content-Type': contentType,
            ...headers,
        },
    }

    // Add body if provided.
    if (body) {
        console.trace('Adding body to the request.')
        if (contentType === 'application/x-www-form-urlencoded') {
            console.trace('Encoding body as URL-encoded form data.')
            options.body = new URLSearchParams(body).toString()
        } else {
            console.trace('Encoding body as JSON.')
            options.body = JSON.stringify(body)
        }
    }

    // Add params to the URL if provided.
    if (params) {
        console.trace('Adding query parameters to the URL.')
        const queryParams = new URLSearchParams(params).toString()
        fullUrl += `?${queryParams}`
    }

    // Request data from the API.
    console.debug(`Final options for fetch: ${JSON.stringify(options)}`)
    const response = await fetch(fullUrl, options)
    if (!response.ok) {
        // Get status and message from the response.
        const errorStatus = response.status
        const errorText = await response.text()
        let errorMessage = errorText
        try {
            const errorJson = JSON.parse(errorText)
            if (errorJson.detail && errorJson.detail instanceof Array && errorJson.detail.length > 0) {
                errorMessage = errorJson.detail[0].msg
            } else if (errorJson.detail && typeof errorJson.detail === 'string') {
                errorMessage = errorJson.detail
            }
        } catch (e) {
            console.warn('Failed to parse error response as JSON:', e)
        }
        errorMessage = errorMessage || errorText || 'Unknown error occurred.'

        console.error('HTTP error:', response.status, 'Response:', errorMessage)
        throw new APIErrorResponse(errorMessage, errorStatus)
    }
    console.debug(`Fetched data from ${fullUrl} successfully.`)

    if (response.status === 204) {
        return
    }
    return await response.json()
}
