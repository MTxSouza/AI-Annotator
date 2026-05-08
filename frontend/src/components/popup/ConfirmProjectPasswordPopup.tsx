import { JSX, useState } from 'react'
import { APIErrorResponse } from '../../scripts/common'
import { PopupOverlay } from '../PopupOverlay'
import { useDialog } from '../dialog/Dialog'
import { authenticateProjectRequest } from '../../scripts/projects'
import { ProjectPasswordInput } from '../input/ProjectPasswordInput'
import { Button } from '../button/Button'
import { ButtonType } from '../../scripts/Button'
import { Popup } from './Popup'

import '../../styles/popup/ConfirmProjectPasswordPopup.css'

export function ConfirmProjectPasswordPopup({
    projectId,
    closePopup,
    onSuccess,
}: {
    projectId: string
    closePopup: () => void
    onSuccess: () => void
}): JSX.Element {
    console.info('Opening confirm project password popup...')

    // Set up dialog.
    const { showDialog } = useDialog()

    // Set up state to manage project password input.
    const [projectPassword, setProjectPassword] = useState<string | null>(null)

    // Authenticate project function.
    async function authenticateProject(projectId: string, password: string) {
        try {
            await authenticateProjectRequest(projectId, password)
            onSuccess()
        } catch (error) {
            if (error instanceof APIErrorResponse) {
                console.error('Error authenticating to project:', error)
                showDialog('error', error.message, error.status_code)
            } else {
                console.error('Unexpected error authenticating to project:', error)
                showDialog('error', 'An unexpected error occurred while authenticating to the project.', 500)
            }
        }
    }

    const children = (
        <div className="confirm-project-password-popup-component">
            <ProjectPasswordInput isOptional={false} setProjectPassword={setProjectPassword} />
            <div>
                <Button
                    id="confirm-project-password-btn"
                    value={'Confirm'}
                    buttonType={ButtonType.SECONDARY}
                    onClickEvent={() => {
                        if (projectPassword === null) {
                            showDialog('error', 'Please enter the project password.', 400)
                            return
                        }
                        authenticateProject(projectId, projectPassword)
                    }}
                />
            </div>
        </div>
    )
    const component = <Popup title="Confirm Project Password" children={children} closePopup={closePopup} />

    return <PopupOverlay children={component} />
}
