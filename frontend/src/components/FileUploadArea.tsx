import { JSX } from 'react'

import '../styles/FileUploadArea.css'

import Upload from '../icons/upload.svg?react'

// Components.
export function FileUploadArea({
    displayName = 'Upload file here',
    onUpload,
    allowedFileTypes,
}: {
    displayName: string | null
    onUpload: (files: FileList | null) => void
    allowedFileTypes?: string[]
}): JSX.Element {
    // Check allowed file types.
    if (allowedFileTypes && allowedFileTypes.length > 0) {
        allowedFileTypes = allowedFileTypes.map((type) => {
            type = type.trim()
            if (type.startsWith('.')) {
                return type
            }
            return `.${type}`
        })
    }

    return (
        <label htmlFor="upload-file-input" className="file-upload-area-component">
            <Upload />
            {displayName}
            <input
                id="upload-file-input"
                type="file"
                multiple
                accept={allowedFileTypes?.join(',')}
                onChange={(e) => onUpload(e.target.files)}
            />
        </label>
    )
}
