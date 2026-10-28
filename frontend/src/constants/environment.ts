/**
 * Frontend environment helpers. Only VITE_* values are available in the browser.
 * Never put secrets in these variables.
 */

export interface AppEnvironment {
  appName: string;
  avatarModelUrl: string;
  /** Optional override for the Head-socket face GLB. */
  avatarFaceUrl: string;
  enableDebugPanel: boolean;
  /**
   * Backend origin for chat/API calls.
   * Empty string = same origin (Vite dev proxy `/api` → backend).
   */
  apiBaseUrl: string;
}

/**
 * Read Vite-injected environment with safe defaults so a clean checkout still runs.
 */
export function loadEnvironment(): AppEnvironment {
  const debugRaw = import.meta.env.VITE_ENABLE_DEBUG_PANEL;
  const apiBase = import.meta.env.VITE_API_BASE_URL;
  return {
    appName: import.meta.env.VITE_APP_NAME ?? "Stylized Chatbot Avatar",
    avatarModelUrl: import.meta.env.VITE_AVATAR_MODEL_URL ?? "/avatars/presenter.glb",
    avatarFaceUrl: import.meta.env.VITE_AVATAR_FACE_URL ?? "/avatars/face.glb",
    enableDebugPanel: debugRaw !== "false",
    apiBaseUrl: typeof apiBase === "string" ? apiBase.trim() : "",
  };
}

export const environment = loadEnvironment();
