import { NavigateFunction } from 'react-router-dom'
import { PROJECT_MENU_URL } from './common'

function getCurrentApplicationTheme() {
    // Get the current theme of the application in browser's local storage.
    const currentTheme = localStorage.getItem('theme') || 'light'
    console.debug('Current theme of the application:', currentTheme)
    return currentTheme
}

export function redirectToProjectMenuPage(navigate: NavigateFunction) {
    console.info('Redirecting to project menu page...')
    navigate(PROJECT_MENU_URL)
}

export function switchApplicationTheme() {
    // Get the current theme of the application.
    const currentTheme = getCurrentApplicationTheme()
    const newTheme = currentTheme === 'light' ? 'darkmode' : 'light'

    // Switch the theme of the application.
    applyCurrentApplicationTheme(newTheme)

    // Update the theme of the application in browser's local storage.
    localStorage.setItem('theme', newTheme)
}

function applyCurrentApplicationTheme(theme: string) {
    // Apply the given theme to the application.
    if (theme === 'light') {
        console.debug('Applying "light" theme to the application.')
        document.body.classList.remove('darkmode')
    } else {
        console.debug('Applying "darkmode" theme to the application.')
        document.body.classList.add('darkmode')
    }
}

// Set theme of the application on page load.
document.addEventListener('DOMContentLoaded', () => {
    console.info('Setting theme of the application on page load.')
    const currentTheme = getCurrentApplicationTheme()
    applyCurrentApplicationTheme(currentTheme)
})
