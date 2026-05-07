/// <reference types="vite/client" />
/// <reference types="vite-plugin-svgr/client" />

interface ImportMetaEnv {
    readonly VITE_APP_DEVELOP: string
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}
