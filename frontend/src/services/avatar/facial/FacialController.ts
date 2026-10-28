/**
 * Face expression driver. Semantic names only — no mask URLs or morph indexes in UI.
 *
 * Production path: face-pack masks crossfaded on FaceCard (FaceMaskLayer).
 * Morph presets remain available for mouth/blink layers on the face socket only.
 */

import { Mesh, Object3D } from "three";
import type { ExpressionName } from "../../../types/animation";
import { logger } from "../../../utils/logger";
import { FaceMaskLayer } from "./FaceMaskLayer";
import { resolveFaceMask } from "./FacePackRegistry";
import type { FaceMaskSpec } from "./facialTypes";

interface MorphMesh {
  mesh: Mesh;
  dictionary: Record<string, number>;
}

export class FacialController {
  private readonly morphMeshes: MorphMesh[] = [];
  private current: ExpressionName = "neutral";
  private activeMask: FaceMaskSpec = resolveFaceMask("neutral");
  private readonly missing = new Set<string>();
  private readonly masks = new FaceMaskLayer();
  private faceBound = false;

  /**
   * @param onWarning Optional reporter for missing assets / face bind issues.
   * Does not bind body meshes — call ``retargetTo`` after ``attachFace``.
   */
  constructor(private readonly onWarning?: (message: string) => void) {}

  /**
   * Point the face driver at the face socket (never the Mixamo body).
   * Starts mask preload; morphs optional for mouth/blink later.
   */
  retargetTo(root: Object3D): void {
    this.resetInfluences();
    this.morphMeshes.length = 0;
    this.missing.clear();
    this.current = "neutral";
    this.activeMask = resolveFaceMask("neutral");
    this.collectMorphMeshes(root);
    this.masks.bind(root);
    this.faceBound = true;
    void this.masks.preload().then(() => {
      this.masks.setExpression(this.current, this.activeMask.crossfadeMs);
    });
  }

  private collectMorphMeshes(root: Object3D): void {
    root.traverse((child) => {
      if (child instanceof Mesh && child.morphTargetDictionary && child.morphTargetInfluences) {
        this.morphMeshes.push({
          mesh: child,
          dictionary: child.morphTargetDictionary,
        });
      }
    });
    if (this.morphMeshes.length === 0) {
      // Expected while masks carry emotion; mouth morphs arrive in a later step.
      return;
    }
    this.resetInfluences();
  }

  getExpression(): ExpressionName {
    return this.current;
  }

  /** Active face-pack mask for the current expression (for loaders / debug). */
  getActiveMask(): FaceMaskSpec {
    return this.activeMask;
  }

  /**
   * Apply a named expression via face-pack mask crossfade.
   */
  setExpression(name: ExpressionName): void {
    this.current = name;
    this.activeMask = resolveFaceMask(name);
    if (this.faceBound) {
      this.masks.setExpression(name, this.activeMask.crossfadeMs);
    }
  }

  /** Advance mask crossfade (call from AvatarRuntime.update). */
  update(delta: number): void {
    this.masks.update(delta);
  }

  /**
   * Set a single morph target by stable shape-key name (mouth / blink layers).
   */
  setBlendShape(name: string, value: number): void {
    if (this.morphMeshes.length === 0) {
      return;
    }
    const clamped = Math.min(1, Math.max(0, value));
    let found = false;
    for (const entry of this.morphMeshes) {
      const index = entry.dictionary[name];
      if (index === undefined || !entry.mesh.morphTargetInfluences) {
        continue;
      }
      entry.mesh.morphTargetInfluences[index] = clamped;
      found = true;
    }
    if (!found) {
      this.warn(`Facial shape key "${name}" not found.`);
    }
  }

  reset(): void {
    this.resetInfluences();
    this.current = "neutral";
    this.activeMask = resolveFaceMask("neutral");
    if (this.faceBound) {
      this.masks.setExpression("neutral", this.activeMask.crossfadeMs);
    }
  }

  dispose(): void {
    this.masks.dispose();
    this.faceBound = false;
  }

  private resetInfluences(): void {
    for (const entry of this.morphMeshes) {
      const influences = entry.mesh.morphTargetInfluences;
      if (!influences) {
        continue;
      }
      for (let i = 0; i < influences.length; i += 1) {
        influences[i] = 0;
      }
    }
  }

  private warn(message: string): void {
    if (this.missing.has(message)) {
      return;
    }
    this.missing.add(message);
    logger.warn(message);
    this.onWarning?.(message);
  }
}
