/**
 * Maps semantic application names to GLB animation clip names.
 * Never expose numeric clip indexes to UI or AI layers.
 */

import type {
  ExpressionName,
  GestureName,
  HeadMotionName,
  IdleName,
  LocomotionName,
} from "../../../types/animation";

export const animationRegistry = {
  idle: {
    neutral: "Idle_Neutral",
    breathing: "Idle_Breathing",
    shiftWeight: "Idle_ShiftWeight",
    standAttention: "Idle_StandAttention",
    adjustPosture: "Idle_AdjustPosture",
  } satisfies Record<IdleName, string>,
  locomotion: {
    walkForward: "Walk_Forward",
    walkBackward: "Walk_Backward",
  } satisfies Record<LocomotionName, string>,
  gestures: {
    openHand: "Gesture_OpenHand",
    wave: "Gesture_Wave",
    raiseHand: "Gesture_RaiseHand",
    raiseHandLeft: "Gesture_RaiseHandLeft",
    emphasize: "Gesture_Emphasize",
    pointLeft: "Gesture_PointLeft",
    pointRight: "Gesture_PointRight",
    handsTogether: "Gesture_HandsTogether",
    bothHands: "Gesture_BothHands",
    shrug: "Gesture_Shrug",
    leanForward: "Gesture_LeanForward",
    leanBack: "Gesture_LeanBack",
  } satisfies Record<GestureName, string>,
  expressions: {
    neutral: "Emotion_Neutral",
    serious: "Emotion_Serious",
    positive: "Emotion_Positive",
    concerned: "Emotion_Concerned",
    // No dedicated Emotion_* clips yet — reuse nearest clip; morphs carry the look.
    amused: "Emotion_Positive",
    curious: "Emotion_Serious",
  } satisfies Record<ExpressionName, string>,
  head: {
    nod: "Head_Nod_Small",
    turnLeft: "Head_Turn_Left",
    turnRight: "Head_Turn_Right",
    tiltLeft: "Head_Tilt_Left",
    tiltRight: "Head_Tilt_Right",
    shakeHead: "Head_Shake",
  } satisfies Record<HeadMotionName, string>,
  blink: "Blink",
} as const;

const GESTURE_NAMES = new Set<string>(Object.keys(animationRegistry.gestures));
const EXPRESSION_NAMES = new Set<string>(Object.keys(animationRegistry.expressions));
const HEAD_NAMES = new Set<string>(Object.keys(animationRegistry.head));
const IDLE_NAMES = new Set<string>(Object.keys(animationRegistry.idle));
const LOCOMOTION_NAMES = new Set<string>(Object.keys(animationRegistry.locomotion));

/**
 * Resolve a semantic idle pose to a GLB clip name.
 * @throws Error when the semantic name is not in the registry.
 */
export function resolveIdleClip(name: string): string {
  if (!IDLE_NAMES.has(name)) {
    throw new Error(`Unknown idle: ${name}`);
  }
  return animationRegistry.idle[name as IdleName];
}

/**
 * Resolve a semantic locomotion cycle to a GLB clip name.
 * @throws Error when the semantic name is not in the registry.
 */
export function resolveLocomotionClip(name: string): string {
  if (!LOCOMOTION_NAMES.has(name)) {
    throw new Error(`Unknown locomotion: ${name}`);
  }
  return animationRegistry.locomotion[name as LocomotionName];
}

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

export function isIdleName(name: string): name is IdleName {
  return IDLE_NAMES.has(name);
}

export function isLocomotionName(name: string): name is LocomotionName {
  return LOCOMOTION_NAMES.has(name);
}
