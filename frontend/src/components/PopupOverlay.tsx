import { useEffect, JSX } from 'react'

import '../styles/PopupOverlay.css'

export function PopupOverlay({ children }: { children: JSX.Element }): JSX.Element {
    // Block background scroll when popup is open.
    useEffect(() => {
        document.body.style.overflow = 'hidden'
        return () => {
            document.body.style.overflow = 'auto'
        }
    }, [])

    return <div className="popup-overlay-component">{children}</div>
}
