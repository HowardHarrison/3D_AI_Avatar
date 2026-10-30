/**
 * Amplitude → mouth morph while speaking. Not phoneme/viseme sync.
 */

import type { AudioController } from "./AudioController";
import type { FacialController } from "../facial/FacialController";

export class LipSyncController {
  private smoothed = 0;
  private active = false;

  constructor(
    private readonly audio: AudioController,
    private readonly facial: FacialController,
  ) {}

  /** Begin driving mouth from amplitude (call when SPEAKING starts). */
  start(): void {
    this.active = true;
    this.smoothed = 0;
  }

  /** Stop and close the mouth. */
  stop(): void {
    this.active = false;
    this.smoothed = 0;
    this.facial.setBlendShape("mouth_open", 0);
  }

  /**
   * Sample audio and update mouth_open.
   * @param delta Seconds since last frame (for smoothing).
   */
  update(delta: number): void {
    if (!this.active) {
      return;
    }
    const target = this.audio.getAmplitude();
    // Faster open, slightly slower close — reads more natural.
    const rate = target > this.smoothed ? 18 : 12;
    const t = 1 - Math.exp(-rate * Math.max(0, delta));
    this.smoothed += (target - this.smoothed) * t;
    // Floor: tiny noise stays shut; ceiling keeps stylized open readable.
    const mouth = this.smoothed < 0.04 ? 0 : Math.min(1, this.smoothed * 1.2);
    this.facial.setBlendShape("mouth_open", mouth);
  }
}