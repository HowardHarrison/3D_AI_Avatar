/**
 * Unit tests for Web Speech error mapping helpers.
 */

import { describe, expect, it } from "vitest";
import { speechErrorMessage } from "../../../features/chat/speechRecognition";

describe("speechErrorMessage", () => {
  it("explains permission denial", () => {
    expect(speechErrorMessage("not-allowed")).toMatch(/permission/i);
  });

  it("returns empty for aborted", () => {
    expect(speechErrorMessage("aborted")).toBe("");
  });
});
