# Animation system

Semantic names live in `apps/web/src/avatar/animation/AnimationRegistry.ts` and `@avatar/shared`.

## Layers (priorities)

| Layer | Priority |
| --- | --- |
| Idle | 0 |
| Head motion | 10 |
| Gesture | 20 |
| Expression | 30 |
| Speech / visemes (future) | 40 |
| Override | 100 |

Phase 1 approximates layers: looping idle, exclusive gesture crossfades, non-exclusive head clips, morph-target expressions, and an independent blink timer.

## State machine

`IDLE` → `GESTURE` → `IDLE`

`IDLE` → `SPEAKING` → (`GESTURE`) → `SPEAKING` → `IDLE`

## Plans

`parseAnimationPlan` validates `{ start, end, emotion, gesture, headMotion, gaze }`. Phase 1 does not play plans automatically; the parser is the stable contract for later LLM output.
