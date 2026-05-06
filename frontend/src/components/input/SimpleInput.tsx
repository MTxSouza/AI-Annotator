import { ChangeEvent, JSX } from 'react'

import '../../styles/input/SimpleInput.css'

export function SimpleInput({
    id,
    onChangeEvent,
    placeholder,
    value,
    type = 'text',
    maxLength = 32,
}: {
    id: string
    onChangeEvent: (value: ChangeEvent<HTMLInputElement>) => void
    placeholder?: string
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
