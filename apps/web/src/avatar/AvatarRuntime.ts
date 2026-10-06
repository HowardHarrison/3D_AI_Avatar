/**
 * Avatar runtime: semantic API over mixers, morphs, idle, and local audio.
 * React must not manipulate bones, morph targets, or the AnimationMixer.
 */

import { Bone, Object3D, AnimationClip } from "three";
import type {
  AnimationStateName,
  AvatarController,
  ExpressionName,
  GazeTarget,
  GestureName,
  HeadMotionName,
} from "@avatar/shared";
import { AudioController } from "../audio/AudioController";
import { logger } from "../logging/logger";
import { AnimationController } from "./animation/AnimationController";
import { AnimationStateMachine } from "./animation/AnimationStateMachine";
import {
  isExpressionName,
  isGestureName,
  isHeadMotionName,
  resolveExpressionClip,
  resolveGestureClip,
  resolveHeadClip,
} from "./animation/AnimationRegistry";
import { IdleController } from "./animation/IdleController";
import { FacialController } from "./facial/FacialController";

export class AvatarRuntime implements AvatarController {
  readonly animation: AnimationController;
  readonly facial: FacialController;
  readonly idle: IdleController;
  readonly audio: AudioController;
  readonly state: AnimationStateMachine;
  private readonly warnings: string[] = [];
  private gestureClip: string | null = null;
  private fps = 0;
  private fpsAccum = 0;
  private fpsFrames = 0;
  private readonly head: Object3D | null;
  private unsubscribeFinished: () => void;

  constructor(root: Object3D, clips: AnimationClip[]) {
    this.animation = new AnimationController(root, clips);
    this.facial = new FacialController(root, (message) => this.pushWarning(message));
    this.idle = new IdleController(root, this.animation, this.facial);
    this.audio = new AudioController();
    this.state = new AnimationStateMachine();
    this.head = root.getObjectByName("Head") ?? null;
    this.unsubscribeFinished = this.animation.onFinished((clipName) => {
      if (clipName === this.gestureClip) {
        this.gestureClip = null;
        this.state.gestureFinished();
        this.idle.start();
      }
    });
    this.assertArmature(root);
    this.idle.start();
  }

  playGesture(name: GestureName): void {
    if (!isGestureName(name)) {
      this.pushWarning(`Unknown gesture: ${name}`);
      return;
    }
    const clip = resolveGestureClip(name);
    if (!this.animation.hasClip(clip)) {
      this.pushWarning(`Animation "${clip}" not found.`);
      return;
    }
    this.state.playGesture();
    this.gestureClip = clip;
    this.animation.play(clip, {
      loop: false,
      exclusive: true,
      fadeInSeconds: 0.25,
      fadeOutSeconds: 0.25,
    });
  }

  setExpression(name: ExpressionName): void {
    if (!isExpressionName(name)) {
      this.pushWarning(`Unknown expression: ${name}`);
      return;
    }
    this.facial.setExpression(name);
    const clip = resolveExpressionClip(name);
    if (this.animation.hasClip(clip)) {
      this.animation.play(clip, { loop: false, exclusive: false, fadeInSeconds: 0.2 });
    }
  }

  setHeadMotion(name: HeadMotionName): void {
    if (!isHeadMotionName(name)) {
      this.pushWarning(`Unknown head motion: ${name}`);
      return;
    }
    const clip = resolveHeadClip(name);
    if (!this.animation.hasClip(clip)) {
      this.pushWarning(`Animation "${clip}" not found.`);
      return;
    }
    this.animation.play(clip, { loop: false, exclusive: false, fadeInSeconds: 0.2 });
  }

  setGaze(target: GazeTarget): void {
    if (!this.head) {
      return;
    }
    const yaw = target === "left" ? 0.35 : target === "right" ? -0.35 : 0;
    const pitch = target === "down" ? 0.15 : 0;
    this.head.rotation.y = yaw;
    this.head.rotation.x = pitch;
  }

  startSpeaking(): void {
    this.state.startSpeaking();
  }

  stopSpeaking(): void {
    this.state.stopSpeaking();
    if (this.state.getState() === "IDLE") {
      this.idle.start();
    }
  }

  reset(): void {
    this.gestureClip = null;
    this.state.reset();
    this.facial.reset();
    this.setGaze("camera");
    this.animation.stopAll();
    this.idle.start();
  }

  update(delta: number): void {
    this.animation.update(delta);
    this.idle.update(delta, this.state.getState() === "GESTURE");
    this.fpsAccum += delta;
    this.fpsFrames += 1;
    if (this.fpsAccum >= 0.5) {
      this.fps = this.fpsFrames / this.fpsAccum;
      this.fpsAccum = 0;
      this.fpsFrames = 0;
    }
  }

  getStatus(): {
    loaded: boolean;
    state: AnimationStateName;
    activeAnimation: string;
    currentExpression: string;
    audioTime: number;
    audioDuration: number;
    fps: number;
    warnings: string[];
    audioError: string | null;
  } {
    return {
      loaded: true,
      state: this.state.getState(),
      activeAnimation: this.animation.getActiveAnimation() || this.gestureClip || "none",
      currentExpression: this.facial.getExpression(),
      audioTime: this.audio.getCurrentTime(),
      audioDuration: this.audio.getDuration(),
      fps: this.fps,
      warnings: [...this.warnings],
      audioError: this.audio.getError(),
    };
  }

  dispose(): void {
    this.unsubscribeFinished();
    this.animation.dispose();
    this.audio.dispose();
  }

  private assertArmature(root: Object3D): void {
    let hasBone = false;
    root.traverse((child) => {
      if (child instanceof Bone || child.type === "Bone") {
        hasBone = true;
      }
    });
    if (!hasBone && !root.getObjectByName("Hips")) {
      this.pushWarning("Avatar armature bones were not detected.");
    }
  }

  private pushWarning(message: string): void {
    if (this.warnings.includes(message)) {
      return;
    }
    this.warnings.push(message);
    logger.warn(message);
  }
}
