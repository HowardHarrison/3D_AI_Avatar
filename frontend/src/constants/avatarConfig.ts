import type { ExpressionName, GazeTarget, GestureName, HeadMotionName } from "../types/animation";

/**
 * Central avatar configuration. Do not scatter camera or asset URLs in components.
 * Default framing shows more of the body; drag to orbit horizontally, scroll to zoom.
 */
export const avatarConfig = {
  /** Cache-bust when the body GLB changes so the browser does not keep an old file. */
  modelUrl: "/avatars/ai_boy.glb?v=10",
  /** Stylized face GLB parented to the body ``Head`` bone (Option 1 face socket). */
  faceUrl: "/avatars/face.glb",
  /** Expression mask textures (face pack). See FacePackRegistry. */
  faceMaskBasePath: "/avatars/face/masks",
  /**
   * When true, attach FaceCard masks on ``Head`` (blank stylized stand-in).
   * Painted-face characters (e.g. AI Boy) must leave this false.
   * Override per character with ``VITE_AVATAR_USE_FACE_PACK`` — no code change.
   */
  useFacePack: false,
  camera: {
    /** Pulled back + mid-body aim so legs are visible; orbit still works around target. */
    position: [0, 1.15, 3.0] as [number, number, number],
    target: [0, 1.0, 0] as [number, number, number],
    fov: 36,
    /** Horizontal-first orbit (azimuth free; polar clamped near level). */
    orbit: {
      minDistance: 1.4,
      maxDistance: 6,
      /** ~π/2 − 0.45 — allow looking down enough to see feet. */
      minPolarAngle: 1.12,
      /** ~π/2 + 0.25 — slight look-up only. */
      maxPolarAngle: 1.82,
    },
  },
  performance: {
    pixelRatioMax: 1.5,
  },
  audioUrl: "/audio/test-presenter.mp3",
} as const;

export const defaultExpression: ExpressionName = "neutral";
export const defaultGaze: GazeTarget = "camera";

export type SemanticGesture = GestureName;
export type SemanticExpression = ExpressionName;
export type SemanticHeadMotion = HeadMotionName;
