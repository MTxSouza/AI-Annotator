import { useState, useEffect, JSX } from 'react'
import { PopupOverlay } from '../components/PopupOverlay'
import { useErrorDialog } from '../components/ErrorDialog'
import { Project, Task, createProjectRequest } from '../scripts/projects'
import { APIErrorResponse, fetchData, RequestMethod } from '../scripts/common'

import '../styles/CreateProjectPopup.css'

export function CreateProjectPopup({
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
                        const project = await createProjectRequest(projectName, selectedTask, null) // No way to delete it from UI, so we set it to null.
                        if (project) refreshProjects(project)
                        closePopup()
                    } catch (error) {
                        if (error instanceof APIErrorResponse) {
                            console.error('Error creating project:', error)
                            showErrorDialog(error.message, error.status_code)
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
