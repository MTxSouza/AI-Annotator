import { JSX } from 'react'

import '../styles/FileUploadArea.css'

import Upload from '../icons/upload.svg?react'

// Components.
export function FileUploadArea({ displayName }: { displayName?: string }): JSX.Element {
    // Check display name.
    if (!displayName) {
        displayName = 'Upload file here'
    }

    return (
        <label htmlFor="upload-file-input" className="file-upload-area-component">
            <Upload />
            {displayName}
            <input id="upload-file-input" type="file" />
        </label>
    )
}
