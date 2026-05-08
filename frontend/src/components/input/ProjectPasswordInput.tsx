import { JSX, useState } from 'react'
import { SimpleInput } from './SimpleInput'

import EyeClose from '../../icons/eyeClose.svg?react'
import EyeOpen from '../../icons/eyeOpen.svg?react'

import '../../styles/input/ProjectPasswordInput.css'

export function ProjectPasswordInput({
    id,
    isOptional,
    setProjectPassword,
    placeholder,
}: {
    id?: string
    isOptional?: boolean
    setProjectPassword: (password: string | null) => void
    placeholder?: string
}): JSX.Element {
    // Set up state to manage the visibility of the project password input.
    const [hidePassword, setHidePassword] = useState<boolean>(true)

    // Set ID.
    const inputId = id || 'project-password-input-component'

    // Set placeholder message.
    let placeholderMessage = 'Password'
    if (placeholder === undefined) {
        if (isOptional) {
            placeholderMessage += ' (optional)'
        }
    } else {
        placeholderMessage = placeholder
    }

    const component = (
        <div className="project-password-input-container">
            <SimpleInput
                id={inputId}
                type={hidePassword ? 'password' : 'text'}
                placeholder={placeholderMessage}
                onChangeEvent={(event) => setProjectPassword(event.target.value || null)}
            />
            <label id="project-password-visibility-label" htmlFor="change-project-password-visibility-btn">
                <input
                    type="checkbox"
                    id="change-project-password-visibility-btn"
                    checked={hidePassword}
                    onChange={() => setHidePassword(!hidePassword)}
                />
                {hidePassword ? <EyeClose /> : <EyeOpen />}
            </label>
        </div>
    )
    return component
}
