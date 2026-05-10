export interface File {
    _id: string
    project_id_list: string[]
    file_hash: string
    filename: string
    file_format: string
    size_in_bytes: number
    created_at: string
    updated_at: string
}
