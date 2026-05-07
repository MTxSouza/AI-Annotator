import { useState, useEffect, JSX } from 'react'
import { PopupOverlay } from '../PopupOverlay'
import { useDialog } from '../dialog/Dialog'
import { Project, Task, createProjectRequest } from '../../scripts/projects'
import { APIErrorResponse, getTasksRequest } from '../../scripts/common'
import { ProjectPasswordInput } from '../input/ProjectPasswordInput'
import { Button } from '../button/Button'
import { ButtonType } from '../../scripts/Button'
import { ProjectNameInput } from '../input/ProjectNameInput'
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

    // Set up dialog.
    const { showDialog } = useDialog()

    // Request project tasks from backend.
    const [tasks, setTasks] = useState<Task[]>([])
    const [projectName, setProjectName] = useState<string>('')
    const [selectedTask, setSelectedTask] = useState<string>('')
    const [projectPassword, setProjectPassword] = useState<string | null>(null)
    useEffect(() => {
        async function getTasks() {
            try {
                const responseData = await getTasksRequest()
                setTasks(responseData)
                if (responseData.length > 0) setSelectedTask(responseData[0].name)
            } catch (error) {
                if (error instanceof APIErrorResponse) {
                    console.error('Error fetching tasks:', error)
                    showDialog('error', error.message, error.status_code)
                } else {
                    console.error('Unexpected error fetching tasks:', error)
                    showDialog('error', 'An unexpected error occurred while fetching tasks.', 500)
                }
            }
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
            <ProjectNameInput onChangeEvent={(event) => setProjectName(event.target.value)} />
            <ProjectPasswordInput isOptional={true} setProjectPassword={setProjectPassword} />
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
            <Button
                id="create-project-btn-component"
                value="Create"
                buttonType={ButtonType.SECONDARY}
                onClickEvent={async () => {
                    try {
                        const project = await createProjectRequest(projectName, selectedTask, projectPassword)
                        if (project) refreshProjects(project)
                        closePopup()
                        showDialog('info', 'Project created successfully!', null)
                    } catch (error) {
                        if (error instanceof APIErrorResponse) {
                            console.error('Error creating project:', error)
                            showDialog('error', error.message, error.status_code)
                        } else {
                            console.error('Unexpected error creating project:', error)
                            showDialog('error', 'An unexpected error occurred while creating the project.', 500)
                        }
                    }
                }}
            />
        </div>
    )
    const component = <Popup children={children} />

    return <PopupOverlay children={component} />
}
