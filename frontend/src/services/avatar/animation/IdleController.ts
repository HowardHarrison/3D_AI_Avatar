/**
 * Subtle idle life: breathing clip, jittered blinks, eye wander, occasional head motion.
 * Updates run on the render loop, not through React state.
 */

import { Object3D } from "three";
import { animationRegistry } from "./AnimationRegistry";
import type { AnimationController } from "./AnimationController";
import type { FacialController } from "../facial/FacialController";

function randomBetween(min: number, max: number): number {
  return min + Math.random() * (max - min);
}

export class IdleController {
  private blinkTimer = randomBetween(3, 6);
  private blinkPhase: "open" | "closing" | "closed" | "opening" = "open";
  private blinkValue = 0;
  private eyeTimer = randomBetween(2, 4);
  private eyeX = 0;
  private eyeY = 0;
  private targetEyeX = 0;
  private targetEyeY = 0;
  private headTimer = randomBetween(6, 12);
  private readonly leftEye: Object3D | null;
  private readonly rightEye: Object3D | null;

  constructor(
    root: Object3D,
    private readonly animation: AnimationController,
    private readonly facial: FacialController,
  ) {
    this.leftEye = root.getObjectByName("LeftEye") ?? null;
    this.rightEye = root.getObjectByName("RightEye") ?? null;
  }

  /** Begin looping idle/breathing clips. */
  start(): void {
    if (this.animation.hasClip(animationRegistry.idle.breathing)) {
      this.animation.play(animationRegistry.idle.breathing, {
        loop: true,
        fadeInSeconds: 0.4,
      });
      return;
    }
    if (this.animation.hasClip(animationRegistry.idle.neutral)) {
      this.animation.play(animationRegistry.idle.neutral, { loop: true, fadeInSeconds: 0.4 });
    }
  }

  /**
   * Advance idle behaviours.
   * @param delta Seconds since last frame.
   * @param gesturesLocked When true, skip head clips so they do not fight a gesture.
   */
  update(delta: number, gesturesLocked: boolean): void {
    this.updateBlink(delta);
    this.updateEyes(delta);
    if (!gesturesLocked) {
      this.updateHead(delta);
    }
  }

  private updateBlink(delta: number): void {
    if (this.blinkPhase === "open") {
      this.blinkTimer -= delta;
      if (this.blinkTimer <= 0) {
        this.blinkPhase = "closing";
      }
      return;
    }
    if (this.blinkPhase === "closing") {
      this.blinkValue = Math.min(1, this.blinkValue + delta * 12);
      this.applyBlink(this.blinkValue);
      if (this.blinkValue >= 1) {
        this.blinkPhase = "closed";
        this.blinkTimer = 0.05;
      }
      return;
    }
    if (this.blinkPhase === "closed") {
      this.blinkTimer -= delta;
      if (this.blinkTimer <= 0) {
        this.blinkPhase = "opening";
      }
      return;
    }
    this.blinkValue = Math.max(0, this.blinkValue - delta * 10);
    this.applyBlink(this.blinkValue);
    if (this.blinkValue <= 0) {
      this.blinkPhase = "open";
      this.blinkTimer = randomBetween(3, 6);
    }
  }

  private applyBlink(value: number): void {
    this.facial.setBlendShape("eye_blink_left", value);
    this.facial.setBlendShape("eye_blink_right", value);
  }

  private updateEyes(delta: number): void {
    this.eyeTimer -= delta;
    if (this.eyeTimer <= 0) {
      this.targetEyeX = randomBetween(-0.08, 0.08);
      this.targetEyeY = randomBetween(-0.04, 0.04);
      this.eyeTimer = randomBetween(2.5, 5);
    }
    this.eyeX += (this.targetEyeX - this.eyeX) * Math.min(1, delta * 3);
    this.eyeY += (this.targetEyeY - this.eyeY) * Math.min(1, delta * 3);
    if (this.leftEye) {
      this.leftEye.rotation.y = this.eyeX;
      this.leftEye.rotation.x = this.eyeY;
    }
    if (this.rightEye) {
      this.rightEye.rotation.y = this.eyeX;
      this.rightEye.rotation.x = this.eyeY;
    }
  }

  private updateHead(delta: number): void {
    this.headTimer -= delta;
    if (this.headTimer > 0) {
      return;
    }
    this.headTimer = randomBetween(8, 16);
    const clip = animationRegistry.head.nod;
    if (this.animation.hasClip(clip)) {
      this.animation.play(clip, {
        loop: false,
        exclusive: false,
        fadeInSeconds: 0.2,
        fadeOutSeconds: 0.3,
      });
    }
  }
}
