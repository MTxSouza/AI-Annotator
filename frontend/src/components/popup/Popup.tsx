/*
Main component to display a popup.
*/
import { JSX } from 'react'

import Close from '../../icons/close.svg?react'

// Styles.
import '../../styles/popup/Popup.css'

// Components.
export function TopMenuBarPopup({ title, closePopup }: { title: string; closePopup: () => void }): JSX.Element {
    return (
        <div className="top-menu-bar-popup-component" onClick={(event) => event.stopPropagation()}>
            <h2>{title}</h2>
            <button onClick={closePopup}>
                <Close />
            </button>
        </div>
    )
}

export function Popup({
    children,
    title,
    closePopup,
}: {
    children: JSX.Element
    title?: string
    closePopup?: () => void
}): JSX.Element {
    // Check if title and closePopup are both defined.
    const showTopMenuBar = title !== undefined && closePopup !== undefined
    return (
        <div className="popup-component" onClick={(event) => event.stopPropagation()}>
            {showTopMenuBar && <TopMenuBarPopup title={title} closePopup={closePopup} />}
            {children}
        </div>
    )
}
