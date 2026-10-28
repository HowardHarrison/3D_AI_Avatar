/**
 * Development debug panel. Disable with VITE_ENABLE_DEBUG_PANEL=false.
 * Closable to a right-edge bubble so the avatar can use full width.
 */

import { useEffect, useState } from "react";
import type { AvatarRuntimeStatus } from "../../../types/events";
import { StatusPanel } from "../../../components/StatusPanel";
import { useAudio } from "../hooks/useAudio";
import type { AvatarHandle } from "../types";
import { AnimationControls } from "./AnimationControls";

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
  audioError: null,
};

export function DebugPanel(props: DebugPanelProps): JSX.Element {
  const { controller, loadError } = props;
  const audio = useAudio(controller);
  const [status, setStatus] = useState<AvatarRuntimeStatus>(EMPTY_STATUS);
  const [audioMessage, setAudioMessage] = useState<string | null>(null);
  const [closed, setClosed] = useState(false);

  useEffect(() => {
    const id = window.setInterval(() => {
      if (controller !== null) {
        const snapshot = controller.getStatus();
        setStatus(snapshot);
        if (snapshot.audioError) {
          setAudioMessage(snapshot.audioError);
        }
      }
    }, 250);
    return () => window.clearInterval(id);
  }, [controller]);

  if (closed) {
    return (
      <button
        type="button"
        className="debug-bubble"
        onClick={() => setClosed(false)}
        aria-label="Open debug panel"
        title="Open debug panel"
      >
        Debug
      </button>
    );
  }

  return (
    <aside className="debug-panel" aria-label="Debug panel">
      <div className="debug-panel__title-row">
        <h2>Debug</h2>
        <button
          type="button"
          className="debug-panel__close"
          onClick={() => setClosed(true)}
          aria-label="Close debug panel"
          title="Close debug panel"
        >
          ×
        </button>
      </div>
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
