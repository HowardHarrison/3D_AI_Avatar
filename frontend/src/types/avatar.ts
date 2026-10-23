/**
 * Public avatar runtime contract. UI must use this API only.
 */

import type { ExpressionName, GazeTarget, GestureName, HeadMotionName } from "./animation";
import type { AvatarRuntimeStatus } from "./events";

/** Semantic facade over Three.js mixers, bones, and morph targets. */
export interface AvatarController {
  playGesture(name: GestureName): void;
  setExpression(name: ExpressionName): void;
  setHeadMotion(name: HeadMotionName): void;
  setGaze(target: GazeTarget): void;
  startSpeaking(): void;
  stopSpeaking(): void;
  reset(): void;
  /**
   * Load a same-origin audio URL for local playback (debug / Phase 1).
   * @param url - Audio file URL relative to the web app origin.
   */
  loadAudio(url: string): Promise<void>;
  /** Start playback of the currently loaded clip. */
  playAudio(): void;
  /** Pause playback without resetting current time. */
  pauseAudio(): void;
  /** Stop playback and rewind to the start of the clip. */
  stopAudio(): void;
  /**
   * Play speech from a URL: speaking state while audio plays, idle when it ends.
   * @param url - Playable audio URL (e.g. `/api/v1/tts/audio/...mp3`).
   */
  speakFromUrl(url: string): Promise<void>;
  /** Snapshot for the debug panel; not intended as per-frame React state. */
  getStatus(): AvatarRuntimeStatus;
}
