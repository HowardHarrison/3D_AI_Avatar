/**
 * Semantic animation identifiers. UI and runtime use these names, never clip indexes.
 */

/** High-level gesture commands accepted by AvatarController.playGesture. */
export type GestureName =
  | "openHand"
  | "emphasize"
  | "pointLeft"
  | "pointRight"
  | "handsTogether"
  /** Both arms raised overhead (chat “both hands”). */
  | "bothHands";

/** Facial expression commands accepted by AvatarController.setExpression. */
export type ExpressionName =
  | "neutral"
  | "serious"
  | "positive"
  | "concerned"
  /** Soft smile + cheeks — short affirmations / light warmth. */
  | "amused"
  /** Raised inner brow — questions / wondering. */
  | "curious";

/** Head motion commands accepted by AvatarController.setHeadMotion. */
export type HeadMotionName =
  | "nod"
  | "turnLeft"
  | "turnRight"
  | "tiltLeft"
  | "tiltRight"
  | "shakeHead";

/** Gaze targets for setGaze. Phase 1 supports camera and left/right look. */
export type GazeTarget = "camera" | "left" | "right" | "down";

/**
 * Conceptual animation layers. Phase 1 uses these as priorities, not a full
 * production layered mixer.
 */
export const AnimationLayerPriority = {
  idle: 0,
  headMotion: 10,
  gesture: 20,
  expression: 30,
  speechLipSync: 40,
  override: 100,
} as const;

/** Discrete runtime states for the animation state machine. */
export type AnimationStateName = "IDLE" | "SPEAKING" | "GESTURE" | "TRANSITION";

/** Options for playing a named clip through AnimationController. */
export interface PlayAnimationOptions {
  loop?: boolean;
  fadeInSeconds?: number;
  fadeOutSeconds?: number;
  timeScale?: number;
  /** When true, fade out the current looping clip (gestures). Head overlays set this false. */
  exclusive?: boolean;
}

/** One timed slice of a future LLM/backend animation plan. */
export interface AnimationSegment {
  start: number;
  end: number;
  emotion?: ExpressionName;
  gesture?: GestureName;
  headMotion?: HeadMotionName;
  gaze?: GazeTarget;
}

/** A sequence of semantic animation segments independent of the data source. */
export interface AnimationPlan {
  segments: AnimationSegment[];
}
