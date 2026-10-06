import type { ExpressionName, GazeTarget, GestureName, HeadMotionName } from "../types/animation";

/**
 * Central presenter configuration. Do not scatter camera or asset URLs in components.
 */
export const avatarConfig = {
  modelUrl: "/avatars/presenter.glb",
  camera: {
    position: [0, 1.65, 3.2] as [number, number, number],
    target: [0, 1.4, 0] as [number, number, number],
    fov: 35,
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
