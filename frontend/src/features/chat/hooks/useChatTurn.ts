/**
 * Chat turn state: message list, draft input, and send → API (with history) → avatar.
 */

import { useCallback, useState } from "react";
import { postChatTurn } from "../../../api/chat";
import { environment } from "../../../constants/environment";
import type { AvatarHandle } from "../../../types";
import { playAssistantReaction } from "../playAssistantReaction";

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  text: string;
}

export interface UseChatTurnResult {
  messages: ChatMessage[];
  draft: string;
  setDraft: (value: string) => void;
  busy: boolean;
  error: string | null;
  send: () => Promise<void>;
  /** Send an explicit utterance (used by mic STT). */
  sendText: (text: string) => Promise<void>;
}

/** Match backend cap so older turns drop from the request, not from the UI list. */
const MAX_HISTORY_SENT = 12;

function nextId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

/**
 * @param controller - Avatar handle; may be null until the GLB is ready.
 */
export function useChatTurn(controller: AvatarHandle | null): UseChatTurnResult {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendText = useCallback(
    async (raw: string) => {
      const text = raw.trim();
      if (!text || busy) {
        return;
      }

      const history = messages.slice(-MAX_HISTORY_SENT).map((item) => ({
        role: item.role,
        content: item.text,
      }));

      setDraft("");
      setBusy(true);
      setError(null);
      setMessages((prev) => [...prev, { id: nextId(), role: "user", text }]);

      try {
        const reply = await postChatTurn(text, {
          apiBaseUrl: environment.apiBaseUrl,
          history,
        });
        setMessages((prev) => [...prev, { id: nextId(), role: "assistant", text: reply }]);
        if (controller) {
          await playAssistantReaction(controller, reply, environment.apiBaseUrl, text);
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : "Chat request failed.";
        setError(message);
      } finally {
        setBusy(false);
      }
    },
    [busy, controller, messages],
  );

  const send = useCallback(async () => {
    await sendText(draft);
  }, [draft, sendText]);

  return { messages, draft, setDraft, busy, error, send, sendText };
}
