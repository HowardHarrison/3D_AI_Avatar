/**
 * Unit tests for the TTS HTTP client.
 */

import { afterEach, describe, expect, it, vi } from "vitest";
import { resolveAudioUrl, synthesizeSpeech } from "../../api/tts";

describe("synthesizeSpeech", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns audioUrl and duration on success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          audioUrl: "/api/v1/tts/audio/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.mp3",
          durationSeconds: 2.5,
        }),
      }),
    );

    await expect(synthesizeSpeech("Hello", "")).resolves.toEqual({
      audioUrl: "/api/v1/tts/audio/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.mp3",
      durationSeconds: 2.5,
    });
  });
});

describe("resolveAudioUrl", () => {
  it("prefixes api base for relative paths", () => {
    expect(resolveAudioUrl("/api/v1/tts/audio/x.mp3", "http://localhost:8000")).toBe(
      "http://localhost:8000/api/v1/tts/audio/x.mp3",
    );
  });

  it("keeps absolute URLs", () => {
    expect(resolveAudioUrl("https://cdn.example/a.mp3", "http://localhost:8000")).toBe(
      "https://cdn.example/a.mp3",
    );
  });
});
