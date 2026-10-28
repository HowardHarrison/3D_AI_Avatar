/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_NAME: string;
  readonly VITE_AVATAR_MODEL_URL: string;
  readonly VITE_AVATAR_FACE_URL: string;
  readonly VITE_ENABLE_DEBUG_PANEL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
