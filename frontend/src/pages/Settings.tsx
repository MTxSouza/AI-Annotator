/*
Main settings page for project management.
*/
import { useState, useEffect, JSX } from 'react'
import { Project, ProjectUpdate, updateProjectRequest } from '../scripts/projects'
import { useNavigate, useOutletContext } from 'react-router-dom'
import { SimpleInput } from '../components/input/SimpleInput'
import { useDialog } from '../components/dialog/Dialog'
import { Button } from '../components/button/Button'
import { ButtonType } from '../scripts/Button'
import { ConfirmProjectDeletionPopup } from '../components/popup/ConfirmProjectDeletionPopup'
import { PROJECT_MENU_URL, APIErrorResponse, redirectTo } from '../scripts/common'

import '../styles/pages/Settings.css'

// Components.
export function Settings(): JSX.Element {
    // Set up dialog.
    const { showDialog } = useDialog()

    // Set page navigator.
    const navigate = useNavigate()

    // Get the project data from the outlet context.
    const project = useOutletContext<Project>()

    // Set up states.
    const [currentProjectName, setCurrentProjectName] = useState<string>(project.name)
    const [newProjectName, setNewProjectName] = useState<string>(currentProjectName)
    const [isProjectInfoChanged, setIsProjectInfoChanged] = useState<boolean>(false)
    const [deleteProject, setDeleteProject] = useState<boolean>(false)

    useEffect(() => {
        setIsProjectInfoChanged(currentProjectName !== newProjectName)
    }, [newProjectName])

    async function saveProjectChanges() {
        const updates: Partial<ProjectUpdate> = {}
        updates.name = newProjectName
        try {
            await updateProjectRequest(project._id, updates)
        } catch (error) {
            if (error instanceof APIErrorResponse) {
                console.error('Error updating project:', error)
                showDialog('error', error.message, error.status_code)
            } else {
                console.error('Unexpected error updating project:', error)
                showDialog('error', 'Failed to update project. Please try again later.', 500)
            }
            return
        }

        // Update UI.
        console.info('Project updated successfully.')
        showDialog('info', 'Project updated successfully!', 201)
        setCurrentProjectName(newProjectName)
        setIsProjectInfoChanged(false)
    }

    return (
        <div id="main-page" className="project-settings-component">
            <h2 id="project-settings-title-component">Settings</h2>
            <div className="project-name-settings-container">
                <label htmlFor="project-name-settings">Project Name</label>
                <SimpleInput
                    id="project-name-settings"
                    placeholder={currentProjectName}
                    value={currentProjectName}
                    onChangeEvent={(event) => setNewProjectName(event.target.value)}
                />
            </div>
            <div className="project-password-settings-container">
                <Button
                    id="set-project-password-btn"
                    value="Set Password"
                    buttonType={ButtonType.TERTIARY}
                    onClickEvent={() => console.log('Set Password clicked')}
                />
            </div>
            <div className="project-type-info-container">
                <p>Extra project information</p>
                <div className="project-type-info-block-container">
                    <div className="project-type-info-block-sub-container">
                        <label htmlFor="project-task-name">Task</label>
                        <span id="project-task-name">{project.task}</span>
                    </div>
                    <div className="project-type-info-block-sub-container">
                        <label htmlFor="is-private-project">Private</label>
                        <span id="is-private-project">{project.is_private ? 'Yes' : 'No'}</span>
                    </div>
                </div>
            </div>
            <div className="project-bottom-buttons-container">
                <Button
                    id="project-delete-btn"
                    value="delete project"
                    buttonType={ButtonType.TERTIARY}
                    onClickEvent={() => setDeleteProject(true)}
                />
                <Button
                    id="project-settings-save-btn"
                    value="Save"
                    buttonType={ButtonType.PRIMARY}
                    onClickEvent={saveProjectChanges}
                    disabled={!isProjectInfoChanged}
                />
            </div>

            {deleteProject && (
                <ConfirmProjectDeletionPopup
                    projectId={project._id}
                    isPrivate={project.is_private}
                    closePopup={() => setDeleteProject(false)}
                    refreshProjects={() => redirectTo(PROJECT_MENU_URL, navigate)}
                />
            )}
        </div>
    )
}
