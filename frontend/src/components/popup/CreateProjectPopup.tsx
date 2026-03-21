import { useState, useEffect, JSX } from 'react'
import { PopupOverlay } from '../PopupOverlay'
import { useErrorDialog } from '../ErrorDialog'
import { Project, Task, createProjectRequest } from '../../scripts/projects'
import { APIErrorResponse, fetchData, RequestMethod } from '../../scripts/common'
import { ProjectPassword } from '../input/ProjectPassword'
import { SimpleConfirmButton } from '../button/SimpleConfirmButton'
import { Popup } from './Popup'

import '../../styles/popup/CreateProjectPopup.css'

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

    const children = (
        <div className="create-project-popup-component">
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
            <ProjectPassword isOpcional={true} setProjectPassword={setProjectPassword} />
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
            <SimpleConfirmButton
                message={'Create'}
                onConfirm={async () => {
                    try {
                        const project = await createProjectRequest(projectName, selectedTask, projectPassword)
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
            />
        </div>
    )
    const component = <Popup children={children} />

    return <PopupOverlay children={component} />
}
