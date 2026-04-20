/*
Main side bar component for the project home page.
*/
import { JSX, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { PROJECT_DATASET_URL, PROJECT_ANALYTICS_URL, PROJECT_SETTINGS_URL, redirectTo } from '../scripts/common'

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
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    height="24px"
                    viewBox="0 -960 960 960"
                    width="24px"
                    fill="#FFFFFF"
                >
                    <path d="M480-120q-151 0-255.5-46.5T120-280v-400q0-66 105.5-113T480-840q149 0 254.5 47T840-680v400q0 67-104.5 113.5T480-120Zm0-479q89 0 179-25.5T760-679q-11-29-100.5-55T480-760q-91 0-178.5 25.5T200-679q14 30 101.5 55T480-599Zm0 199q42 0 81-4t74.5-11.5q35.5-7.5 67-18.5t57.5-25v-120q-26 14-57.5 25t-67 18.5Q600-528 561-524t-81 4q-42 0-82-4t-75.5-11.5Q287-543 256-554t-56-25v120q25 14 56 25t66.5 18.5Q358-408 398-404t82 4Zm0 200q46 0 93.5-7t87.5-18.5q40-11.5 67-26t32-29.5v-98q-26 14-57.5 25t-67 18.5Q600-328 561-324t-81 4q-42 0-82-4t-75.5-11.5Q287-343 256-354t-56-25v99q5 15 31.5 29t66.5 25.5q40 11.5 88 18.5t94 7Z" />
                </svg>
                <span>Dataset</span>
            </button>
            <button
                onClick={() => {
                    redirectTo(PROJECT_ANALYTICS_URL.replace(':projectId', projectId), navigate)
                }}
                className={isInAnalyticsPage ? 'active' : ''}
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    height="24px"
                    viewBox="0 -960 960 960"
                    width="24px"
                    fill="#FFFFFF"
                >
                    <path d="M640-160v-280h160v280H640Zm-240 0v-640h160v640H400Zm-240 0v-440h160v440H160Z" />
                </svg>
                <span>Analytics</span>
            </button>
            <button
                id="project-settings-btn"
                onClick={() => {
                    redirectTo(PROJECT_SETTINGS_URL.replace(':projectId', projectId), navigate)
                }}
                className={isInSettingsPage ? 'active' : ''}
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    height="24px"
                    viewBox="0 -960 960 960"
                    width="24px"
                    fill="#FFFFFF"
                >
                    <path d="m370-80-16-128q-13-5-24.5-12T307-235l-119 50L78-375l103-78q-1-7-1-13.5v-27q0-6.5 1-13.5L78-585l110-190 119 50q11-8 23-15t24-12l16-128h220l16 128q13 5 24.5 12t22.5 15l119-50 110 190-103 78q1 7 1 13.5v27q0 6.5-2 13.5l103 78-110 190-118-50q-11 8-23 15t-24 12L590-80H370Zm70-80h79l14-106q31-8 57.5-23.5T639-327l99 41 39-68-86-65q5-14 7-29.5t2-31.5q0-16-2-31.5t-7-29.5l86-65-39-68-99 42q-22-23-48.5-38.5T533-694l-13-106h-79l-14 106q-31 8-57.5 23.5T321-633l-99-41-39 68 86 64q-5 15-7 30t-2 32q0 16 2 31t7 30l-86 65 39 68 99-42q22 23 48.5 38.5T427-266l13 106Zm42-180q58 0 99-41t41-99q0-58-41-99t-99-41q-59 0-99.5 41T342-480q0 58 40.5 99t99.5 41Zm-2-140Z" />
                </svg>
                <span>Settings</span>
            </button>
        </div>
    )
}
