/**
 * Unit tests for assistant-reply → semantic avatar reaction mapping.
 */

import { describe, expect, it } from "vitest";
import { mapReplyReaction } from "../../../features/chat/mapReplyReaction";

describe("mapReplyReaction", () => {
  it("returns neutral with no gesture for empty text", () => {
    expect(mapReplyReaction("   ")).toEqual({ expression: "neutral" });
  });

  it("nods on short affirmations without an arm gesture", () => {
    expect(mapReplyReaction("Okay.")).toEqual({
      expression: "amused",
      headMotion: "nod",
    });
  });

  it("uses concerned cues for apologies and problems", () => {
    expect(mapReplyReaction("Sorry, I cannot help with that problem.")).toEqual({
      expression: "concerned",
      gesture: "handsTogether",
      headMotion: "tiltLeft",
    });
  });

  it("keeps concerned on short apologies (not the short-nod path)", () => {
    expect(mapReplyReaction("Sorry.")).toEqual({
      expression: "concerned",
      gesture: "handsTogether",
      headMotion: "tiltLeft",
    });
  });

  it("emphasizes positive wording", () => {
    expect(mapReplyReaction("Great news — I'm glad that worked!")).toMatchObject({
      expression: "positive",
      gesture: "emphasize",
    });
  });

  it("waves openHand on greetings and *waves* stage directions", () => {
    expect(
      mapReplyReaction("Hi there! *waves hand* It’s great to see you! How’s your day going?"),
    ).toEqual({
      expression: "positive",
      gesture: "openHand",
      headMotion: "nod",
    });
    expect(mapReplyReaction("Hello! Welcome aboard.")).toMatchObject({
      gesture: "openHand",
    });
  });

  it("uses curious cues for questions", () => {
    expect(mapReplyReaction("Would you like me to try another approach?")).toEqual({
      expression: "curious",
      gesture: "openHand",
      headMotion: "tiltRight",
    });
  });

  it("uses openHand for ordinary mid-length replies", () => {
    const reply =
      "Here is a short explanation of how the avatar reacts while chatting with you today.";
    expect(reply.length).toBeGreaterThan(80);
    expect(reply.length).toBeLessThanOrEqual(160);
    expect(mapReplyReaction(reply)).toEqual({
      expression: "neutral",
      gesture: "openHand",
    });
  });
});
