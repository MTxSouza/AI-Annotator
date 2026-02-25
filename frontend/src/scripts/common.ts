// Global variables.
export const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

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
export async function fetchData(url: string, method: RequestMethod, params?: any, body?: any): Promise<any | void> {
    // Set up the full URL.
    let fullUrl: string = new URL(url, API_BASE_URL).toString()
    console.debug(
        `Fetching data from ${fullUrl} with method ${method}, params: ${JSON.stringify(params)}, body: ${JSON.stringify(body)}`,
    )

    // Set up the request options.
    const options: RequestInit = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
    }

    // Add body if provided.
    if (body) {
        options.body = JSON.stringify(body)
    }

    // Add params to the URL if provided.
    if (params) {
        const queryParams = new URLSearchParams(params).toString()
        fullUrl += `?${queryParams}`
    }

    // Request data from the API.
    const response = await fetch(fullUrl, options)
    if (!response.ok) {
        // Get status and message from the response.
        const errorText = await response.text()
        const errorStatus = response.status
        let errorMessage = errorText
        try {
            const errorJson = JSON.parse(errorText)
            errorMessage = errorJson.detail || errorText
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
