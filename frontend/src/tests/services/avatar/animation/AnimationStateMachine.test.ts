import { describe, expect, it } from "vitest";
import { AnimationStateMachine } from "../../../../services/avatar/animation/AnimationStateMachine";

describe("AnimationStateMachine", () => {
  it("transitions IDLE to GESTURE and back to IDLE", () => {
    const machine = new AnimationStateMachine();
    expect(machine.getState()).toBe("IDLE");
    expect(machine.playGesture()).toBe(true);
    expect(machine.getState()).toBe("GESTURE");
    expect(machine.gestureFinished()).toBe(true);
    expect(machine.getState()).toBe("IDLE");
  });

  it("transitions IDLE to SPEAKING", () => {
    const machine = new AnimationStateMachine();
    machine.startSpeaking();
    expect(machine.getState()).toBe("SPEAKING");
  });

  it("returns to SPEAKING after a gesture while speaking", () => {
    const machine = new AnimationStateMachine();
    machine.startSpeaking();
    expect(machine.playGesture()).toBe(true);
    expect(machine.getState()).toBe("GESTURE");
    expect(machine.gestureFinished()).toBe(true);
    expect(machine.getState()).toBe("SPEAKING");
  });

  it("enters LOCOMOTION from IDLE and returns on stop", () => {
    const machine = new AnimationStateMachine();
    expect(machine.startLocomotion()).toBe(true);
    expect(machine.getState()).toBe("LOCOMOTION");
    expect(machine.stopLocomotion()).toBe(true);
    expect(machine.getState()).toBe("IDLE");
  });

  it("allows a gesture to interrupt locomotion", () => {
    const machine = new AnimationStateMachine();
    expect(machine.startLocomotion()).toBe(true);
    expect(machine.playGesture()).toBe(true);
    expect(machine.getState()).toBe("GESTURE");
  });
});
