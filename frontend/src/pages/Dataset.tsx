/*
Main dataset page for project management.
*/
import { JSX, useEffect, useState } from 'react'
import { Project } from '../scripts/projects'
import { fetchData, RequestMethod, APIErrorResponse } from '../scripts/common'
import { useOutletContext } from 'react-router-dom'
import { FileUploadArea } from '../components/FileUploadArea'
import { useDialog } from '../components/dialog/Dialog'

import '../styles/pages/Dataset.css'

// Components.
export function Dataset(): JSX.Element {
    // Set up dialog.
    const { showDialog } = useDialog()

    // Set up states.
    const [projectFiles, setProjectFiles] = useState<File[]>([])

    // Get the project data from the outlet context.
    const project = useOutletContext<Project>()
    let projectFileFormat = project.details.file_format || []

    // Request all files and annotations of the project.
    useEffect(() => {
        async function fetchProjectFiles() {
            try {
                const projectFiles = await fetchData(`/projects/${project._id}/files`, RequestMethod.GET)
                console.debug(`Fetched ${projectFiles.length} files for project ${project._id}`)
                setProjectFiles(projectFiles)
            } catch (error) {
                if (error instanceof APIErrorResponse) {
                    console.error('Error fetching project files:', error)
                    showDialog('error', error.message, error.status_code)
                } else {
                    console.error('Unexpected error fetching project files:', error)
                    showDialog('error', 'An unexpected error occurred while fetching project files.', 500)
                }
            }
        }
        fetchProjectFiles()
    }, [project._id])

    return (
        <div className="project-dataset-component">
            {!projectFiles.length && (
                <FileUploadArea
                    displayName="Upload a file to start labeling."
                    onUpload={() => {
                        console.debug('Upload button clicked.')
                    }}
                    allowedFileTypes={projectFileFormat}
                />
            )}
        </div>
    )
}
