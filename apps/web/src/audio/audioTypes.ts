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
  dispose(): void;
}
