/*
Main component to display a popup.
*/
import { JSX } from 'react'

// Styles.
import '../../styles/popup/Popup.css'

// Components.
export function Popup({ children }: { children: JSX.Element }): JSX.Element {
    return (
        <div className="popup-component" onClick={(event) => event.stopPropagation()}>
            {children}
        </div>
    )
}
