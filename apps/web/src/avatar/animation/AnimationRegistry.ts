/**
 * Maps semantic application names to GLB animation clip names.
 * Never expose numeric clip indexes to UI or AI layers.
 */

import type { ExpressionName, GestureName, HeadMotionName } from "@avatar/shared";

export const animationRegistry = {
  idle: {
    neutral: "Idle_Neutral",
    breathing: "Idle_Breathing",
    shiftWeight: "Idle_ShiftWeight",
  },
  gestures: {
    openHand: "Gesture_OpenHand",
    emphasize: "Gesture_Emphasize",
    pointLeft: "Gesture_PointLeft",
    pointRight: "Gesture_PointRight",
    handsTogether: "Gesture_HandsTogether",
  } satisfies Record<GestureName, string>,
  expressions: {
    neutral: "Emotion_Neutral",
    serious: "Emotion_Serious",
    positive: "Emotion_Positive",
    concerned: "Emotion_Concerned",
  } satisfies Record<ExpressionName, string>,
  head: {
    nod: "Head_Nod_Small",
    turnLeft: "Head_Turn_Left",
    turnRight: "Head_Turn_Right",
    tiltLeft: "Head_Tilt_Left",
    tiltRight: "Head_Tilt_Right",
  } satisfies Record<HeadMotionName, string>,
  blink: "Blink",
} as const;

const GESTURE_NAMES = new Set<string>(Object.keys(animationRegistry.gestures));
const EXPRESSION_NAMES = new Set<string>(Object.keys(animationRegistry.expressions));
const HEAD_NAMES = new Set<string>(Object.keys(animationRegistry.head));

/**
 * Resolve a semantic gesture to a GLB clip name.
 * @throws Error when the semantic name is not in the registry.
 */
export function resolveGestureClip(name: string): string {
  if (!GESTURE_NAMES.has(name)) {
    throw new Error(`Unknown gesture: ${name}`);
  }
  return animationRegistry.gestures[name as GestureName];
}

/**
 * Resolve a semantic expression to a GLB clip name.
 * @throws Error when the semantic name is not in the registry.
 */
export function resolveExpressionClip(name: string): string {
  if (!EXPRESSION_NAMES.has(name)) {
    throw new Error(`Unknown expression: ${name}`);
  }
  return animationRegistry.expressions[name as ExpressionName];
}

/**
 * Resolve a semantic head motion to a GLB clip name.
 * @throws Error when the semantic name is not in the registry.
 */
export function resolveHeadClip(name: string): string {
  if (!HEAD_NAMES.has(name)) {
    throw new Error(`Unknown head motion: ${name}`);
  }
  return animationRegistry.head[name as HeadMotionName];
}

export function isGestureName(name: string): name is GestureName {
  return GESTURE_NAMES.has(name);
}

export function isExpressionName(name: string): name is ExpressionName {
  return EXPRESSION_NAMES.has(name);
}

export function isHeadMotionName(name: string): name is HeadMotionName {
  return HEAD_NAMES.has(name);
}
