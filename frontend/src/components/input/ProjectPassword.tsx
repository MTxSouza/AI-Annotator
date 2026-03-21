import { JSX, useState } from 'react'

import '../../styles/input/ProjectPassword.css'

export function ProjectPassword({
    isOpcional,
    setProjectPassword,
}: {
    isOpcional?: boolean
    setProjectPassword: (password: string | null) => void
}): JSX.Element {
    // Set up state to manage the visibility of the project password input.
    const [hidePassword, setHidePassword] = useState<boolean>(true)

    // Set placeholder message.
    let placeholderMessage = 'Password'
    if (isOpcional) {
        placeholderMessage += ' (optional)'
    }

    const component = (
        <div className="project-password-input-container">
            <input
                id="project-password-input"
                type={hidePassword ? 'password' : 'text'}
                placeholder={placeholderMessage}
                onChange={(event) => setProjectPassword(event.target.value || null)}
            />
            <label id="project-password-visibility-label" htmlFor="change-project-password-visibilty-btn">
                <input
                    type="checkbox"
                    id="change-project-password-visibilty-btn"
                    checked={hidePassword}
                    onChange={() => setHidePassword(!hidePassword)}
                />
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    height="24px"
                    viewBox="0 -960 960 960"
                    width="24px"
                    fill="#FFFFFF"
                >
                    <path d="M240-80q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640h40v-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240Zm0-80h480v-400H240v400Zm296.5-143.5Q560-327 560-360t-23.5-56.5Q513-440 480-440t-56.5 23.5Q400-393 400-360t23.5 56.5Q447-280 480-280t56.5-23.5ZM360-640h240v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85v80ZM240-160v-400 400Z" />
                </svg>
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    height="24px"
                    viewBox="0 -960 960 960"
                    width="24px"
                    fill="#FFFFFF"
                >
                    <path d="M240-640h360v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85h-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640Zm0 480h480v-400H240v400Zm296.5-143.5Q560-327 560-360t-23.5-56.5Q513-440 480-440t-56.5 23.5Q400-393 400-360t23.5 56.5Q447-280 480-280t56.5-23.5ZM240-160v-400 400Z" />
                </svg>
            </label>
        </div>
    )
    return component
}
