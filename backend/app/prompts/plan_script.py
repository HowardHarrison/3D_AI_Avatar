"""Prompt templates for presenter script / plan text generation."""


def build_plan_script_prompt(topic: str) -> str:
    """
    Build the user prompt for a short spoken presenter script.

    Args:
        topic: News or segment topic (already trimmed by the caller).

    Returns:
        Prompt string for ``LLMProvider.generate``.
    """
    return (
        "You write short scripts for a 3D news-presenter avatar.\n"
        f"Topic: {topic}\n"
        "Write 2-4 spoken sentences the avatar can say aloud.\n"
        "Plain text only. No stage directions, labels, or markdown."
    )
