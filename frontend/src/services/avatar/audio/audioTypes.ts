/**
 * Local audio playback contract used by the debug panel and AvatarRuntime.
 */
export interface AudioControllerApi {
  load(url: string): Promise<void>;
  play(): void;
  pause(): void;
  stop(): void;
  getCurrentTime(): number;
  getDuration(): number;
  /** Register a listener for natural playback end; returns an unsubscribe. */
  onEnded(listener: () => void): () => void;
  dispose(): void;
  /**
  * Current speech amplitude in 0…1 (0 when silent / not analysing).
  * Used by amplitude lip-sync; not for UI.
  */
  getAmplitude(): number;
}
