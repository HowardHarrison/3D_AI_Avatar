# Agent instructions — learn by building

This is a **learning project**. The human is developing it to understand the stack (Blender → GLB → React / R3F → avatar runtime → later AI). Speed and completeness are not the goal.

## Default: one small step

- Implement **one** learning-sized step, then **stop**.
- Explain what changed, why, which files to read, and what to run or click.
- Wait for the human to try it and ask for the next step.
- Prefer teaching the architecture (boundaries, names, why) over dumping a finished subsystem.

A “step” is something like: scaffold Vite, empty R3F scene, load a GLB, one controller class, debug buttons for that controller. It is **not** an entire MVP phase.

## Do not finish a whole phase unprompted

Do **not** implement a full phase, full plan, or every remaining todo in one go.

This still applies when:

- a plan file lists many steps
- todos say “complete all”
- the request is “implement the plan”
- the work is “only Phase 1” or “only the MVP”

Those mean **follow the plan’s order**, not **ship the whole phase now**.

Only implement multiple steps in one session if the human is explicit, for example: “do steps 1–3 now” or “I want the full remaining phase in this chat, not stepwise.”

If a request is ambiguous, default to **the next incomplete step only** and say what the following step will be.

## After each step

1. Keep the public API semantic (no clip indexes, no UI morph/bone math).
2. Do not add LLM, TTS, FastAPI, or other later-phase features.
3. Do not expand scope “while we are here.”
