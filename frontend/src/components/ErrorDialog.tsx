import { createContext, useContext, useState, JSX, ReactNode } from 'react'
import { ErrorDialogMessage } from '../scripts/ErrorDialog'

import '../styles/ErrorDialog.css'

// Create the context.
interface ErrorDialogContextType {
    showErrorDialog: (message: string, status_code: number) => void
}
const ErrorDialogContext = createContext<ErrorDialogContextType | undefined>(undefined)

// Create the provider component.
export function ErrorDialogProvider({ children }: { children: ReactNode }): JSX.Element {
    // State to store all error dialogs.
    const [errorDialogs, setErrorDialogs] = useState<ErrorDialogMessage[]>([])

    // Function to show an error dialog.
    const showErrorDialog = (message: string, status_code: number) => {
        // Set up error dialog.
        const id = Date.now()
        setErrorDialogs((prevDialogs) => [...prevDialogs, { id, message: message, status_code: status_code }])

        // Add time to remove the dialog.
        setTimeout(() => {
            setErrorDialogs((prevDialogs) => prevDialogs.filter((dialog) => dialog.id !== id))
        }, 5000) // Remove after 5 seconds.
    }

    return (
        <ErrorDialogContext.Provider value={{ showErrorDialog }}>
            {children}
            <div className="error-dialog-popup-container">
                {errorDialogs.map((dialog) => (
                    <div key={dialog.id} className="error-dialog-popup-component">
                        <p className="error-dialog-message">
                            {dialog.message}: {dialog.status_code}
                        </p>
                    </div>
                ))}
            </div>
        </ErrorDialogContext.Provider>
    )
}

export function useErrorDialog(): ErrorDialogContextType {
    const context = useContext(ErrorDialogContext)
    if (!context) {
        throw new Error('useErrorDialog must be used within an ErrorDialogProvider')
    }
    return context
}
