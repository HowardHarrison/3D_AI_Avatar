/**
 * Minimal text chat UI. Calls the backend chat turn API; avatar reacts via semantic API.
 */

import type { FormEvent } from "react";
import type { AvatarHandle } from "../../../types";
import { useChatTurn } from "../hooks/useChatTurn";

interface ChatPanelProps {
  controller: AvatarHandle | null;
}

export function ChatPanel(props: ChatPanelProps): JSX.Element {
  const { controller } = props;
  const { messages, draft, setDraft, busy, error, send } = useChatTurn(controller);

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    void send();
  };

  return (
    <section className="chat-panel" aria-label="Chat">
      <header className="chat-panel__header">
        <h2>Chat</h2>
        <p className="chat-panel__hint">Type a message — the avatar will react when it replies.</p>
      </header>

      <ul className="chat-panel__messages">
        {messages.length === 0 ? (
          <li className="chat-panel__empty">Say hello to start.</li>
        ) : (
          messages.map((item) => (
            <li
              key={item.id}
              className={
                item.role === "user" ? "chat-panel__msg chat-panel__msg--user" : "chat-panel__msg"
              }
            >
              <span className="chat-panel__role">{item.role === "user" ? "You" : "Avatar"}</span>
              <p>{item.text}</p>
            </li>
          ))
        )}
      </ul>

      {error ? <p className="status-error chat-panel__error">{error}</p> : null}

      <form className="chat-panel__form" onSubmit={onSubmit}>
        <label className="visually-hidden" htmlFor="chat-input">
          Message
        </label>
        <input
          id="chat-input"
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder={controller ? "Type a message…" : "Waiting for avatar…"}
          disabled={busy || !controller}
          autoComplete="off"
        />
        <button type="submit" disabled={busy || !controller || !draft.trim()}>
          {busy ? "…" : "Send"}
        </button>
      </form>
    </section>
  );
}
