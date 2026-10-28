Expression **look** is no longer authored as Mixamo body shape-key stretch.

Production path: face-pack **masks** (see `docs/avatar-art-contract.md` and
`frontend/public/avatars/face/masks/`). Semantic ids: `neutral`, `serious`,
`positive`, `concerned`, `amused`, `curious`.

Legacy clip names (`Emotion_Neutral`, …) may still exist on the body GLB for
validators; the runtime must **not** use them to hold the face.
