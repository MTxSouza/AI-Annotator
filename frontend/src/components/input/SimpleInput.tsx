import { JSX } from 'react'

import '../../styles/input/SimpleInput.css'

export function SimpleInput({
    id,
    placeholder,
    onChangeEvent,
    value,
    type = 'text',
    maxLength = 32,
}: {
    id: string
    placeholder: string
    onChangeEvent: (value: any) => void
    value?: string | number
    type?: string
    maxLength?: number
}): JSX.Element {
    /*
    Abstracted input component for text input.
    */
    return (
        <input
            className="simple-input-component"
            id={id}
            defaultValue={value}
            type={type}
            maxLength={maxLength}
            placeholder={placeholder}
            onChange={onChangeEvent}
        />
    )
}
