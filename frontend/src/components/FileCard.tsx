import { JSX } from 'react'
import { File } from '../scripts/files'
import { FileUploadArea } from './FileUploadArea'

import SmallCheck from '../icons/smallCheck.svg?react'
import Trash from '../icons/trash.svg?react'

import '../styles/FileCard.css'

// Components.
export function UploadFileCard({
    onUpload,
    allowedFileTypes,
}: {
    onUpload: (file: FileList | null) => void
    allowedFileTypes?: string[]
}): JSX.Element {
    return (
        <div className="upload-file-card-component">
            <FileUploadArea displayName={null} onUpload={onUpload} allowedFileTypes={allowedFileTypes} />
        </div>
    )
}

export function FileCard({ file }: { file: File }): JSX.Element {
    return (
        <div className="file-card-component">
            <label className="is-file-labeled-component">
                <SmallCheck />
            </label>
            <button className="delete-file-btn-component">
                <Trash />
            </button>
            <label className="file-card-icon-component"></label>
            <p className="file-card-name-component">{file.filename}</p>
        </div>
    )
}
