/*
Main component to store all sub components for the project home page.
*/
import { JSX, useState, useEffect } from 'react'
import { Outlet, useParams } from 'react-router-dom'
import { Project } from '../scripts/projects'
import { useDialog } from '../components/dialog/Dialog'
import { RequestMethod, fetchData, APIErrorResponse } from '../scripts/common'
import { ProjectSideBar } from '../components/ProjectSideBar'

import '../styles/ProjectHomeLayout.css'

// Components.
export function ProjectPageLayout(): JSX.Element {
    // Set up dialog.
    const { showDialog } = useDialog()

    // Get the project ID from the URL parameters.
    const { projectId } = useParams<{ projectId: string }>()
    if (!projectId) {
        console.error('Project ID not found in URL parameters.')
        return <div className="project-home-layout-component">Project ID not found in URL parameters.</div>
    }

    // Request project data from the server when the component mounts.
    const [projectData, setProjectData] = useState<Project | null>(null)
    useEffect(() => {
        // Fetch project data from the server.
        const fetchProjectData = async () => {
            try {
                const projectData = await fetchData(`/projects/${projectId}`, RequestMethod.GET)
                setProjectData(projectData)
            } catch (error) {
                if (error instanceof APIErrorResponse) {
                    console.error('Error fetching project data:', error)
                    showDialog('error', error.message, error.status_code)
                } else {
                    console.error('Unexpected error fetching project data:', error)
                    showDialog('error', 'An unexpected error occurred while fetching project data.', 500)
                }
            }
        }
        fetchProjectData()
    }, [])
    if (!projectData) {
        return <div className="project-home-layout-component">Loading project data...</div>
    }

    return (
        <div className="project-home-layout-component">
            <ProjectSideBar projectId={projectId} />
            <Outlet context={projectData} />
        </div>
    )
}
