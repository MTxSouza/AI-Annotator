// Types.
export type DialogType = 'error' | 'info' | 'warning'

// Interfaces.
export interface dialogMessage {
    id: number
    type: DialogType
    message: string
    status_code: number | null
}
