/**
 * Parse and validate semantic animation plans. The runtime does not care whether
 * a plan came from a hardcoded script, an LLM, or a future FastAPI backend.
 */

import type {
  AnimationPlan,
  AnimationSegment,
  ExpressionName,
  GazeTarget,
  GestureName,
  HeadMotionName,
} from "../../../types";
import { isExpressionName, isGestureName, isHeadMotionName } from "./AnimationRegistry";

const GAZE: GazeTarget[] = ["camera", "left", "right", "down"];

export class AnimationPlanError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AnimationPlanError";
  }
}

/**
 * Validate a raw JSON-like plan and return a typed AnimationPlan.
 * @throws AnimationPlanError when required fields are missing or invalid.
 */
export function parseAnimationPlan(input: unknown): AnimationPlan {
  if (typeof input !== "object" || input === null || !("segments" in input)) {
    throw new AnimationPlanError("Animation plan must include a segments array.");
  }
  const segmentsRaw = (input as { segments: unknown }).segments;
  if (!Array.isArray(segmentsRaw)) {
    throw new AnimationPlanError("Animation plan segments must be an array.");
  }
  const segments = segmentsRaw.map((segment, index) => parseSegment(segment, index));
  return { segments };
}

function parseSegment(segment: unknown, index: number): AnimationSegment {
  if (typeof segment !== "object" || segment === null) {
    throw new AnimationPlanError(`Segment ${index} must be an object.`);
  }
  const record = segment as Record<string, unknown>;
  const start = record.start;
  const end = record.end;
  if (typeof start !== "number" || typeof end !== "number") {
    throw new AnimationPlanError(`Segment ${index} must include numeric start and end.`);
  }
  if (end < start) {
    throw new AnimationPlanError(`Segment ${index} end must be >= start.`);
  }
  const parsed: AnimationSegment = { start, end };
  if (record.emotion !== undefined) {
    if (typeof record.emotion !== "string" || !isExpressionName(record.emotion)) {
      throw new AnimationPlanError(`Segment ${index} has an invalid emotion.`);
    }
    parsed.emotion = record.emotion as ExpressionName;
  }
  if (record.gesture !== undefined) {
    if (typeof record.gesture !== "string" || !isGestureName(record.gesture)) {
      throw new AnimationPlanError(`Segment ${index} has an invalid gesture.`);
    }
    parsed.gesture = record.gesture as GestureName;
  }
  if (record.headMotion !== undefined) {
    if (typeof record.headMotion !== "string" || !isHeadMotionName(record.headMotion)) {
      throw new AnimationPlanError(`Segment ${index} has an invalid headMotion.`);
    }
    parsed.headMotion = record.headMotion as HeadMotionName;
  }
  if (record.gaze !== undefined) {
    if (typeof record.gaze !== "string" || !GAZE.includes(record.gaze as GazeTarget)) {
      throw new AnimationPlanError(`Segment ${index} has an invalid gaze.`);
    }
    parsed.gaze = record.gaze as GazeTarget;
  }
  return parsed;
}
