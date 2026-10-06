import { describe, expect, it } from "vitest";
import {
  animationRegistry,
  isExpressionName,
  isGestureName,
  isHeadMotionName,
  resolveExpressionClip,
  resolveGestureClip,
  resolveHeadClip,
} from "../../../../services/avatar/animation/AnimationRegistry";

describe("AnimationRegistry", () => {
  it("maps semantic gestures to clip names", () => {
    expect(resolveGestureClip("openHand")).toBe("Gesture_OpenHand");
    expect(resolveGestureClip("emphasize")).toBe("Gesture_Emphasize");
    expect(resolveGestureClip("pointLeft")).toBe("Gesture_PointLeft");
    expect(resolveGestureClip("pointRight")).toBe("Gesture_PointRight");
    expect(resolveGestureClip("handsTogether")).toBe("Gesture_HandsTogether");
  });

  it("maps semantic expressions to clip names", () => {
    expect(resolveExpressionClip("neutral")).toBe("Emotion_Neutral");
    expect(resolveExpressionClip("serious")).toBe("Emotion_Serious");
    expect(resolveExpressionClip("positive")).toBe("Emotion_Positive");
    expect(resolveExpressionClip("concerned")).toBe("Emotion_Concerned");
  });

  it("maps semantic head motions to clip names", () => {
    expect(resolveHeadClip("nod")).toBe(animationRegistry.head.nod);
    expect(isHeadMotionName("tiltLeft")).toBe(true);
  });

  it("rejects invalid semantic names", () => {
    expect(() => resolveGestureClip("unknown")).toThrow(/Unknown gesture/);
    expect(() => resolveExpressionClip("angry")).toThrow(/Unknown expression/);
    expect(() => resolveHeadClip("spin")).toThrow(/Unknown head motion/);
    expect(isGestureName("emphasize")).toBe(true);
    expect(isExpressionName("positive")).toBe(true);
    expect(isGestureName("7")).toBe(false);
  });
});
