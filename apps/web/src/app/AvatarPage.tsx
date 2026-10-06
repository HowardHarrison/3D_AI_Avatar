/**
 * Presenter page: 3D studio plus optional debug controls.
 */

import { useCallback, useMemo, useState } from "react";
import { AvatarScene } from "../avatar/components/AvatarScene";
import type { AvatarHandle } from "../avatar/avatarTypes";
import { environment } from "../config/environment";
import { useAvatar } from "../hooks/useAvatar";
import { DebugPanel } from "../ui/DebugPanel";

function supportsWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl"));
  } catch {
    return false;
  }
}

export function AvatarPage(): JSX.Element {
  const { controller, setController } = useAvatar();
  const [loadError, setLoadError] = useState<string | null>(null);
  const webgl = useMemo(() => supportsWebGL(), []);

  const onReady = useCallback(
    (handle: AvatarHandle) => {
      setLoadError(null);
      setController(handle);
    },
    [setController],
  );

  const onError = useCallback((message: string) => {
    setLoadError(message);
  }, []);

  if (!webgl) {
    return (
      <main className="page">
        <p className="status-error">
          WebGL is not available in this browser, so the 3D presenter cannot be rendered.
        </p>
      </main>
    );
  }

  return (
    <main className="page">
      <AvatarScene className="scene" onReady={onReady} onError={onError} />
      {environment.enableDebugPanel ? (
        <DebugPanel controller={controller} loadError={loadError} />
      ) : null}
      {loadError && !environment.enableDebugPanel ? (
        <p className="status-error overlay-error">{loadError}</p>
      ) : null}
    </main>
  );
}
