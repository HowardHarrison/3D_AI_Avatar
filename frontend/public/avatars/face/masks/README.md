# Face-pack expression masks

Production expressions are **masks** crossfaded onto the face area (not Mixamo body morph stretch).

Required files (same face UV / card size for every expression):

| Semantic id | File |
| --- | --- |
| `neutral` | `neutral.webp` (PNG fallback OK) |
| `serious` | `serious.webp` |
| `positive` | `positive.webp` |
| `concerned` | `concerned.webp` |
| `amused` | `amused.webp` |
| `curious` | `curious.webp` |

Generate placeholders:

```bash
python blender/scripts/generate_face_pack_masks.py
```

Runtime: `FacePackRegistry.ts` + `FaceMaskLayer` (200 ms crossfade on FaceCard).  
Replace these drawings with authored art that matches the body; keep filenames.
