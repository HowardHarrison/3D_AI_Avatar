/**
 * Frontend environment helpers. Only VITE_* values are available in the browser.
 * Never put secrets in these variables.
 */

export interface AppEnvironment {
  appName: string;
  avatarModelUrl: string;
  enableDebugPanel: boolean;
}

/**
 * Read Vite-injected environment with safe defaults so a clean checkout still runs.
 */
export function loadEnvironment(): AppEnvironment {
  const debugRaw = import.meta.env.VITE_ENABLE_DEBUG_PANEL;
  return {
    appName: import.meta.env.VITE_APP_NAME ?? "Avatar News Presenter",
    avatarModelUrl: import.meta.env.VITE_AVATAR_MODEL_URL ?? "/avatars/presenter.glb",
    enableDebugPanel: debugRaw !== "false",
  };
}

export const environment = loadEnvironment();
