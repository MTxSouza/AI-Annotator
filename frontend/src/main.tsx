import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { TopMenuBar } from './components/TopMenuBar'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { BottomMenuBar } from './components/BottomMenuBar'
import { DialogProvider } from './components/dialog/Dialog'
import { ProjectMenu } from './pages/ProjectMenu'
import { Home } from './pages/Home'
import { PROJECT_MENU_URL, PROJECT_HOME_URL } from './scripts/common'

import './main.css'

// Get environment variables.
const isDevelopment: boolean = import.meta.env.VITE_APP_DEVELOP === 'true'

// Ensure that the root element exists before attempting to render the React application.
const rootElement: HTMLElement | null = document.getElementById('root')
if (!rootElement) {
    throw new Error(
        'Failed to find the root element. Please ensure that there is an element with id "root" in the HTML file.',
    )
}

const application = () => {
    // Define the main application component with routing and context providers.
    const application = (
        <DialogProvider>
            <BrowserRouter>
                <TopMenuBar />
                <Routes>
                    <Route path={PROJECT_MENU_URL} element={<ProjectMenu />} />
                    <Route path={PROJECT_HOME_URL} element={<Home />} />
                </Routes>
                <BottomMenuBar />
            </BrowserRouter>
        </DialogProvider>
    )

    if (isDevelopment) {
        console.info('Running in development mode...')
        return <StrictMode>{application}</StrictMode>
    }
    console.info('Running in production mode...')
    return application
}
createRoot(rootElement).render(application())
