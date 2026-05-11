/*
Main component to store all sub components for the project analysis page.
*/
import { JSX } from 'react'
import { Project } from '../scripts/projects'
import { useOutletContext } from 'react-router-dom'

import '../styles/pages/AnalysisLayout.css'

// Components.
export function AnalysisLayout(): JSX.Element {
    // Get the project data from the outlet context.
    const [project, setProject] = useOutletContext<[Project, React.Dispatch<React.SetStateAction<Project>>]>()

    return <div className="project-analysis-layout-component"></div>
}
