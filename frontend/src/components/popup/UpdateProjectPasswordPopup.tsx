import { JSX, useState } from 'react'
import { APIErrorResponse } from '../../scripts/common'
import { PopupOverlay } from '../PopupOverlay'
import { useDialog } from '../dialog/Dialog'
import { authenticateProjectRequest, Project, updateProjectRequest } from '../../scripts/projects'
import { ProjectPasswordInput } from '../input/ProjectPasswordInput'
import { Button } from '../button/Button'
import { ButtonType } from '../../scripts/Button'
import { Popup } from './Popup'

import '../../styles/popup/UpdateProjectPasswordPopup.css'

// Components.
export function UpdateProjectPasswordPopup({
    projectId,
    isPrivate,
    closePopup,
    onSuccess,
}: {
    projectId: string
    isPrivate: boolean
    closePopup: () => void
    onSuccess: (project: Project) => void
}): JSX.Element {
    console.info('Opening double check project password popup...')

    // Set up dialog.
    const { showDialog } = useDialog()

    // Set up state to manage passwords.
    const [currentPassword, setCurrentPassword] = useState<string | null>(null)
    const [newPassword, setNewPassword] = useState<string | null>(null)
    const [confirmNewPassword, setConfirmNewPassword] = useState<string | null>(null)

    // Authenticate project function.
    async function checkCurrentPassword(projectId: string, password: string): Promise<boolean> {
        try {
            await authenticateProjectRequest(projectId, password)
            return true
        } catch (error) {
            if (error instanceof APIErrorResponse) {
                console.error('Error authenticating to project:', error)
                showDialog('error', 'Current password is incorrect.', error.status_code)
            } else {
                console.error('Unexpected error authenticating to project:', error)
                showDialog('error', 'An unexpected error occurred while authenticating to the project.', 500)
            }
        }
        return false
    }

    async function validateNewPassword() {
        return newPassword === confirmNewPassword
    }

    const children = (
        <div className="update-project-password-popup-component">
            {isPrivate && (
                <ProjectPasswordInput
                    id="current-project-password"
                    isOptional={false}
                    setProjectPassword={setCurrentPassword}
                    placeholder="Current password"
                />
            )}
            <ProjectPasswordInput
                id="new-project-password"
                isOptional={false}
                setProjectPassword={setNewPassword}
                placeholder="New password"
            />
            <ProjectPasswordInput
                id="confirm-new-project-password"
                isOptional={false}
                setProjectPassword={setConfirmNewPassword}
                placeholder="Confirm new password"
            />
            <Button
                id="update-project-password-btn"
                value="Update"
                buttonType={ButtonType.SECONDARY}
                onClickEvent={async () => {
                    // Check current password of the project.
                    console.debug(currentPassword, newPassword, confirmNewPassword)
                    const isValidCurrentPassword = isPrivate
                        ? await checkCurrentPassword(projectId, currentPassword ?? '')
                        : true
                    if (!isValidCurrentPassword) {
                        console.error('Current password validation failed.')
                        showDialog(
                            'error',
                            'Current password is incorrect. Please enter the correct current password.',
                            null,
                        )
                        return
                    }

                    // Check new password and confirmation match.
                    const isValidNewPassword = await validateNewPassword()
                    if (!isValidNewPassword) {
                        console.error('New password validation failed.')
                        showDialog('error', 'The new password does not match the confirmation.', null)
                        return
                    }

                    // Update project password.
                    try {
                        const project = await updateProjectRequest(projectId, { password: newPassword })
                        showDialog('info', 'Project password updated successfully.', null)
                        onSuccess(project)
                    } catch (error) {
                        if (error instanceof APIErrorResponse) {
                            console.error('Error updating project password:', error)
                            showDialog('error', error.message, error.status_code)
                        } else {
                            console.error('Unexpected error updating project password:', error)
                            showDialog(
                                'error',
                                'An unexpected error occurred while updating the project password.',
                                500,
                            )
                        }
                    }
                }}
            />
        </div>
    )

    const component = <Popup title="Update Project Password" children={children} closePopup={closePopup} />

    return <PopupOverlay children={component} />
}
