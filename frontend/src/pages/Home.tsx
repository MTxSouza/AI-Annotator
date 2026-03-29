/*
Main home page for project management.
*/
import { JSX } from 'react'
import { useParams } from 'react-router-dom'

// Components.
export function Home(): JSX.Element {
    // Get the project ID from the URL parameters.
    const { projectId } = useParams<{ projectId: string }>()

    return (
        <div className="main-component-page">
            <p>Project ID: {projectId}</p>
        </div>
    )
}
