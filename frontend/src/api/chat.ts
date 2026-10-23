/**
 * Chat turn HTTP client. Calls the backend; never holds LLM secrets.
 */

import { readErrorDetail } from "./httpError";

export type ChatApiRole = "user" | "assistant";

export interface ChatHistoryItem {
  role: ChatApiRole;
  content: string;
}

export interface ChatTurnResponse {
  reply: string;
}

export interface PostChatTurnOptions {
  /** Origin of the API (empty string = same origin / Vite proxy). */
  apiBaseUrl?: string;
  /** Prior turns only (do not include the current ``message``). */
  history?: ChatHistoryItem[];
}

/**
 * POST one user message (with optional history) and return the assistant reply.
 *
 * @param message - User utterance (non-empty).
 * @param options - Base URL and prior conversation turns.
 * @throws Error when the network fails or the API returns a non-OK status.
 */
export async function postChatTurn(
  message: string,
  options: PostChatTurnOptions | string = "",
): Promise<string> {
  // Back-compat: second arg used to be apiBaseUrl string.
  const opts: PostChatTurnOptions =
    typeof options === "string" ? { apiBaseUrl: options } : options;
  const apiBaseUrl = opts.apiBaseUrl ?? "";
  const history = opts.history ?? [];

  const base = apiBaseUrl.replace(/\/$/, "");
  const url = `${base}/api/v1/chat/turns`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      history: history.map((item) => ({
        role: item.role,
        content: item.content,
      })),
    }),
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
