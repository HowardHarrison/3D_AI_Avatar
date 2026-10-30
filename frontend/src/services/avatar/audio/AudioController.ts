/**
 * Local HTMLAudioElement playback. No secrets; URLs come from the app/backend.
 */

import { logger } from "../../../utils/logger";
import type { AudioControllerApi } from "./audioTypes";

export class AudioController implements AudioControllerApi {
  private element: HTMLAudioElement | null = null;
  private loadedUrl: string | null = null;
  private lastError: string | null = null;
  private readonly endedListeners = new Set<() => void>();
  private audioContext: AudioContext | null = null;
  private mediaSource: MediaElementAudioSourceNode | null = null;
  private analyser: AnalyserNode | null = null;
  private analyserData: Float32Array<ArrayBuffer> | null = null;
  private readonly onNativeEnded = (): void => {
    this.endedListeners.forEach((listener) => listener());
  };

  getError(): string | null {
    return this.lastError;
  }

  /**
   * Create/resume AudioContext during a user gesture (e.g. Send click)
   * so playback after async TTS is not stuck suspended/silent.
   */
  unlock(): void {
    const ContextCtor =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!ContextCtor) {
      return;
    }
    if (!this.audioContext || this.audioContext.state === "closed") {
      this.audioContext = new ContextCtor();
    }
    if (this.audioContext.state === "suspended") {
      void this.audioContext.resume();
    }
  }

  /**
   * Load a playable audio URL. Replaces any previous element.
   */
  async load(url: string): Promise<void> {
    this.disposeElement();
    this.lastError = null;
    const audio = new Audio();
    audio.preload = "auto";
    // Required when routing through Web Audio (analyser) across origins / proxy.
    audio.crossOrigin = "anonymous";
    audio.src = url;
    audio.addEventListener("ended", this.onNativeEnded);
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
    try {
      this.ensureAnalyser();
    } catch (error: unknown) {
      // Keep HTMLAudioElement playback if Web Audio wiring fails.
      logger.warn("Audio analyser setup failed; playing without lip-sync amplitude.", error);
    }

    const start = (): void => {
      void this.element?.play().catch((error: unknown) => {
        this.lastError = "Audio playback was blocked or failed.";
        logger.error(this.lastError, error);
      });
    };

    // New contexts start suspended; resume after TTS await or sound is silent.
    if (this.audioContext && this.audioContext.state === "suspended") {
      void this.audioContext.resume().then(start).catch(start);
      return;
    }
    start();
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

  onEnded(listener: () => void): () => void {
    this.endedListeners.add(listener);
    return () => {
      this.endedListeners.delete(listener);
    };
  }

  dispose(): void {
    this.endedListeners.clear();
    this.disposeElement();
    void this.audioContext?.close();
    this.audioContext = null;
  }

  private disposeElement(): void {
    if (this.element) {
      this.element.removeEventListener("ended", this.onNativeEnded);
      this.element.pause();
      this.element.src = "";
    }
    this.analyser?.disconnect();
    this.mediaSource?.disconnect();
    // Keep AudioContext alive across loads — closing it each clip leaves the next
    // context suspended after async TTS, which mutes MediaElementSource output.
    this.analyser = null;
    this.mediaSource = null;
    this.analyserData = null;

    this.element = null;
    this.loadedUrl = null;
  }

  /**
   * Wire Web Audio analyser once per element (createMediaElementSource is one-shot).
   */
  private ensureAnalyser(): void {
    if (!this.element || this.mediaSource) {
      return;
    }
    const ContextCtor =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!ContextCtor) {
      return;
    }
    if (!this.audioContext || this.audioContext.state === "closed") {
      this.audioContext = new ContextCtor();
    }
    this.mediaSource = this.audioContext.createMediaElementSource(this.element);
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 256;
    this.analyser.smoothingTimeConstant = 0.85;
    this.mediaSource.connect(this.analyser);
    this.analyser.connect(this.audioContext.destination);
    this.analyserData = new Float32Array(new ArrayBuffer(this.analyser.fftSize * 4));
  }

  /** RMS amplitude mapped roughly into 0…1 for mouth drive. */
  getAmplitude(): number {
    if (!this.analyser || !this.analyserData) {
      return 0;
    }
    this.analyser.getFloatTimeDomainData(this.analyserData);
    let sum = 0;
    for (let i = 0; i < this.analyserData.length; i += 1) {
      const sample = this.analyserData[i] ?? 0;
      sum += sample * sample;
    }
    const rms = Math.sqrt(sum / this.analyserData.length);
    // Empirically scale TTS levels; clamp. Tune 4–8 if mouth is too shy/loud.
    return Math.min(1, Math.max(0, rms * 6));
  }
}
