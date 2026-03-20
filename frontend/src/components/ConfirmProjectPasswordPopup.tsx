import { JSX, useState } from 'react'
import { APIErrorResponse } from '../scripts/common'
import { PopupOverlay } from '../components/PopupOverlay'
import { useErrorDialog } from '../components/ErrorDialog'
import { authenticateProjectRequest } from '../scripts/projects'

import '../styles/ConfirmProjectPasswordPopup.css'

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

    const component = <div className="confirm-project-password-popup-component"></div>

    return <PopupOverlay children={component} />
}
