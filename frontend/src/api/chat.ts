/**
 * Chat turn HTTP client. Calls the backend; never holds LLM secrets.
 */

import { readErrorDetail } from "./httpError";

export interface ChatTurnResponse {
  reply: string;
}

/**
 * POST one user message and return the assistant reply text.
 *
 * @param message - User utterance (non-empty).
 * @param apiBaseUrl - Origin of the API (empty string = same origin / Vite proxy).
 * @throws Error when the network fails or the API returns a non-OK status.
 */
export async function postChatTurn(message: string, apiBaseUrl = ""): Promise<string> {
  const base = apiBaseUrl.replace(/\/$/, "");
  const url = `${base}/api/v1/chat/turns`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error(await readErrorDetail(response, "Chat request failed"));
  }

  const body = (await response.json()) as ChatTurnResponse;
  if (typeof body.reply !== "string" || !body.reply.trim()) {
    throw new Error("Chat response missing reply text.");
  }
  return body.reply.trim();
}
