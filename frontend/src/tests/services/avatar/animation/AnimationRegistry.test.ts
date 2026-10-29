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
    expect(resolveGestureClip("bothHands")).toBe("Gesture_BothHands");
    expect(isGestureName("bothHands")).toBe(true);
    expect(resolveGestureClip("wave")).toBe("Gesture_Wave");
    expect(isGestureName("wave")).toBe(true);
    expect(resolveGestureClip("raiseHand")).toBe("Gesture_RaiseHand");
    expect(isGestureName("raiseHand")).toBe(true);
    expect(resolveGestureClip("raiseHandLeft")).toBe("Gesture_RaiseHandLeft");
    expect(isGestureName("raiseHandLeft")).toBe(true);
    expect(resolveGestureClip("shrug")).toBe("Gesture_Shrug");
    expect(isGestureName("shrug")).toBe(true);
  });

  it("maps semantic expressions to clip names", () => {
    expect(resolveExpressionClip("neutral")).toBe("Emotion_Neutral");
    expect(resolveExpressionClip("serious")).toBe("Emotion_Serious");
    expect(resolveExpressionClip("positive")).toBe("Emotion_Positive");
    expect(resolveExpressionClip("concerned")).toBe("Emotion_Concerned");
    expect(resolveExpressionClip("amused")).toBe("Emotion_Positive");
    expect(resolveExpressionClip("curious")).toBe("Emotion_Serious");
    expect(isExpressionName("amused")).toBe(true);
    expect(isExpressionName("curious")).toBe(true);
  });

  it("maps semantic head motions to clip names", () => {
    expect(resolveHeadClip("nod")).toBe(animationRegistry.head.nod);
    expect(isHeadMotionName("tiltLeft")).toBe(true);
    expect(resolveHeadClip("shakeHead")).toBe("Head_Shake");
    expect(isHeadMotionName("shakeHead")).toBe(true);
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
