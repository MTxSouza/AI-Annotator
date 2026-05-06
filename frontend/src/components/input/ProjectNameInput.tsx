import { ChangeEvent, JSX } from 'react'
import { SimpleInput } from './SimpleInput'

export function ProjectNameInput({
    onChangeEvent,
}: {
    onChangeEvent: (value: ChangeEvent<HTMLInputElement>) => void
}): JSX.Element {
    return (
        <SimpleInput
            id="project-name-input-component"
            placeholder="Project Name"
            onChangeEvent={onChangeEvent}
            maxLength={32}
        />
    )
}
