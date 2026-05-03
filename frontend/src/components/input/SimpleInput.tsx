import { JSX } from 'react'

export function SimpleInput({
    id,
    placeholder,
    onChangeEvent,
    maxLength = 32,
}: {
    id: string
    placeholder: string
    onChangeEvent: (value: any) => void
    maxLength?: number
}): JSX.Element {
    /*
    Abstracted input component for text input.
    */
    return (
        <input
            id={id}
            type="text"
            maxLength={maxLength}
            placeholder={placeholder}
            onChange={(event) => onChangeEvent(event.target.value)}
        />
    )
}
