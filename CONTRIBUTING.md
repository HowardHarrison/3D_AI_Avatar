# Contributing — GitFlow-lite

This repo uses a **lightweight** branching model (not full classic GitFlow).  
Goal: keep `main` demoable, keep changes small, and leave a clear history.

## Trunk

| Branch | Role |
| --- | --- |
| `main` | Always releasable / demoable. Prefer merging via pull request. |

There is **no** long-lived `develop` or `release/*` branch for day-to-day work. Add those later only if you ship versioned web + mobile clients that need freeze windows.

## Branch names

Create a short-lived branch from an up-to-date `main`:

```text
feature/<area>-<short-name>
fix/<area>-<short-name>
chore/<short-name>
docs/<short-name>
```

`<area>` examples: `frontend`, `backend`, `blender`, `avatar`, `docs`.

Examples:

- `feature/backend-sample-plan-client`
- `feature/frontend-animation-plan-player`
- `fix/avatar-idle-blend`
- `chore/gitflow-lite-docs`

## Workflow

1. `git checkout main` and pull latest (when a remote exists).
2. `git checkout -b feature/<area>-<short-name>`
3. Implement **one** learning-sized step (see [AGENTS.md](AGENTS.md)).
4. Commit with a clear message (see below).
5. Open a pull request into `main`.
6. After merge, delete the branch.

Keep branches short-lived (hours/days). Do not park unfinished LLM/TTS work on `main`.

## Monorepo

One git tree for frontend, backend, and Blender scripts. Prefer one PR per step.  
If a step changes the shared `AnimationPlan` contract, prefer **schema/API first**, then the client — or one PR that updates both together.

## Commit messages

Prefer Conventional Commits:

```text
feat(backend): add sample AnimationPlan endpoint
fix(avatar): restore idle after gesture
docs: describe GitFlow-lite
chore: ignore Python venv artifacts
```

`type(scope): summary` — focus on **why**, keep the subject under ~72 characters.

## Pull requests

Use the PR template under `.github/`. Include:

- What changed (one step)
- How to verify (commands / clicks)
- Follow-up step (optional)

## What we are not doing yet

- Long-lived `develop`
- `release/*` / `hotfix/*` trains
- Forcing branch protection rules in this doc (configure on the host: GitHub/GitLab when you use a remote)

## Agents

Coding agents must follow this model: **do not commit straight to `main`** when a feature branch is appropriate. See [AGENTS.md](AGENTS.md).
