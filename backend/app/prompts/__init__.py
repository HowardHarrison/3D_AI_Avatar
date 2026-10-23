"""Prompt templates. Keep prompts out of services."""

from app.prompts.animation_plan import build_animation_plan_prompt
from app.prompts.chat_turn import build_chat_turn_prompt
from app.prompts.plan_script import build_plan_script_prompt

__all__ = [
    "build_animation_plan_prompt",
    "build_chat_turn_prompt",
    "build_plan_script_prompt",
]
