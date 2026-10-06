/**
 * Morph-target (shape key) facade. UI must not write morphTargetInfluences directly.
 */

import { Mesh, Object3D } from "three";
import type { ExpressionName } from "../../../types/animation";
import { logger } from "../../../utils/logger";

const EXPRESSION_SHAPES: Record<ExpressionName, Record<string, number>> = {
  neutral: {},
  serious: { brow_down: 0.7, mouth_frown: 0.35, mouth_close: 0.2 },
  positive: { mouth_smile: 0.85, brow_up: 0.25, eye_wide: 0.15 },
  concerned: { brow_up: 0.45, mouth_frown: 0.5, eye_squint: 0.2 },
};

interface MorphMesh {
  mesh: Mesh;
  dictionary: Record<string, number>;
}

export class FacialController {
  private readonly morphMeshes: MorphMesh[] = [];
  private current: ExpressionName = "neutral";
  private readonly missing = new Set<string>();

  /**
   * @param root Loaded GLB scene graph.
   * @param onWarning Optional reporter for missing shape keys.
   */
  constructor(
    root: Object3D,
    private readonly onWarning?: (message: string) => void,
  ) {
    root.traverse((child) => {
      if (child instanceof Mesh && child.morphTargetDictionary && child.morphTargetInfluences) {
        this.morphMeshes.push({
          mesh: child,
          dictionary: child.morphTargetDictionary,
        });
      }
    });
    if (this.morphMeshes.length === 0) {
      this.warn("No facial morph targets found on the avatar.");
    }
  }

  getExpression(): ExpressionName {
    return this.current;
  }

  /**
   * Apply a named expression as a set of blend-shape weights.
   */
  setExpression(name: ExpressionName): void {
    this.current = name;
    this.resetInfluences();
    const shapes = EXPRESSION_SHAPES[name];
    for (const [shape, value] of Object.entries(shapes)) {
      this.setBlendShape(shape, value);
    }
  }

  /**
   * Set a single morph target by stable shape-key name.
   */
  setBlendShape(name: string, value: number): void {
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
