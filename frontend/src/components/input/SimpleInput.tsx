import { JSX } from 'react'

export function SimpleInput({
    id,
    placeholder,
    onChangeEvent,
    type = 'text',
    maxLength = 32,
}: {
    id: string
    placeholder: string
    onChangeEvent: (value: any) => void
    type?: string
    maxLength?: number
}): JSX.Element {
    /*
    Abstracted input component for text input.
    */
    return <input id={id} type={type} maxLength={maxLength} placeholder={placeholder} onChange={onChangeEvent} />
}
