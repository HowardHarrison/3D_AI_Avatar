/**
 * Chat turn state: message list, draft input, and send → API → avatar reaction.
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
}

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

  const send = useCallback(async () => {
    const text = draft.trim();
    if (!text || busy) {
      return;
    }

    setDraft("");
    setBusy(true);
    setError(null);
    setMessages((prev) => [...prev, { id: nextId(), role: "user", text }]);

    try {
      const reply = await postChatTurn(text, environment.apiBaseUrl);
      setMessages((prev) => [...prev, { id: nextId(), role: "assistant", text: reply }]);
      if (controller) {
        playAssistantReaction(controller, reply);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Chat request failed.";
      setError(message);
    } finally {
      setBusy(false);
    }
  }, [busy, controller, draft]);

  return { messages, draft, setDraft, busy, error, send };
}
