import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { TopMenuBar } from './components/TopMenuBar'
import { ApplicationContainer } from './components/ApplicationContainer'
import { BottomMenuBar } from './components/BottomMenuBar'

import './main.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <TopMenuBar />
    <ApplicationContainer />
    <BottomMenuBar />
  </StrictMode>,
)
