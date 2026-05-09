import { JSX } from 'react'
import { Project } from '../scripts/projects'
import { redirectTo } from '../scripts/common'
import { useNavigate } from 'react-router-dom'

import Lock from '../icons/lock.svg?react'
import Trash from '../icons/trash.svg?react'

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
                        <Lock style={{ fill: 'var(--tertiary-text-color)' }} />
                    </label>
                )}
                <button onClick={handleDeleteBtnClick}>
                    <Trash />
                </button>
            </div>
            <h3 title={project.name}>{project.name}</h3>
        </div>
    )
}
