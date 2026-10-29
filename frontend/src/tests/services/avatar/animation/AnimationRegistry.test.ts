import { describe, expect, it } from "vitest";
import {
  animationRegistry,
  isExpressionName,
  isGestureName,
  isHeadMotionName,
  isIdleName,
  isLocomotionName,
  resolveExpressionClip,
  resolveGestureClip,
  resolveHeadClip,
  resolveIdleClip,
  resolveLocomotionClip,
} from "../../../../services/avatar/animation/AnimationRegistry";

describe("AnimationRegistry", () => {
  it("maps semantic idles to clip names", () => {
    expect(resolveIdleClip("breathing")).toBe("Idle_Breathing");
    expect(resolveIdleClip("standAttention")).toBe("Idle_StandAttention");
    expect(isIdleName("standAttention")).toBe(true);
    expect(resolveIdleClip("adjustPosture")).toBe("Idle_AdjustPosture");
    expect(isIdleName("adjustPosture")).toBe(true);
    expect(isIdleName("dance")).toBe(false);
  });

  it("maps semantic locomotion to clip names", () => {
    expect(resolveLocomotionClip("walkForward")).toBe("Walk_Forward");
    expect(isLocomotionName("walkForward")).toBe(true);
    expect(resolveLocomotionClip("walkBackward")).toBe("Walk_Backward");
    expect(isLocomotionName("walkBackward")).toBe(true);
    expect(isLocomotionName("fly")).toBe(false);
    expect(() => resolveLocomotionClip("fly")).toThrow(/Unknown locomotion/);
  });

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
    expect(resolveGestureClip("leanForward")).toBe("Gesture_LeanForward");
    expect(resolveGestureClip("leanBack")).toBe("Gesture_LeanBack");
    expect(isGestureName("leanForward")).toBe(true);
    expect(resolveGestureClip("turnBodyLeft")).toBe("Turn_Body_Left");
    expect(resolveGestureClip("turnBodyRight")).toBe("Turn_Body_Right");
    expect(isGestureName("turnBodyLeft")).toBe(true);
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
    expect(() => resolveIdleClip("dance")).toThrow(/Unknown idle/);
    expect(isGestureName("emphasize")).toBe(true);
    expect(isExpressionName("positive")).toBe(true);
    expect(isGestureName("7")).toBe(false);
  });
});
