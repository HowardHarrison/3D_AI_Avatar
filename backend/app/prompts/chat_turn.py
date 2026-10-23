"""Prompt templates for interactive chatbot turns."""

from __future__ import annotations

from typing import Literal, Sequence

ChatRole = Literal["user", "assistant"]


def build_chat_turn_prompt(
    message: str,
    history: Sequence[tuple[ChatRole, str]] | None = None,
) -> str:
    """
    Build the prompt for one stylized chatbot reply, with optional prior turns.

    Args:
        message: Latest user utterance (already trimmed by the caller).
        history: Prior ``(role, text)`` pairs in chronological order (not including
            the current ``message``).

    Returns:
        Prompt string for ``LLMProvider.generate``.
    """
    lines = [
        "You are a friendly stylized 3D chatbot avatar (cartoon / Bitmoji-like).",
        "Reply in 1-3 short spoken sentences the avatar can say aloud.",
        "Be warm, clear, and conversational. Plain text only.",
        "No stage directions, markdown, bullet lists, or labels.",
        "Use earlier turns in this conversation when relevant.",
        "",
    ]
    if history:
        lines.append("Conversation so far:")
        for role, text in history:
            label = "User" if role == "user" else "Assistant"
            lines.append(f"{label}: {text}")
        lines.append("")
    lines.append(f"User: {message}")
    lines.append("Assistant:")
    return "\n".join(lines)
