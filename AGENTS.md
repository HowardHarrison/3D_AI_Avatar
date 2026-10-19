# Agent instructions — learn by building

This is a **learning project**. The human is developing it to understand the stack (Blender → GLB → React / R3F → avatar runtime → later AI). Speed and completeness are not the goal.

The npm app lives in `frontend/` (one Vite project). There is no `packages/` workspace.

## Durable context (Obsidian)

Chat context is limited. Persist only **necessary** resume facts outside the repo:

`C:\Users\USER\Documents\Obsidian Vault\Projects' Contexts\AI_3D_Avatar\`

| File | Use |
| --- | --- |
| `AI_3D_Avatar.md` | Stable map: what / where / how to run |
| `Context Log.md` | Dated milestones and decisions (append-only) |

**When to read:** at session start if the task depends on prior progress or “where we left off.”

**When to write:** after a meaningful milestone (API decision, phase boundary, non-obvious gotcha, agreed next step). One short dated entry. No chat transcripts, no secrets, no dumping `docs/` into Obsidian — link or name the repo file instead.

**Do not** treat Obsidian as the source of truth for architecture; repo `docs/` and code win on conflict. Update the vault date on `AI_3D_Avatar.md` when the stable map changes.

## Navigate by graphify nodes (save tokens)

Before broad `Read` / `Grep` / `Glob` exploration, orient with the code graph at `graphify-out/`. Prefer **nodes and edges** over loading whole files or folders into chat.

| Command | Use when |
| --- | --- |
| `graphify query "<question>"` | Debugging or “where does X live?” — get a scoped subgraph |
| `graphify path "<A>" "<B>"` | Tracing a call/dependency chain between two symbols |
| `graphify explain "<concept>"` | Adding a feature near a concept (e.g. gesture, expression, GLB export) |

**Workflow**

1. Query/path/explain → note the **node names** and file paths they point to.
2. Open only those files (and only the needed lines) to change or verify.
3. After code edits: `graphify update .` (AST-only, no API key) so the next session stays accurate.

If `graphify-out/graph.json` is missing, run `graphify . --code-only` once, then `graphify cluster-only .`. Do not dump `GRAPH_REPORT.md` or large subgraphs into Obsidian — store a short dated pointer in `Context Log.md` only when a hub or boundary mattered for a decision.

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
4. If the step was a durable milestone, append a dated line to Obsidian `Context Log.md` (see above).
