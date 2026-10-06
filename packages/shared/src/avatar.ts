/**
 * Public avatar runtime contract. UI and future AI code must use this API only.
 */

import type { ExpressionName, GazeTarget, GestureName, HeadMotionName } from "./animation";

/** Semantic facade over Three.js mixers, bones, and morph targets. */
export interface AvatarController {
  playGesture(name: GestureName): void;
  setExpression(name: ExpressionName): void;
  setHeadMotion(name: HeadMotionName): void;
  setGaze(target: GazeTarget): void;
  startSpeaking(): void;
  stopSpeaking(): void;
  reset(): void;
}
