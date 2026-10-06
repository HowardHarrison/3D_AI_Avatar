import { describe, expect, it } from "vitest";
import { parseAnimationPlan } from "./parseAnimationPlan";

describe("parseAnimationPlan", () => {
  it("accepts a valid plan with start, end, emotion, gesture, headMotion, and gaze", () => {
    const plan = parseAnimationPlan({
      segments: [
        {
          start: 0,
          end: 4.2,
          emotion: "positive",
          gesture: "openHand",
          headMotion: "nod",
          gaze: "camera",
        },
      ],
    });
    expect(plan.segments).toHaveLength(1);
    expect(plan.segments[0]?.gesture).toBe("openHand");
  });

  it("rejects inverted times and unknown semantics", () => {
    expect(() => parseAnimationPlan({ segments: [{ start: 2, end: 1 }] })).toThrow(/end must be/);
    expect(() =>
      parseAnimationPlan({ segments: [{ start: 0, end: 1, gesture: "wave" }] }),
    ).toThrow(/invalid gesture/);
  });
});
