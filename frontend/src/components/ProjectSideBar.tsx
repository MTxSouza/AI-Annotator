/*
Main side bar component for the project home page.
*/
import { JSX, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { PROJECT_DATASET_URL, PROJECT_ANALYTICS_URL, PROJECT_SETTINGS_URL, redirectTo } from '../scripts/common'

import Database from '../icons/database.svg?react'
import BarChart from '../icons/barChart.svg?react'
import Settings from '../icons/settings.svg?react'

import '../styles/ProjectSideBar.css'

// Components.
export function ProjectSideBar({ projectId }: { projectId: string }): JSX.Element {
    // Set up navigation and location hooks.
    const navigate = useNavigate()
    const location = useLocation()

    // Get URL for each page.
    const datasetUrl: string = PROJECT_DATASET_URL.replace(':projectId', projectId)
    const analyticsUrl: string = PROJECT_ANALYTICS_URL.replace(':projectId', projectId)
    const settingsUrl: string = PROJECT_SETTINGS_URL.replace(':projectId', projectId)

    const isInDatasetPage: boolean = location.pathname === datasetUrl
    const isInAnalyticsPage: boolean = location.pathname === analyticsUrl
    const isInSettingsPage: boolean = location.pathname === settingsUrl

    useEffect(() => {
        if (!isInDatasetPage && !isInAnalyticsPage && !isInSettingsPage) {
            // If the user is not in any of the pages, redirect to the dataset page.
            console.warn('User is not in any of the project pages, redirecting to dataset page.')
            redirectTo(datasetUrl, navigate)
        }
    }, [isInDatasetPage, isInSettingsPage, datasetUrl, navigate])

    return (
        <div className="project-side-bar-component">
            <button
                onClick={() => {
                    redirectTo(PROJECT_DATASET_URL.replace(':projectId', projectId), navigate)
                }}
                className={isInDatasetPage ? 'active' : ''}
            >
                <Database />
                <span>Dataset</span>
            </button>
            <button
                onClick={() => {
                    redirectTo(PROJECT_ANALYTICS_URL.replace(':projectId', projectId), navigate)
                }}
                className={isInAnalyticsPage ? 'active' : ''}
            >
                <BarChart />
                <span>Analytics</span>
            </button>
            <button
                id="project-settings-btn"
                onClick={() => {
                    redirectTo(PROJECT_SETTINGS_URL.replace(':projectId', projectId), navigate)
                }}
                className={isInSettingsPage ? 'active' : ''}
            >
                <Settings />
                <span>Settings</span>
            </button>
        </div>
    )
}
