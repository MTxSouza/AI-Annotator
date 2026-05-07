import { JSX, useState } from 'react'
import { SimpleInput } from './SimpleInput'

import EyeClose from '../../icons/eyeClose.svg?react'
import EyeOpen from '../../icons/eyeOpen.svg?react'

import '../../styles/input/ProjectPasswordInput.css'

export function ProjectPasswordInput({
    isOptional,
    setProjectPassword,
}: {
    isOptional?: boolean
    setProjectPassword: (password: string | null) => void
}): JSX.Element {
    // Set up state to manage the visibility of the project password input.
    const [hidePassword, setHidePassword] = useState<boolean>(true)

    // Set placeholder message.
    let placeholderMessage = 'Password'
    if (isOptional) {
        placeholderMessage += ' (optional)'
    }

    const component = (
        <div className="project-password-input-container">
            <SimpleInput
                id="project-password-input-component"
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
