import { JSX } from 'react'
import { APIErrorResponse } from '../scripts/common'
import { PopupOverlay } from '../components/PopupOverlay'
import { useErrorDialog } from '../components/ErrorDialog'
import { deleteProjectRequest } from '../scripts/projects'

import '../styles/ConfirmProjectDeletionPopup.css'

export function ConfirmProjectDeletionPopup({
    projectId,
    closePopup,
    refreshProjects,
}: {
    projectId: string
    closePopup: () => void
    refreshProjects: () => void
}): JSX.Element {
    console.info('Opening confirm project deletion popup...')

    // Set up error dialog.
    const { showErrorDialog } = useErrorDialog()

    // Delete project function.
    async function deleteProject(projectId: string) {
        try {
            await deleteProjectRequest(projectId)
            refreshProjects()
        } catch (error) {
            if (error instanceof APIErrorResponse) {
                console.error('Error deleting project:', error)
                showErrorDialog(error.message, error.status_code)
            } else {
                console.error('Unexpected error deleting project:', error)
                showErrorDialog('An unexpected error occurred while deleting the project.', 500)
            }
        }
    }

    const component = (
        <div className="confirm-project-deletion-popup-component" onClick={(event) => event.stopPropagation()}>
            <h4>Are you sure you want to delete this project?</h4>
            <div>
                <button onClick={() => deleteProject(projectId)}>Yes</button>
                <button onClick={closePopup}>No</button>
            </div>
        </div>
    )
    return <PopupOverlay children={component} />
}
