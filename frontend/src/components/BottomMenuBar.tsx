/*
Main component for the bottom menu bar.
*/
import { JSX } from 'react'

import GitHubIcon from '../icons/github.svg?react'
import LinkedInIcon from '../icons/linkedin.svg?react'
import KeyBoardIcon from '../icons/keyBoard.svg?react'

import '../styles/BottomMenuBar.css'

// Components.
function ShortcutKey({ keyMapping, description }: { keyMapping: string; description: string }): JSX.Element {
    return (
        <p>
            <span className="shortcut-key">{keyMapping}</span>
            {description}
        </p>
    )
}

export function BottomMenuBar(): JSX.Element {
    return (
        <div className="bottom-menu-bar-component">
            <div className="developer-info-container">
                <button onClick={() => window.open('https://github.com/MTxSouza/AI-Annotator')}>
                    <GitHubIcon />
                </button>
                <button onClick={() => window.open('https://www.linkedin.com/in/matheus-oliveira-de-souza/')}>
                    <LinkedInIcon />
                </button>
            </div>
            <div className="keyboard-shortcuts-image-container">
                <button>
                    <KeyBoardIcon style={{ fill: 'var(--tertiary-text-color)' }} />
                    <div className="keyboard-shortcuts-window-popup">
                        <h3>Keyboard Shortcuts</h3>
                        <ShortcutKey keyMapping="CTRL + SHIFT + F" description="Full Screen (Recommended)" />
                        <ShortcutKey keyMapping="CTRL + SHIFT + L" description="Switch theme" />
                    </div>
                </button>
            </div>
        </div>
    )
}
