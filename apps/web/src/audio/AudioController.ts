/**
 * Local HTMLAudioElement playback for Phase 1. No backend streaming.
 */

import { logger } from "../logging/logger";
import type { AudioControllerApi } from "./audioTypes";

export class AudioController implements AudioControllerApi {
  private element: HTMLAudioElement | null = null;
  private loadedUrl: string | null = null;
  private lastError: string | null = null;

  getError(): string | null {
    return this.lastError;
  }

  /**
   * Load a same-origin audio URL. Replaces any previous element.
   */
  async load(url: string): Promise<void> {
    this.dispose();
    this.lastError = null;
    const audio = new Audio();
    audio.preload = "auto";
    audio.src = url;
    this.element = audio;
    this.loadedUrl = url;
    await new Promise<void>((resolve, reject) => {
      const onReady = (): void => {
        cleanup();
        resolve();
      };
      const onError = (): void => {
        cleanup();
        this.lastError = "Failed to load audio.";
        logger.error(this.lastError, url);
        reject(new Error(this.lastError));
      };
      const cleanup = (): void => {
        audio.removeEventListener("canplaythrough", onReady);
        audio.removeEventListener("error", onError);
      };
      audio.addEventListener("canplaythrough", onReady);
      audio.addEventListener("error", onError);
      audio.load();
    });
  }

  play(): void {
    if (!this.element) {
      this.lastError = "Audio is not loaded.";
      logger.warn(this.lastError);
      return;
    }
    void this.element.play().catch((error: unknown) => {
      this.lastError = "Audio playback was blocked or failed.";
      logger.error(this.lastError, error);
    });
  }

  pause(): void {
    this.element?.pause();
  }

  stop(): void {
    if (!this.element) {
      return;
    }
    this.element.pause();
    this.element.currentTime = 0;
  }

  getCurrentTime(): number {
    return this.element?.currentTime ?? 0;
  }

  getDuration(): number {
    const duration = this.element?.duration;
    return Number.isFinite(duration) ? (duration as number) : 0;
  }

  getLoadedUrl(): string | null {
    return this.loadedUrl;
  }

  dispose(): void {
    if (this.element) {
      this.element.pause();
      this.element.src = "";
    }
    this.element = null;
    this.loadedUrl = null;
  }
}
