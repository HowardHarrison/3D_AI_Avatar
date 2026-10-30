/**
 * Amplitude → mouth overlay while speaking. Not phoneme/viseme sync.
 */

import type { AudioController } from "./AudioController";
import type { FacialController } from "../facial/FacialController";

export class LipSyncController {
  private smoothed = 0;
  private display = 0;
  private active = false;

  constructor(
    private readonly audio: AudioController,
    private readonly facial: FacialController,
  ) {}

  /** Begin driving mouth from amplitude (call when SPEAKING starts). */
  start(): void {
    this.active = true;
    this.smoothed = 0;
    this.display = 0;
  }

  /** Stop and close the mouth. */
  stop(): void {
    this.active = false;
    this.smoothed = 0;
    this.display = 0;
    this.facial.setBlendShape("mouth_open", 0);
  }

  /**
   * Sample audio and update mouth_open with two-stage smoothing.
   * @param delta Seconds since last frame (for smoothing).
   */
  update(delta: number): void {
    if (!this.active) {
      return;
    }
    const dt = Math.max(0, delta);
    const target = this.audio.getAmplitude();
    // Gentle chase — high rates looked like flicker on TTS amplitude spikes.
    const ampRate = target > this.smoothed ? 10 : 6;
    const ampT = 1 - Math.exp(-ampRate * dt);
    this.smoothed += (target - this.smoothed) * ampT;

    // Soft floor (smoothstep) avoids hard 0↔open pops near silence.
    const gated = softGate(this.smoothed, 0.03, 0.12);
    const desired = Math.min(1, gated * 1.15);

    const mouthRate = desired > this.display ? 8 : 5;
    const mouthT = 1 - Math.exp(-mouthRate * dt);
    this.display += (desired - this.display) * mouthT;
    if (this.display < 0.01) {
      this.display = 0;
    }

    this.facial.setBlendShape("mouth_open", this.display);
  }
}

/** Hermite smoothstep gate: 0 below lo, 1 above hi, smooth in between. */
function softGate(value: number, lo: number, hi: number): number {
  if (value <= lo) {
    return 0;
  }
  if (value >= hi) {
    return 1;
  }
  const t = (value - lo) / (hi - lo);
  return t * t * (3 - 2 * t);
}