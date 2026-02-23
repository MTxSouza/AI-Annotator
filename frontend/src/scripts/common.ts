// Global variables.
export const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// Structures.
export enum RequestMethod {
    GET = 'GET',
    POST = 'POST',
    PUT = 'PUT',
    DELETE = 'DELETE'
}

// Functions.
export async function fetchData(url: string, method: RequestMethod, params?: any, body?: any): Promise<any> {

    // Set up the full URL.
    let fullUrl: string = new URL(url, API_BASE_URL).toString();
    console.debug(`Fetching data from ${fullUrl} with method ${method}, params: ${JSON.stringify(params)}, body: ${JSON.stringify(body)}`);

    // Set up the request options.
    const options: RequestInit = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    // Add body if provided.
    if (body) {
        options.body = JSON.stringify(body);
    }

    // Add params to the URL if provided.
    if (params) {
        const queryParams = new URLSearchParams(params).toString();
        fullUrl += `?${queryParams}`;
    }

    // Request data from the API.
    const response = await fetch(fullUrl, options);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    console.debug(`Fetched data from ${fullUrl} successfully.`);
    return await response.json();
};
