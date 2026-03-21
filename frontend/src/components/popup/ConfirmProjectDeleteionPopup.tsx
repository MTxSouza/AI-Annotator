import { JSX, useState } from 'react'
import { APIErrorResponse } from '../../scripts/common'
import { PopupOverlay } from '../../components/PopupOverlay'
import { useErrorDialog } from '../../components/ErrorDialog'
import { deleteProjectRequest } from '../../scripts/projects'
import { ConfirmProjectPasswordPopup } from './ConfirmProjectPasswordPopup'
import { Popup } from './Popup'

import '../../styles/popup/ConfirmProjectDeletionPopup.css'

export function ConfirmProjectDeletionPopup({
    projectId,
    isPrivate,
    closePopup,
    refreshProjects,
}: {
    projectId: string
    isPrivate: boolean
    closePopup: () => void
    refreshProjects: () => void
}): JSX.Element {
    console.info('Opening confirm project deletion popup...')

    // Set up error dialog.
    const { showErrorDialog } = useErrorDialog()

    // Set up state to manage project password input.
    const [showPasswordPopup, setShowPasswordPopup] = useState<boolean>(false)

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

    if (showPasswordPopup) {
        const children = (
            <ConfirmProjectPasswordPopup
                projectId={projectId}
                closePopup={closePopup}
                onSuccess={() => {
                    deleteProject(projectId)
                    setShowPasswordPopup(false)
                }}
            />
        )
        const component = <Popup children={children} />

        return <PopupOverlay children={component} />
    }

    const children = (
        <div className="confirm-project-deletion-popup-component" onClick={(event) => event.stopPropagation()}>
            <h4>Are you sure you want to delete this project?</h4>
            <div>
                <button
                    onClick={() => {
                        if (isPrivate) {
                            setShowPasswordPopup(true)
                            return
                        }
                        deleteProject(projectId)
                    }}
                >
                    Yes
                </button>
                <button onClick={closePopup}>No</button>
            </div>
        </div>
    )
    const component = <Popup children={children} />

    return <PopupOverlay children={component} />
}
