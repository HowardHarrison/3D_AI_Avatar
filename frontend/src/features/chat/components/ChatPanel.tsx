/**
 * Text + mic chat UI. Continuous mic until Stop; then send the full transcript.
 */

import type { FormEvent } from "react";
import { useCallback } from "react";
import type { AvatarHandle } from "../../../types";
import { useChatTurn } from "../hooks/useChatTurn";
import { useSpeechToText } from "../hooks/useSpeechToText";

interface ChatPanelProps {
  controller: AvatarHandle | null;
}

export function ChatPanel(props: ChatPanelProps): JSX.Element {
  const { controller } = props;
  const { messages, draft, setDraft, busy, error, send, sendText } = useChatTurn(controller);

  const onTranscript = useCallback(
    (text: string) => {
      setDraft(text);
    },
    [setDraft],
  );

  const {
    supported: micSupported,
    listening,
    error: micError,
    start: startMic,
    stop: stopMic,
  } = useSpeechToText({ onTranscript });

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (listening) {
      const spoken = stopMic();
      if (spoken) {
        void sendText(spoken);
        return;
      }
    }
    void send();
  };

  const onMicClick = () => {
    if (busy || !controller) {
      return;
    }
    if (listening) {
      const spoken = stopMic();
      if (spoken) {
        void sendText(spoken);
      }
      return;
    }
    startMic();
  };

  const combinedError = error ?? micError;

  return (
    <section className="chat-panel" aria-label="Chat">
      <header className="chat-panel__header">
        <h2>Chat</h2>
        <p className="chat-panel__hint">
          Type, or click Mic and speak as long as you want — Stop sends the full message.
        </p>
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

      {combinedError ? <p className="status-error chat-panel__error">{combinedError}</p> : null}
      {listening ? (
        <p className="chat-panel__listening">Listening… click Stop when you finish speaking.</p>
      ) : null}

      <form className="chat-panel__form" onSubmit={onSubmit}>
        <label className="visually-hidden" htmlFor="chat-input">
          Message
        </label>
        <input
          id="chat-input"
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder={
            listening
              ? "Listening… keep talking"
              : controller
                ? "Type or use the mic…"
                : "Waiting for avatar…"
          }
          disabled={busy || !controller || listening}
          autoComplete="off"
        />
        <button
          type="button"
          className={
            listening ? "chat-panel__mic chat-panel__mic--active" : "chat-panel__mic"
          }
          onClick={onMicClick}
          disabled={busy || !controller || !micSupported}
          aria-pressed={listening}
          title={
            !micSupported
              ? "Speech recognition needs Chrome or Edge"
              : listening
                ? "Stop and send"
                : "Start listening"
          }
        >
          {listening ? "Stop" : "Mic"}
        </button>
        <button type="submit" disabled={busy || !controller || !draft.trim() || listening}>
          {busy ? "…" : "Send"}
        </button>
      </form>
    </section>
  );
}
