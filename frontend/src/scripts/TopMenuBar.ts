import { NavigateFunction } from 'react-router-dom'
import { PROJECT_MENU_URL } from './common'

export function redirectToProjectMenuPage(navigate: NavigateFunction) {
    console.info('Redirecting to project menu page...')
    navigate(PROJECT_MENU_URL)
}
