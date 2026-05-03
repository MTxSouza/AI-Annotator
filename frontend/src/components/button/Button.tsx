import { JSX } from 'react'
import { ButtonType } from '../../scripts/Button'

import '../../styles/button/Button.css'

export function Button({
    id,
    value,
    buttonType = ButtonType.TERTIARY,
    disabled = false,
    onClickEvent,
}: {
    id: string
    value?: string
    buttonType?: ButtonType
    disabled?: boolean
    onClickEvent: (value: any) => void
}): JSX.Element {
    // Set up class name based on button type.
    const className = `${buttonType}-btn-component`

    return (
        <button className={className} id={id} onClick={onClickEvent} disabled={disabled}>
            {value}
        </button>
    )
}
