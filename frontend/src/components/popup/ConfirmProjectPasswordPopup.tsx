import { JSX, useState } from 'react'
import { APIErrorResponse } from '../../scripts/common'
import { PopupOverlay } from '../PopupOverlay'
import { useErrorDialog } from '../ErrorDialog'
import { authenticateProjectRequest } from '../../scripts/projects'
import { ProjectPassword } from '../input/ProjectPassword'
import { SimpleConfirmButton } from '../button/SimpleConfirmButton'

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

    // Set up error dialog.
    const { showErrorDialog } = useErrorDialog()

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
                showErrorDialog(error.message, error.status_code)
            } else {
                console.error('Unexpected error authenticating to project:', error)
                showErrorDialog('An unexpected error occurred while authenticating to the project.', 500)
            }
        }
    }

    const component = (
        <div className="confirm-project-password-popup-component">
            <div>
                <h2>Project Password</h2>
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
            <ProjectPassword isOpcional={false} setProjectPassword={setProjectPassword} />
            <div>
                <SimpleConfirmButton
                    message={'Confirm'}
                    onConfirm={() => {
                        if (projectPassword === null) {
                            showErrorDialog('Please enter the project password.', 400)
                            return
                        }
                        authenticateProject(projectId, projectPassword)
                    }}
                />
            </div>
        </div>
    )

    return <PopupOverlay children={component} />
}
