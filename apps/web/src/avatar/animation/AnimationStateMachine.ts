/**
 * Finite state machine for presenter animation phases.
 * Transition rules stay independent of Three.js so they can be unit-tested.
 */

import type { AnimationStateName } from "@avatar/shared";

const ALLOWED: Record<AnimationStateName, AnimationStateName[]> = {
  IDLE: ["GESTURE", "SPEAKING", "TRANSITION"],
  GESTURE: ["IDLE", "TRANSITION", "SPEAKING"],
  SPEAKING: ["IDLE", "GESTURE", "TRANSITION"],
  TRANSITION: ["IDLE", "GESTURE", "SPEAKING"],
};

export class AnimationStateMachine {
  private current: AnimationStateName = "IDLE";

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

  /** Convenience: start a one-shot gesture from idle or speaking. */
  playGesture(): boolean {
    if (this.current === "IDLE" || this.current === "SPEAKING" || this.current === "TRANSITION") {
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

  private speakingHeld = false;

  /** Mark that speech is active so gestures return to SPEAKING instead of IDLE. */
  startSpeaking(): void {
    this.speakingHeld = true;
    this.current = "SPEAKING";
  }

  /** End speech and return to idle unless a gesture is in progress. */
  stopSpeaking(): void {
    this.speakingHeld = false;
    if (this.current !== "GESTURE") {
      this.current = "IDLE";
    }
  }

  reset(): void {
    this.speakingHeld = false;
    this.current = "IDLE";
  }
}
