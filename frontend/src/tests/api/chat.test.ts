/**
 * Unit tests for the chat turn HTTP client.
 */

import { afterEach, describe, expect, it, vi } from "vitest";
import { postChatTurn } from "../../api/chat";

describe("postChatTurn", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns reply text on success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ reply: "Hello from the avatar." }),
      }),
    );

    await expect(postChatTurn("Hi", "")).resolves.toBe("Hello from the avatar.");
    expect(fetch).toHaveBeenCalledWith(
      "/api/v1/chat/turns",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("throws with API detail on failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({ detail: "LLM_API_KEY is not set." }),
      }),
    );

    await expect(postChatTurn("Hi", "http://localhost:8000")).rejects.toThrow(
      "LLM_API_KEY is not set.",
    );
  });
});
