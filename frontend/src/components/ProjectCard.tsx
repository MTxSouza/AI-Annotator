import { JSX } from 'react'
import { Project } from '../scripts/projects'
import { redirectTo } from '../scripts/common'
import { useNavigate } from 'react-router-dom'

import '../styles/ProjectCard.css'

export function LoadCreateProjectCard(): JSX.Element {
    return <div className="load-create-project-card-component"></div>
}

export function CreateProjectCard({ createProjectPopup }: { createProjectPopup: () => void }): JSX.Element {
    return <div className="create-project-card-component" onClick={createProjectPopup}></div>
}

export function ProjectCard({
    project,
    confirmProjectDeletion,
    authenticatedProject,
}: {
    project: Project
    confirmProjectDeletion: () => void
    authenticatedProject: () => void
}): JSX.Element {
    // Set page navigator.
    const navigate = useNavigate()
    const handleCardClick = () => {
        if (project.is_private) {
            authenticatedProject()
        } else {
            redirectTo(`/${project._id}`, navigate)
        }
    }

    // Set delete button click handler.
    const handleDeleteBtnClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.stopPropagation() // Prevent card click event from firing.
        confirmProjectDeletion()
    }

    return (
        <div className="project-card-component" onClick={handleCardClick}>
            <div>
                {project.is_private && (
                    <label>
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            height="24px"
                            viewBox="0 -960 960 960"
                            width="24px"
                            fill="#FFFFFF"
                        >
                            <path d="M240-80q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640h40v-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240Zm0-80h480v-400H240v400Zm296.5-143.5Q560-327 560-360t-23.5-56.5Q513-440 480-440t-56.5 23.5Q400-393 400-360t23.5 56.5Q447-280 480-280t56.5-23.5ZM360-640h240v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85v80ZM240-160v-400 400Z" />
                        </svg>
                    </label>
                )}
                <button onClick={handleDeleteBtnClick}>
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
