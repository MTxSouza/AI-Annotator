// Types.
export type DialogType = 'error' | 'info' | 'warning'

// Interfaces.
export interface DialogMessage {
    id: number
    type: DialogType
    message: string
    status_code: number | null
}
