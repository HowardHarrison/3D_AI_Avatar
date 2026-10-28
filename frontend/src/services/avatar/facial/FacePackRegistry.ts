/**
 * Maps semantic expressions to face-pack mask assets.
 * UI/chat use ExpressionName only — never mask URLs or texture indexes.
 *
 * Mask textures are the production expression path (crossfade). Morph presets on
 * the face GLB remain an interim fallback until masks are authored.
 */

import type { ExpressionName } from "../../../types/animation";
import type { FaceMaskSpec } from "./facialTypes";

/** Default crossfade when switching expression masks (milliseconds). */
export const FACE_PACK_CROSSFADE_MS = 200;

/** Directory under ``frontend/public`` for expression mask textures. */
export const FACE_MASK_BASE_PATH = "/avatars/face/masks";

function mask(id: ExpressionName): FaceMaskSpec {
  return {
    id,
    url: `${FACE_MASK_BASE_PATH}/${id}.webp`,
    crossfadeMs: FACE_PACK_CROSSFADE_MS,
  };
}

/**
 * Required face-pack entries — one mask per semantic ExpressionName.
 * Author files at these URLs (same face UV / face-card size).
 */
export const facePackRegistry = {
  neutral: mask("neutral"),
  serious: mask("serious"),
  positive: mask("positive"),
  concerned: mask("concerned"),
  amused: mask("amused"),
  curious: mask("curious"),
} as const satisfies Record<ExpressionName, FaceMaskSpec>;

/**
 * Resolve a semantic expression to its face-pack mask spec.
 * @throws Error when the name is not in the face pack.
 */
export function resolveFaceMask(name: string): FaceMaskSpec {
  if (!(name in facePackRegistry)) {
    throw new Error(`Unknown face-pack expression: ${name}`);
  }
  return facePackRegistry[name as ExpressionName];
}

export function isFacePackExpression(name: string): name is ExpressionName {
  return name in facePackRegistry;
}
