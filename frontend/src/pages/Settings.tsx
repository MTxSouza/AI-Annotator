/*
Main settings page for project management.
*/
import { JSX } from 'react'
import { Project } from '../scripts/projects'
import { useOutletContext } from 'react-router-dom'

// Components.
export function Settings(): JSX.Element {
    // Get the project data from the outlet context.
    const project = useOutletContext<Project>()

    return <div className="main-page-component"></div>
}
