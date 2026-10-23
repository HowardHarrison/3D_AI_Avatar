"""Prompt templates for interactive chatbot turns."""


def build_chat_turn_prompt(message: str) -> str:
    """
    Build the prompt for one stylized chatbot reply.

    Args:
        message: User utterance (already trimmed by the caller).

    Returns:
        Prompt string for ``LLMProvider.generate``.
    """
    return (
        "You are a friendly stylized 3D chatbot avatar (cartoon / Bitmoji-like).\n"
        "Reply in 1-3 short spoken sentences the avatar can say aloud.\n"
        "Be warm, clear, and conversational. Plain text only.\n"
        "No stage directions, markdown, bullet lists, or labels.\n"
        f"User: {message}\n"
        "Assistant:"
    )
