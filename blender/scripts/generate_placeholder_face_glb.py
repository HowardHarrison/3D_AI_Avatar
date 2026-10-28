"""Generate a stylized face-only placeholder GLB for the Head bone socket.

Drawn eyes / nose / mouth (not clay stretching). Morph names match contracts.

    python blender/scripts/generate_placeholder_face_glb.py

Writes ``blender/exports/face.glb`` and ``frontend/public/avatars/face.glb``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from contracts import OPTIONAL_SHAPE_KEYS, REQUIRED_SHAPE_KEYS  # noqa: E402
from generate_placeholder_glb import GltfBuilder  # noqa: E402


def build_face() -> bytes:
    """Build a Bitmoji-like face with contract morph names on head + mouth meshes."""
    builder = GltfBuilder()
    # Pale matte skin closer to Mixamo body; FaceCard masks draw the features.
    skin = builder.add_material("FaceSkin", (0.91, 0.89, 0.86))
    hair = builder.add_material("FaceHair", (0.22, 0.16, 0.14))
    eye_white = builder.add_material("EyeWhite", (0.98, 0.98, 1.0))
    pupil = builder.add_material("Pupil", (0.05, 0.05, 0.08))
    nose_mat = builder.add_material("Nose", (0.88, 0.84, 0.8))
    mouth_mat = builder.add_material("Mouth", (0.55, 0.12, 0.18))

    morph_names = list(REQUIRED_SHAPE_KEYS) + list(OPTIONAL_SHAPE_KEYS)
    morph_offsets = {name: (0.0, 0.0, 0.0) for name in morph_names}

    head_mesh = builder.add_box_mesh("FaceHeadMesh", (0.42, 0.46, 0.36), skin, morph_offsets)
    hair_mesh = builder.add_box_mesh("FaceHairMesh", (0.44, 0.14, 0.38), hair)
    sclera_mesh = builder.add_box_mesh("EyeWhiteMesh", (0.11, 0.1, 0.05), eye_white)
    pupil_mesh = builder.add_box_mesh("PupilMesh", (0.05, 0.05, 0.04), pupil)
    nose_mesh = builder.add_box_mesh("NoseMesh", (0.06, 0.055, 0.08), nose_mat)
    mouth_mesh = builder.add_box_mesh("MouthMesh", (0.16, 0.045, 0.045), mouth_mat, morph_offsets)

    left_pupil = builder.add_node("LeftPupil", translation=(0.0, 0.0, 0.03), mesh=pupil_mesh)
    left_sclera = builder.add_node(
        "LeftSclera", translation=(0.0, 0.0, 0.0), mesh=sclera_mesh, children=[left_pupil]
    )
    left_eye = builder.add_node(
        "LeftEye", translation=(-0.1, 0.06, 0.19), children=[left_sclera]
    )
    right_pupil = builder.add_node("RightPupil", translation=(0.0, 0.0, 0.03), mesh=pupil_mesh)
    right_sclera = builder.add_node(
        "RightSclera", translation=(0.0, 0.0, 0.0), mesh=sclera_mesh, children=[right_pupil]
    )
    right_eye = builder.add_node(
        "RightEye", translation=(0.1, 0.06, 0.19), children=[right_sclera]
    )
    nose = builder.add_node("Nose", translation=(0.0, -0.02, 0.2), mesh=nose_mesh)
    mouth = builder.add_node("Mouth", translation=(0.0, -0.12, 0.19), mesh=mouth_mesh)
    hair_node = builder.add_node("Hair", translation=(0.0, 0.22, 0.0), mesh=hair_mesh)
    face_head = builder.add_node(
        "FaceHead",
        translation=(0.0, 0.0, 0.0),
        mesh=head_mesh,
        children=[hair_node, left_eye, right_eye, nose, mouth],
    )
    # Runtime parents this root to the body ``Head`` bone.
    builder.add_node("AvatarFace", translation=(0.0, 0.0, 0.0), children=[face_head])
    return builder.to_glb(root_node="AvatarFace")


def main() -> int:
    """Write face.glb next to the body presenter asset."""
    root = Path(__file__).resolve().parents[2]
    data = build_face()
    for path in (
        root / "blender" / "exports" / "face.glb",
        root / "frontend" / "public" / "avatars" / "face.glb",
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(f"PASS: Wrote {path} ({len(data)} bytes)")
    print("RESULT: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
