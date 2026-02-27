import { useState, useEffect, JSX } from 'react'
import { APIErrorResponse, fetchData, RequestMethod } from '../scripts/common'
import { Project, createProjectRequest, Task, deleteProjectRequest } from '../scripts/ProjectMenuPage'
import { PopupOverlay } from '../components/PopupOverlay'
import { useErrorDialog } from '../components/ErrorDialog'

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

            {createProjectPopup && (
                <CreateProjectPopup closePopup={() => setCreateProjectPopup(false)} refreshProjects={onProjectInsert} />
            )}

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

function CreateProjectPopup({
    closePopup,
    refreshProjects,
}: {
    closePopup: () => void
    refreshProjects: (project: Project) => void
}): JSX.Element {
    console.info('Opening create project popup...')

    // Set up error dialog.
    const { showErrorDialog } = useErrorDialog()

    // Request project tasks from backend.
    const [tasks, setTasks] = useState<Task[]>([])
    const [projectName, setProjectName] = useState<string>('')
    const [selectedTask, setSelectedTask] = useState<string>('')
    const [projectPassword, setProjectPassword] = useState<string | null>(null)
    const [hidePassword, setHidePassword] = useState<boolean>(true)
    useEffect(() => {
        async function getTasks() {
            const responseData = await fetchData('/tasks/', RequestMethod.GET)
            setTasks(responseData)
            if (responseData.length > 0) setSelectedTask(responseData[0].name)
        }
        getTasks()
    }, [])

    // Set up state to manage selected project task.
    function handleTaskChange(event: React.ChangeEvent<HTMLSelectElement>): void {
        setSelectedTask(event.target.value)
    }
    const currentTaskDescription = tasks.find((task) => task.name === selectedTask)?.description || ''
    const currentTaskFileFormat = tasks.find((task) => task.name === selectedTask)?.file_format_list || []

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
            <input
                id="create-project-name-input"
                type="text"
                maxLength={32}
                placeholder="Project Name"
                onChange={(event) => setProjectName(event.target.value)}
            />
            <div className="create-project-password-input-container">
                <input
                    id="create-project-password-input"
                    type={hidePassword ? 'password' : 'text'}
                    placeholder="Password (optional)"
                    onChange={(event) => setProjectPassword(event.target.value || null)}
                />
                <label
                    id="create-project-password-visibility-label"
                    htmlFor="change-create-project-password-visibilty-btn"
                >
                    <input
                        type="checkbox"
                        id="change-create-project-password-visibilty-btn"
                        checked={hidePassword}
                        onChange={() => setHidePassword(!hidePassword)}
                    />
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        height="24px"
                        viewBox="0 -960 960 960"
                        width="24px"
                        fill="#FFFFFF"
                    >
                        <path d="M240-80q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640h40v-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240Zm0-80h480v-400H240v400Zm296.5-143.5Q560-327 560-360t-23.5-56.5Q513-440 480-440t-56.5 23.5Q400-393 400-360t23.5 56.5Q447-280 480-280t56.5-23.5ZM360-640h240v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85v80ZM240-160v-400 400Z" />
                    </svg>
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        height="24px"
                        viewBox="0 -960 960 960"
                        width="24px"
                        fill="#FFFFFF"
                    >
                        <path d="M240-640h360v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85h-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640Zm0 480h480v-400H240v400Zm296.5-143.5Q560-327 560-360t-23.5-56.5Q513-440 480-440t-56.5 23.5Q400-393 400-360t23.5 56.5Q447-280 480-280t56.5-23.5ZM240-160v-400 400Z" />
                    </svg>
                </label>
            </div>
            <div className="create-project-task-input-container">
                <select
                    name="create-project-task"
                    id="create-project-task-input"
                    value={selectedTask || ''}
                    onChange={handleTaskChange}
                >
                    {tasks.map((task) => (
                        <option key={task.name} value={task.name}>
                            {task.name}
                        </option>
                    ))}
                </select>
                <p id="create-project-task-description">{currentTaskDescription}</p>
                <div className="create-project-task-file-format-container">
                    <p>Allowed file formats:</p>
                    <div>
                        {currentTaskFileFormat &&
                            currentTaskFileFormat.map((fileFormat: string) => <p key={fileFormat}>{fileFormat}</p>)}
                    </div>
                </div>
            </div>
            <button
                id="create-project-confirm-button"
                onClick={async () => {
                    try {
                        const project = await createProjectRequest(projectName, selectedTask, null) // No way to delete it from UI, so we set it to null if it's empty.
                        if (project) refreshProjects(project)
                        closePopup()
                    } catch (error) {
                        if (error instanceof APIErrorResponse) {
                            console.error('Error creating project:', error)
                            showErrorDialog(error.message, error.status_code)
                        } else if (error instanceof Error) {
                            console.error('Error creating project:', error)
                            showErrorDialog(error.message, 500)
                        } else {
                            console.error('Unexpected error creating project:', error)
                            showErrorDialog('An unexpected error occurred while creating the project.', 500)
                        }
                    }
                }}
            >
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

    // Set up error dialog.
    const { showErrorDialog } = useErrorDialog()

    // Delete project function.
    async function deleteProject(projectId: string) {
        try {
            await deleteProjectRequest(projectId)
            refreshProjects()
        } catch (error) {
            if (error instanceof APIErrorResponse) {
                console.error('Error deleting project:', error)
                showErrorDialog(error.message, error.status_code)
            } else {
                console.error('Unexpected error deleting project:', error)
                showErrorDialog('An unexpected error occurred while deleting the project.', 500)
            }
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
