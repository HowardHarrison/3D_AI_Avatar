/**
 * Three.js AnimationMixer wrapper. Callers pass clip names from the registry,
 * never numeric indexes.
 */

import {
  AnimationAction,
  AnimationClip,
  AnimationMixer,
  LoopOnce,
  LoopRepeat,
  Object3D,
} from "three";
import type { PlayAnimationOptions } from "../../../types/animation";
import { logger } from "../../../utils/logger";

export class AnimationController {
  private readonly mixer: AnimationMixer;
  private readonly clips = new Map<string, AnimationClip>();
  private readonly actions = new Map<string, AnimationAction>();
  private activeLoop: string | null = null;
  private readonly finishedListeners = new Set<(clipName: string) => void>();
  private disposed = false;

  /**
   * @param root Scene or avatar root that owns the animated nodes.
   * @param clips All GLB animation clips.
   */
  constructor(root: Object3D, clips: AnimationClip[]) {
    this.mixer = new AnimationMixer(root);
    for (const clip of clips) {
      this.clips.set(clip.name, clip);
    }
    this.mixer.addEventListener("finished", (event: { action?: AnimationAction }) => {
      const clipName = event.action?.getClip().name;
      if (clipName) {
        this.finishedListeners.forEach((listener) => listener(clipName));
      }
    });
  }

  /** Register a callback when a one-shot clip completes. */
  onFinished(listener: (clipName: string) => void): () => void {
    this.finishedListeners.add(listener);
    return () => this.finishedListeners.delete(listener);
  }

  /** Whether a clip with this exact GLB name exists. */
  hasClip(name: string): boolean {
    return this.clips.has(name);
  }

  /** Names of clips loaded from the GLB. */
  listClips(): string[] {
    return [...this.clips.keys()];
  }

  getActiveAnimation(): string {
    return this.activeLoop ?? "";
  }

  /**
   * Play a clip by GLB name with optional crossfade.
   * Missing names log a warning and do not throw.
   */
  play(name: string, options?: PlayAnimationOptions): void {
    if (this.disposed) {
      return;
    }
    const clip = this.clips.get(name);
    if (!clip) {
      logger.warn(`Animation "${name}" not found.`);
      return;
    }
    const fadeIn = options?.fadeInSeconds ?? 0.3;
    const fadeOut = options?.fadeOutSeconds ?? 0.3;
    const loop = options?.loop ?? false;
    const exclusive = options?.exclusive ?? true;
    const action = this.mixer.clipAction(clip);
    this.actions.set(name, action);
    action.reset();
    action.enabled = true;
    action.timeScale = options?.timeScale ?? 1;
    action.setLoop(loop ? LoopRepeat : LoopOnce, loop ? Infinity : 1);
    action.clampWhenFinished = !loop;
    if (exclusive && this.activeLoop && this.activeLoop !== name) {
      const previous = this.actions.get(this.activeLoop);
      previous?.fadeOut(fadeOut);
      if (!loop) {
        this.activeLoop = null;
      }
    }
    action.fadeIn(fadeIn);
    action.play();
    if (loop) {
      this.activeLoop = name;
    }
  }

  stop(name?: string): void {
    if (name) {
      this.actions.get(name)?.stop();
      if (this.activeLoop === name) {
        this.activeLoop = null;
      }
      return;
    }
    this.stopAll();
  }

  stopAll(): void {
    this.mixer.stopAllAction();
    this.activeLoop = null;
  }

  update(delta: number): void {
    if (!this.disposed) {
      this.mixer.update(delta);
    }
  }

  dispose(): void {
    this.stopAll();
    this.mixer.uncacheRoot(this.mixer.getRoot());
    this.finishedListeners.clear();
    this.disposed = true;
  }
}
