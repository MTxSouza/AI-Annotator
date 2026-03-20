import { Project } from '../scripts/projects'
import { useState, useEffect, JSX } from 'react'
import { useErrorDialog } from '../components/ErrorDialog'
import { CreateProjectPopup } from '../components/CreateProjectPopup'
import { APIErrorResponse, fetchData, RequestMethod } from '../scripts/common'
import { ConfirmProjectDeletionPopup } from '../components/ConfirmProjectDeleteionPopup'
import { CreateProjectCard, LoadCreateProjectCard, ProjectCard } from '../components/ProjectCard'

import '../styles/ProjectMenu.css'

function LoadProjectMenuComponent(): JSX.Element {
    return (
        <div className="main-page-component">
            <LoadCreateProjectCard />
        </div>
    )
}

function ProjectMenuComponent({
    projects,
    onProjectInsert,
    onProjectDelete,
}: {
    projects: Project[]
    onProjectInsert: (newProject: Project) => void
    onProjectDelete: (deletedProjectId: string) => void
}): JSX.Element {
    console.info(`Number of projects fetched: ${projects.length}`)

    // Set up popup states.
    const [createProjectPopup, setCreateProjectPopup] = useState(false)
    const [projectToDelete, setProjectToDelete] = useState<string | null>(null)
    const [isProjectPrivate, setIsProjectPrivate] = useState(false)

    return (
        <div className="main-page-component">
            <CreateProjectCard createProjectPopup={() => setCreateProjectPopup(true)} />

            {projects.map((project) => (
                <ProjectCard
                    key={project._id}
                    project={project}
                    confirmProjectDeletion={() => {
                        setProjectToDelete(project._id)
                        setIsProjectPrivate(project.is_private)
                    }}
                />
            ))}

            {createProjectPopup && (
                <CreateProjectPopup closePopup={() => setCreateProjectPopup(false)} refreshProjects={onProjectInsert} />
            )}

            {projectToDelete && (
                <ConfirmProjectDeletionPopup
                    projectId={projectToDelete}
                    isPrivate={isProjectPrivate}
                    closePopup={() => setProjectToDelete(null)}
                    refreshProjects={() => {
                        onProjectDelete(projectToDelete)
                        setProjectToDelete(null)
                    }}
                />
            )}
        </div>
    )
}

export function ProjectMenu(): JSX.Element {
    // Set up error dialog.
    const { showErrorDialog } = useErrorDialog()

    // Set states to manage the projects.
    const [projects, setProjects] = useState<Project[]>([])
    const [isLoading, setIsLoading] = useState(true)

    // Handle deleted project by refreshing the project list.
    const insertProject = (newProject: Project) => {
        console.info(`Refreshing projects after creation of project with ID: ${newProject._id}`)
        setProjects((prevProjects) => [...prevProjects, newProject])
    }
    const deleteProject = (deletedProjectId: string) => {
        console.info(`Refreshing projects after deletion of project with ID: ${deletedProjectId}`)
        setProjects((prevProjects) => prevProjects.filter((project) => project._id !== deletedProjectId))
    }

    // Fetch projects.
    useEffect(() => {
        async function getProjects() {
            try {
                console.info('Fetching projects from backend...')
                const responseData = await fetchData('/projects/', RequestMethod.GET)
                setProjects(responseData)
            } catch (error) {
                if (error instanceof APIErrorResponse) {
                    console.error('Error fetching projects:', error)
                    showErrorDialog(error.message, error.status_code)
                } else {
                    console.error('Unexpected error fetching projects:', error)
                    showErrorDialog('An unexpected error occurred while fetching projects.', 500)
                }
            }
            setIsLoading(false)
        }
        getProjects()
    }, [])

    // Display loading screen while fetching projects.
    if (isLoading) {
        return <LoadProjectMenuComponent />
    }

    return <ProjectMenuComponent projects={projects} onProjectInsert={insertProject} onProjectDelete={deleteProject} />
}
