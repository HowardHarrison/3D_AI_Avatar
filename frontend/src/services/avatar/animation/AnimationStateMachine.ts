/**
 * Finite state machine for presenter animation phases.
 * Transition rules stay independent of Three.js so they can be unit-tested.
 */

import type { AnimationStateName } from "../../../types/animation";

const ALLOWED: Record<AnimationStateName, AnimationStateName[]> = {
  IDLE: ["GESTURE", "SPEAKING", "TRANSITION", "LOCOMOTION"],
  GESTURE: ["IDLE", "TRANSITION", "SPEAKING", "LOCOMOTION"],
  SPEAKING: ["IDLE", "GESTURE", "TRANSITION", "LOCOMOTION"],
  TRANSITION: ["IDLE", "GESTURE", "SPEAKING", "LOCOMOTION"],
  LOCOMOTION: ["IDLE", "GESTURE", "SPEAKING", "TRANSITION", "LOCOMOTION"],
};

export class AnimationStateMachine {
  private current: AnimationStateName = "IDLE";
  private speakingHeld = false;

  /** Return the current high-level animation state. */
  getState(): AnimationStateName {
    return this.current;
  }

  /**
   * Attempt a state change. Illegal transitions are ignored and return false.
   */
  transitionTo(next: AnimationStateName): boolean {
    if (this.current === next) {
      return true;
    }
    if (!ALLOWED[this.current].includes(next)) {
      return false;
    }
    this.current = next;
    return true;
  }

  /** Convenience: start a one-shot gesture from idle, speaking, or locomotion. */
  playGesture(): boolean {
    if (
      this.current === "IDLE" ||
      this.current === "SPEAKING" ||
      this.current === "TRANSITION" ||
      this.current === "LOCOMOTION"
    ) {
      this.current = "GESTURE";
      return true;
    }
    return false;
  }

  /** Convenience: gesture clip finished. */
  gestureFinished(): boolean {
    if (this.current === "GESTURE" || this.current === "TRANSITION") {
      this.current = this.speakingHeld ? "SPEAKING" : "IDLE";
      return true;
    }
    return false;
  }

  /** Enter looping locomotion (walk, etc.). */
  startLocomotion(): boolean {
    if (
      this.current === "IDLE" ||
      this.current === "SPEAKING" ||
      this.current === "LOCOMOTION" ||
      this.current === "TRANSITION"
    ) {
      this.current = "LOCOMOTION";
      return true;
    }
    return false;
  }

  /** Leave locomotion; prefer SPEAKING if speech is still held. */
  stopLocomotion(): boolean {
    if (this.current !== "LOCOMOTION") {
      return false;
    }
    this.current = this.speakingHeld ? "SPEAKING" : "IDLE";
    return true;
  }

  /** Mark that speech is active so gestures return to SPEAKING instead of IDLE. */
  startSpeaking(): void {
    this.speakingHeld = true;
    this.current = "SPEAKING";
  }

  /** End speech and return to idle unless a gesture or locomotion is in progress. */
  stopSpeaking(): void {
    this.speakingHeld = false;
    if (this.current !== "GESTURE" && this.current !== "LOCOMOTION") {
      this.current = "IDLE";
    }
  }

  reset(): void {
    this.speakingHeld = false;
    this.current = "IDLE";
  }
}
