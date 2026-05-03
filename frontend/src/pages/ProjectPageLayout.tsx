/*
Main component to store all sub components for the project home page.
*/
import { JSX, useState, useEffect } from 'react'
import { Outlet, useParams } from 'react-router-dom'
import { Project, getCurrentProjectAccessToken, getProjectRequest } from '../scripts/projects'
import { useDialog } from '../components/dialog/Dialog'
import { APIErrorResponse } from '../scripts/common'
import { ProjectSideBar } from '../components/ProjectSideBar'

import '../styles/pages/ProjectHomeLayout.css'

// Components.
export function ProjectPageLayout(): JSX.Element {
    // Set up dialog.
    const { showDialog } = useDialog()

    // Set up parameters and state.
    const { projectId } = useParams<{ projectId: string }>()
    const [projectData, setProjectData] = useState<Project | null>(null)

    // Request project data from the server when the component mounts.
    useEffect(() => {
        // Check if project ID is available.
        if (!projectId) return

        // Fetch project data from the server.
        const fetchProjectData = async () => {
            try {
                const accessToken = getCurrentProjectAccessToken()
                const fetchedData = await getProjectRequest(projectId, accessToken)
                setProjectData(fetchedData)
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
    }, [projectId])

    // Get the project ID from the URL parameters.
    if (!projectId) {
        console.error('Project ID not found in URL parameters.')
        return <div className="project-home-layout-component">Project ID not found in URL parameters.</div>
    }

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
