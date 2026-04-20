/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_APP_DEVELOP: string
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}
