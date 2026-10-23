/**
 * Avatar runtime: semantic API over mixers, morphs, idle, and local audio.
 * React must not manipulate bones, morph targets, or the AnimationMixer.
 */

import { Bone, Object3D, AnimationClip } from "three";
import type {
  AvatarController,
  AvatarRuntimeStatus,
  ExpressionName,
  GazeTarget,
  GestureName,
  HeadMotionName,
} from "../../types";
import { logger } from "../../utils/logger";
import { AudioController } from "./audio/AudioController";
import { AnimationController } from "./animation/AnimationController";
import { AnimationStateMachine } from "./animation/AnimationStateMachine";
import {
  animationRegistry,
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
  private readonly animation: AnimationController;
  private readonly facial: FacialController;
  private readonly idle: IdleController;
  private readonly audio: AudioController;
  private readonly state: AnimationStateMachine;
  private readonly warnings: string[] = [];
  private gestureClip: string | null = null;
  private fps = 0;
  private fpsAccum = 0;
  private fpsFrames = 0;
  private readonly head: Object3D | null;
  private unsubscribeFinished: () => void;
  private speechGeneration = 0;

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
    // Drop prior head clips so Left/Right do not blend into uneven poses.
    for (const headClip of Object.values(animationRegistry.head)) {
      if (headClip !== clip) {
        this.animation.stop(headClip);
      }
    }
    // Clear direct gaze overrides so the mixer owns head rotation for this clip.
    if (this.head) {
      this.head.rotation.set(0, 0, 0);
    }
    this.animation.play(clip, { loop: false, exclusive: false, fadeInSeconds: 0.15 });
  }

  setGaze(target: GazeTarget): void {
    if (!this.head) {
      return;
    }
    // Match head-turn clip magnitude (±0.7) so gaze and Turn Left/Right agree.
    const yaw = target === "left" ? 0.7 : target === "right" ? -0.7 : 0;
    const pitch = target === "down" ? 0.25 : 0;
    this.head.rotation.set(pitch, yaw, 0);
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

  /**
   * Load a same-origin audio URL via AudioController.
   * @param url - Audio file URL relative to the web app origin.
   */
  async loadAudio(url: string): Promise<void> {
    await this.audio.load(url);
  }

  /** Start playback of the currently loaded clip. */
  playAudio(): void {
    this.audio.play();
  }

  /** Pause playback without resetting current time. */
  pauseAudio(): void {
    this.audio.pause();
  }

  /** Stop playback and rewind to the start of the clip. */
  stopAudio(): void {
    this.audio.stop();
  }

  /**
   * Load and play speech audio, holding SPEAKING until playback ends.
   */
  async speakFromUrl(url: string): Promise<void> {
    const generation = ++this.speechGeneration;
    this.audio.stop();
    await this.audio.load(url);
    if (generation !== this.speechGeneration) {
      return;
    }

    // Expression / gesture are chosen by the chat layer (mapReplyReaction), not here.
    this.startSpeaking();
    this.setGaze("camera");
    this.facial.setBlendShape("mouth_open", 0.4);

    await new Promise<void>((resolve) => {
      let settled = false;
      const finish = (): void => {
        if (settled) {
          return;
        }
        settled = true;
        unsubscribe();
        window.clearTimeout(fallbackTimer);
        if (generation !== this.speechGeneration) {
          resolve();
          return;
        }
        this.facial.setBlendShape("mouth_open", 0);
        this.stopSpeaking();
        this.setExpression("neutral");
        resolve();
      };

      const unsubscribe = this.audio.onEnded(finish);
      this.audio.play();

      const duration = this.audio.getDuration();
      const fallbackMs =
        duration > 0
          ? Math.ceil((duration + 0.35) * 1000)
          : Math.min(12000, Math.max(2500, url.length * 20));
      const fallbackTimer = window.setTimeout(finish, fallbackMs);
    });
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

  getStatus(): AvatarRuntimeStatus {
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
    this.speechGeneration += 1;
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
