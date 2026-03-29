/*
Main component to store all sub components for the project home page.
*/
import { JSX } from 'react'
import { Outlet } from 'react-router-dom'
import { ProjectSideBar } from '../components/ProjectSideBar'

import '../styles/ProjectHomeLayout.css'

// Components.
export function ProjectHomeLayout(): JSX.Element {
    return (
        <div className="project-home-layout-component">
            <ProjectSideBar />
            <Outlet />
        </div>
    )
}
