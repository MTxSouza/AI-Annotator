/*
Main dataset page for project management.
*/
import { JSX } from 'react'
import { Project } from '../scripts/projects'
import { useOutletContext } from 'react-router-dom'

// Components.
export function Dataset(): JSX.Element {
    // Get the project data from the outlet context.
    const project = useOutletContext<Project>()

    return (
        <div className="main-page-component">
            <p>Project ID: {project._id}</p>
        </div>
    )
}
