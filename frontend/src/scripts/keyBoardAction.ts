import { switchApplicationTheme } from './theme'

document.addEventListener('keydown', (event) => {
    // "CTRL" + "SHIFT" + "F" shortcut to toggle full screen mode.
    if (event.ctrlKey && event.shiftKey && event.code === 'KeyF') {
        console.info('CTRL + SHIFT + F keyboard shortcut pressed. Toggling full screen mode...')
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch((err) => {
                console.error(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`)
            })
        } else {
            document.exitFullscreen()
        }
    }

    // "CTRL" + "SHIFT" + "L" shortcut to switch the theme.
    if (event.ctrlKey && event.shiftKey && event.code === 'KeyL') {
        console.info('CTRL + SHIFT + L keyboard shortcut pressed. Switching theme of the application...')
        switchApplicationTheme()
    }
})
