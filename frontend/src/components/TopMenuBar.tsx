/*
Main component for the top menu bar.
*/
import { JSX } from 'react'
import { useNavigate } from 'react-router-dom'
import { logoutProjectRequest } from '../scripts/projects'
import { redirectToProjectMenuPage, switchApplicationTheme } from '../scripts/TopMenuBar'

import LightThemeIcon from '../icons/lightMode.svg?react'
import DarkThemeIcon from '../icons/darkMode.svg?react'

import '../styles/TopMenuBar.css'

export function TopMenuBar(): JSX.Element {
    // Set up navigation.
    const navigate = useNavigate()

    return (
        <div className="top-menu-bar-component">
            <div className="project-logo-image-container">
                <button
                    id="redirect-project-menu-btn"
                    onClick={() => {
                        redirectToProjectMenuPage(navigate)
                        logoutProjectRequest()
                    }}
                ></button>
            </div>
            <div className="switch-theme-btn-container">
                <button id="switch-dark-theme-btn" onClick={switchApplicationTheme}>
                    <DarkThemeIcon />
                </button>
                <button id="switch-light-theme-btn" onClick={switchApplicationTheme}>
                    <LightThemeIcon />
                </button>
            </div>
        </div>
    )
}
