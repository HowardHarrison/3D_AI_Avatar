import type { ExpressionName } from "../../../types/animation";

export type { ExpressionName };

/** Internal facial pose applied by FacialController morph fallback. */
export type BlendShapeMap = Record<string, number>;

/**
 * One expression mask in the face pack.
 * ``url`` is a texture (or later a small face-card mesh asset) mapped onto the face area.
 */
export interface FaceMaskSpec {
  /** Same as semantic ExpressionName (stable id for assets and logs). */
  id: ExpressionName;
  /** Public URL under ``/avatars/face/masks/``. */
  url: string;
  /** Crossfade duration when switching to this mask. */
  crossfadeMs: number;
}
