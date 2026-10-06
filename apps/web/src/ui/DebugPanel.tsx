/**
 * Development debug panel. Disable with VITE_ENABLE_DEBUG_PANEL=false.
 */

import { useEffect, useState } from "react";
import type { AvatarRuntimeStatus } from "@avatar/shared";
import { AvatarRuntime } from "../avatar/AvatarRuntime";
import type { AvatarHandle } from "../avatar/avatarTypes";
import { useAudio } from "../hooks/useAudio";
import { AnimationControls } from "./AnimationControls";
import { StatusPanel } from "./StatusPanel";

interface DebugPanelProps {
  controller: AvatarHandle | null;
  loadError: string | null;
}

const EMPTY_STATUS: AvatarRuntimeStatus = {
  loaded: false,
  state: "IDLE",
  activeAnimation: "none",
  currentExpression: "neutral",
  audioTime: 0,
  audioDuration: 0,
  fps: 0,
  warnings: [],
};

export function DebugPanel(props: DebugPanelProps): JSX.Element {
  const { controller, loadError } = props;
  const audio = useAudio(controller);
  const [status, setStatus] = useState<AvatarRuntimeStatus>(EMPTY_STATUS);
  const [audioMessage, setAudioMessage] = useState<string | null>(null);

  useEffect(() => {
    const id = window.setInterval(() => {
      if (controller instanceof AvatarRuntime) {
        const snapshot = controller.getStatus();
        setStatus({
          loaded: snapshot.loaded,
          state: snapshot.state,
          activeAnimation: snapshot.activeAnimation,
          currentExpression: snapshot.currentExpression,
          audioTime: snapshot.audioTime,
          audioDuration: snapshot.audioDuration,
          fps: snapshot.fps,
          warnings: snapshot.warnings,
        });
        if (snapshot.audioError) {
          setAudioMessage(snapshot.audioError);
        }
      }
    }, 250);
    return () => window.clearInterval(id);
  }, [controller]);

  return (
    <aside className="debug-panel">
      <h2>Debug</h2>
      <AnimationControls controller={controller} />
      <div className="debug-section">
        <h3>Audio</h3>
        <div className="debug-row">
          <button
            type="button"
            onClick={() => {
              void audio.loadTestAudio().catch(() => {
                setAudioMessage("Failed to load audio.");
              });
            }}
          >
            Load Audio
          </button>
          <button type="button" onClick={() => audio.play()}>
            Play
          </button>
          <button type="button" onClick={() => audio.pause()}>
            Pause
          </button>
          <button type="button" onClick={() => audio.stop()}>
            Stop
          </button>
        </div>
      </div>
      <StatusPanel
        loaded={status.loaded}
        fps={status.fps}
        state={status.state}
        activeAnimation={status.activeAnimation}
        currentExpression={status.currentExpression}
        audioTime={status.audioTime}
        audioDuration={status.audioDuration}
        message={loadError ?? audioMessage}
        warnings={status.warnings}
      />
    </aside>
  );
}
