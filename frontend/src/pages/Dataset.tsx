/*
Main dataset page for project management.
*/
import { JSX, useEffect, useState } from 'react'
import { Project } from '../scripts/projects'
import { File, uploadFileToProject } from '../scripts/files'
import { fetchData, RequestMethod, APIErrorResponse } from '../scripts/common'
import { useOutletContext } from 'react-router-dom'
import { FileUploadArea } from '../components/FileUploadArea'
import { useDialog } from '../components/dialog/Dialog'
import { UploadFileCard, FileCard } from '../components/FileCard'

import '../styles/pages/Dataset.css'

// Components.
function DatasetInfoHeaderCard({ value, label }: { value: number | string; label: string }): JSX.Element {
    return (
        <div className="dataset-info-header-card-component">
            <span>{value}</span>
            <p>{label}</p>
        </div>
    )
}

export function Dataset(): JSX.Element {
    // Set up dialog.
    const { showDialog } = useDialog()

    // Set up states.
    const [projectFiles, setProjectFiles] = useState<File[]>([])
    const [isLoading, setIsLoading] = useState(true)

    async function uploadFiles(files: FileList | null) {
        // Send upload request to the server.
        try {
            const fileUploadWorkerResult = await uploadFileToProject(files, project._id)
            showDialog('info', 'Files uploaded requested successfully!', null)
        } catch (error) {
            if (error instanceof APIErrorResponse) {
                console.error('Error uploading files:', error)
                showDialog('error', error.message, error.status_code)
            } else {
                console.error('Unexpected error uploading files:', error)
                showDialog('error', 'An unexpected error occurred while uploading files.', 500)
            }
        }
    }

    // Get the project data from the outlet context.
    const [project, setProject] = useOutletContext<[Project, React.Dispatch<React.SetStateAction<Project>>]>()
    let projectFileFormat = project.details.file_format || []

    // Request all files and annotations of the project.
    useEffect(() => {
        async function fetchProjectFiles() {
            try {
                const projectFiles = await fetchData(`/projects/${project._id}/files`, RequestMethod.GET)
                console.debug(`Fetched ${projectFiles.length} files for project ${project._id}`)
                setProjectFiles(projectFiles)
                setIsLoading(false)
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

    // Wait fetching project files before rendering.
    if (isLoading) {
        return <></>
    }

    // Compute total disk usage of project files.
    const totalDiskUsage = projectFiles.reduce((total, file) => total + file.size_in_bytes, 0) / (1024 * 1024) // Convert to megabytes
    console.debug(`Total disk usage for project ${project._id}: ${totalDiskUsage} MB`)

    return (
        <div className="project-dataset-component">
            <div className="project-dataset-header-component">
                <DatasetInfoHeaderCard value={projectFiles.length} label="Files" />
                <DatasetInfoHeaderCard value={project.details.number_of_samples} label="Total annotated samples" />
                <DatasetInfoHeaderCard value={totalDiskUsage.toFixed(2)} label="Total disk usage (MB)" />
            </div>
            {(!projectFiles.length && (
                <FileUploadArea
                    displayName="Upload a file to start labeling."
                    onUpload={uploadFiles}
                    allowedFileTypes={projectFileFormat}
                />
            )) || (
                <div className="project-file-list-component">
                    <UploadFileCard onUpload={uploadFiles} allowedFileTypes={projectFileFormat} />
                    {projectFiles.map((file) => (
                        <FileCard key={file._id} file={file} />
                    ))}
                </div>
            )}
        </div>
    )
}
