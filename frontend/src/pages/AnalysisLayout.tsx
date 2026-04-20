/*
Main component to store all sub components for the project analysis page.
*/
import { JSX } from 'react'
import { Project } from '../scripts/projects'
import { useOutletContext } from 'react-router-dom'

import '../styles/AnalysisLayout.css'

// Components.
export function AnalysisLayout(): JSX.Element {
    // Get the project data from the outlet context.
    const project = useOutletContext<Project>()

    return <div className="project-analysis-layout-component"></div>
}
