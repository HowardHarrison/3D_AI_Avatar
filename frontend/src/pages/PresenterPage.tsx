/**
 * Presenter page: 3D studio plus optional debug controls.
 */

import { useCallback, useMemo, useState } from "react";
import { environment } from "../constants/environment";
import { AvatarScene } from "../features/avatar/components/AvatarScene";
import { DebugPanel } from "../features/avatar/components/DebugPanel";
import { useAvatar } from "../features/avatar/hooks/useAvatar";
import type { AvatarHandle } from "../types";
import { PresenterLayout } from "../layouts/PresenterLayout";

function supportsWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl"));
  } catch {
    return false;
  }
}

export function PresenterPage(): JSX.Element {
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
      <PresenterLayout>
        <p className="status-error">
          WebGL is not available in this browser, so the 3D presenter cannot be rendered.
        </p>
      </PresenterLayout>
    );
  }

  return (
    <PresenterLayout>
      <AvatarScene className="scene" onReady={onReady} onError={onError} />
      {environment.enableDebugPanel ? (
        <DebugPanel controller={controller} loadError={loadError} />
      ) : null}
      {loadError && !environment.enableDebugPanel ? (
        <p className="status-error overlay-error">{loadError}</p>
      ) : null}
    </PresenterLayout>
  );
}
