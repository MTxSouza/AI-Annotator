import { JSX } from 'react'

import '../../styles/button/SimpleConfirmButton.css'

export function SimpleConfirmButton({ message, onConfirm }: { message: string; onConfirm: () => void }): JSX.Element {
    const component = (
        <button className="simple-confirm-button-component" onClick={onConfirm}>
            {message}
        </button>
    )
    return component
}
