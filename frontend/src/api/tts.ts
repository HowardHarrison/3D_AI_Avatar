/**
 * TTS HTTP client. Calls the backend; never holds provider secrets.
 */

import { readErrorDetail } from "./httpError";

export interface SynthesizeSpeechResult {
  audioUrl: string;
  durationSeconds: number;
}

/**
 * POST text and receive a relative audio URL to play.
 *
 * @param text - Words to speak.
 * @param apiBaseUrl - Origin of the API (empty = same origin / Vite proxy).
 */
export async function synthesizeSpeech(
  text: string,
  apiBaseUrl = "",
): Promise<SynthesizeSpeechResult> {
  const base = apiBaseUrl.replace(/\/$/, "");
  const response = await fetch(`${base}/api/v1/tts/synthesize`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error(await readErrorDetail(response, "TTS request failed"));
  }

  const body = (await response.json()) as {
    audioUrl?: string;
    durationSeconds?: number;
  };
  if (typeof body.audioUrl !== "string" || !body.audioUrl) {
    throw new Error("TTS response missing audioUrl.");
  }
  return {
    audioUrl: body.audioUrl,
    durationSeconds: typeof body.durationSeconds === "number" ? body.durationSeconds : 0,
  };
}

/**
 * Join API base + relative audio path for playback.
 */
export function resolveAudioUrl(audioUrl: string, apiBaseUrl = ""): string {
  if (/^https?:\/\//i.test(audioUrl)) {
    return audioUrl;
  }
  const base = apiBaseUrl.replace(/\/$/, "");
  return `${base}${audioUrl.startsWith("/") ? "" : "/"}${audioUrl}`;
}
