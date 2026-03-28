/*
Main component for the dialog system.
*/
import { createContext, JSX, ReactNode, useContext, useRef, useState } from 'react'
import { DialogMessage } from '../../scripts/Dialog'
import { DialogType } from '../../scripts/Dialog'

// Styles.
import '../../styles/dialog/Dialog.css'

// Create the context.
interface dialogContextType {
    showDialog: (type: DialogType, message: string, status_code: number | null) => void
}
const dialogContext = createContext<dialogContextType | undefined>(undefined)

// Components.
export function DialogContainer({ children }: { children: JSX.Element | JSX.Element[] }): JSX.Element {
    return <div className="dialog-container">{children}</div>
}

// Create the provider component.
export function DialogProvider({ children }: { children: ReactNode }): JSX.Element {
    // State to store all error dialogs.
    const [dialogs, setDialogs] = useState<DialogMessage[]>([])
    const errorDialogsMap = useRef<Record<number, number>>({})

    // Function to show an error dialog.
    const showDialog = (type: DialogType, message: string, status_code: number | null) => {
        // Set up error dialog.
        const id = Date.now() + Math.random() // Unique ID for the dialog.
        setDialogs((prevDialogs) => [...prevDialogs, { id, type: type, message: message, status_code: status_code }])

        // Add time to remove the dialog.
        errorDialogsMap.current[id] = setTimeout(() => {
            setDialogs((prevDialogs) => prevDialogs.filter((dialog) => dialog.id !== id))
            delete errorDialogsMap.current[id]
        }, 5000) // Remove after 5 seconds.
    }

    const dialogList = dialogs.map((dialog) => {
        const message = dialog.status_code ? `${dialog.message} (Status code: ${dialog.status_code})` : dialog.message
        return (
            <div key={dialog.id} className={`dialog-component ${dialog.type}`}>
                <p className="dialog-message">{message}</p>
            </div>
        )
    })
    const dialogContainer = <DialogContainer children={dialogList.length > 0 ? dialogList : []} />

    return (
        <dialogContext.Provider value={{ showDialog }}>
            {children}
            {dialogContainer}
        </dialogContext.Provider>
    )
}

export function useDialog(): dialogContextType {
    const context = useContext(dialogContext)
    if (!context) {
        throw new Error('useDialog must be used within a DialogProvider')
    }
    return context
}
