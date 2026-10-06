/**
 * Event shapes reserved for later lip-sync. Phase 1 does not play visemes.
 */

/** Timed viseme instruction that a future LipSyncController will consume. */
export interface VisemeEvent {
  time: number;
  duration: number;
  viseme: string;
}

/** Lightweight status snapshot for the debug panel (not per-frame React state). */
export interface AvatarRuntimeStatus {
  loaded: boolean;
  state: string;
  activeAnimation: string;
  currentExpression: string;
  audioTime: number;
  audioDuration: number;
  fps: number;
  warnings: string[];
  /** Last local-audio failure, or null when none. */
  audioError: string | null;
}
