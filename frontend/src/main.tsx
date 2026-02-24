import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { TopMenuBar } from './components/TopMenuBar'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { BottomMenuBar } from './components/BottomMenuBar'
import { ProjectMenuPage } from './components/ProjectMenuPage'

import './main.css'

// Ensure that the root element exists before attempting to render the React application.
const rootElement: HTMLElement | null = document.getElementById('root')
if (!rootElement) {
    throw new Error(
        'Failed to find the root element. Please ensure that there is an element with id "root" in the HTML file.',
    )
}
createRoot(rootElement).render(
    <StrictMode>
        <BrowserRouter>
            <TopMenuBar />
            <Routes>
                <Route path="/" element={<ProjectMenuPage />} />
            </Routes>
            <BottomMenuBar />
        </BrowserRouter>
    </StrictMode>,
)
