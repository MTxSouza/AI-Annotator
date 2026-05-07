import { switchApplicationTheme } from './theme'

document.addEventListener('keydown', (event) => {
    // "SHIFT" + "F" shortcut to toggle full screen mode.
    if (event.shiftKey && event.code === 'KeyF') {
        console.info('SHIFT + F keyboard shortcut pressed. Toggling full screen mode...')
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch((err) => {
                console.error(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`)
            })
        } else {
            document.exitFullscreen()
        }
    }

    // "SHIFT + T" shortcut to switch the theme.
    if (event.shiftKey && event.code === 'KeyT') {
        console.info('SHIFT + T keyboard shortcut pressed. Switching theme of the application...')
        switchApplicationTheme()
    }
})
