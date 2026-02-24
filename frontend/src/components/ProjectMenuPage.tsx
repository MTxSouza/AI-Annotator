import { useState, useEffect, JSX } from 'react'
import { fetchData, RequestMethod } from '../scripts/common'
import { Project, triggerProjectCreation, ProjectTask, deleteProjectRequest } from '../scripts/ProjectMenuPage'
import { PopupOverlay } from '../components/PopupOverlay'

import '../styles/ProjectMenuPage.css'

function LoadCreateProjectCard(): JSX.Element {
    return <div className="load-create-project-card-component"></div>
}

function CreateProjectCard({ createProjectPopup }: { createProjectPopup: () => void }): JSX.Element {
    return <div className="create-project-card-component" onClick={createProjectPopup}></div>
}

function ProjectCard({
    project,
    confirmProjectDeletion,
}: {
    project: Project
    confirmProjectDeletion: () => void
}): JSX.Element {
    return (
        <div className="project-card-component" project-id={project._id}>
            <div>
                <button onClick={confirmProjectDeletion}>
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        height="24px"
                        viewBox="0 -960 960 960"
                        width="24px"
                        fill="#FFFFFF"
                    >
                        <path d="M280-120q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm400-600H280v520h400v-520ZM360-280h80v-360h-80v360Zm160 0h80v-360h-80v360ZM280-720v520-520Z" />
                    </svg>
                </button>
            </div>
            <h3 title={project.name}>{project.name}</h3>
        </div>
    )
}

function LoadProjectMenuComponent(): JSX.Element {
    return (
        <div className="main-page-component">
            <LoadCreateProjectCard />
        </div>
    )
}

function ProjectMenuComponent({
    projects,
    onProjectDelete,
}: {
    projects: Project[]
    onProjectDelete: (deletedProjectId: string) => void
}): JSX.Element {
    console.info(`Number of projects fetched: ${projects.length}`)

    // Set up popup states.
    const [createProjectPopup, setCreateProjectPopup] = useState(false)
    const [projectToDelete, setProjectToDelete] = useState<string | null>(null)

    return (
        <div className="main-page-component">
            <CreateProjectCard createProjectPopup={() => setCreateProjectPopup(true)} />

            {projects.map((project) => (
                <ProjectCard
                    key={project._id}
                    project={project}
                    confirmProjectDeletion={() => setProjectToDelete(project._id)}
                />
            ))}

            {createProjectPopup && <CreateProjectPopup closePopup={() => setCreateProjectPopup(false)} />}

            {projectToDelete && (
                <ConfirmProjectDeletionPopup
                    projectId={projectToDelete}
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

function CreateProjectPopup({ closePopup }: { closePopup: () => void }): JSX.Element {
    console.info('Opening create project popup...')

    // Set up options to be displayed.
    const projectTasks = Object.values(ProjectTask)

    const component = (
        <div className="create-project-popup-component" onClick={(event) => event.stopPropagation()}>
            <div>
                <h1>Create Project</h1>
                <button onClick={closePopup}>
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        height="24px"
                        viewBox="0 -960 960 960"
                        width="24px"
                        fill="#FFFFFF"
                    >
                        <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z" />
                    </svg>
                </button>
            </div>
            <input id="create-project-name-input" type="text" maxLength={32} placeholder="Project Name" />
            <select name="create-project-task" id="create-project-task-input">
                {projectTasks.map((task) => (
                    <option key={task} value={task}>
                        {task}
                    </option>
                ))}
            </select>
            <button id="create-project-confirm-button" onClick={triggerProjectCreation}>
                Create
            </button>
        </div>
    )
    return <PopupOverlay children={component} />
}

function ConfirmProjectDeletionPopup({
    projectId,
    closePopup,
    refreshProjects,
}: {
    projectId: string
    closePopup: () => void
    refreshProjects: () => void
}): JSX.Element {
    console.info('Opening confirm project deletion popup...')

    // Delete project function.
    async function deleteProject(projectId: string) {
        try {
            await deleteProjectRequest(projectId)
            refreshProjects()
        } catch (error) {
            console.error('Error deleting project:', error)
        }
    }

    const component = (
        <div className="confirm-project-deletion-popup-component" onClick={(event) => event.stopPropagation()}>
            <h4>Are you sure you want to delete this project?</h4>
            <div>
                <button onClick={() => deleteProject(projectId)}>Yes</button>
                <button onClick={closePopup}>No</button>
            </div>
        </div>
    )
    return <PopupOverlay children={component} />
}

export function ProjectMenuPage(): JSX.Element {
    // Set states to manage the projects.
    const [projects, setProjects] = useState<Project[]>([])
    const [isLoading, setIsLoading] = useState(true)

    // Handle deleted project by refreshing the project list.
    const refreshProjects = (deletedProjectId: string) => {
        console.info(`Refreshing projects after deletion of project with ID: ${deletedProjectId}`)
        setProjects((prevProjects) => prevProjects.filter((project) => project._id !== deletedProjectId))
    }

    // Fetch projects.
    useEffect(() => {
        async function getProjects() {
            try {
                console.info('Featching projects from backend...')
                const responseData = await fetchData('/projects/', RequestMethod.GET)
                setProjects(responseData)
            } catch (error) {
                console.error('Error fetching projects:', error)
            }
            setIsLoading(false)
        }
        getProjects()
    }, [])

    // Display loading screen while fetching projects.
    if (isLoading) {
        return <LoadProjectMenuComponent />
    }

    return <ProjectMenuComponent projects={projects} onProjectDelete={refreshProjects} />
}
