"""Generate a contract-compliant stylized placeholder presenter.glb without Blender.

Big-head cartoon proportions and flat colors (chatbot / Bitmoji-like stand-in).
Bone, clip, and morph names match ``contracts.py``. Replace with an authored
stylized character when ready — keep the same names.

    python blender/scripts/generate_placeholder_glb.py
"""

from __future__ import annotations

import json
import math
import struct
from pathlib import Path

from contracts import OPTIONAL_ANIMATIONS, REQUIRED_ANIMATIONS, REQUIRED_SHAPE_KEYS


GLB_MAGIC = 0x46546C67
GLB_VERSION = 2
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942
COMPONENT_FLOAT = 5126
COMPONENT_USHORT = 5123


def _align4(length: int) -> int:
    """Return the next 4-byte aligned length."""
    return (length + 3) & ~3


def _box_positions(sx: float, sy: float, sz: float) -> list[float]:
    """Return 24 unique-enough cube vertices as xyz floats (8 corners expanded per face)."""
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    corners = [
        (-hx, -hy, hz),
        (hx, -hy, hz),
        (hx, hy, hz),
        (-hx, hy, hz),
        (-hx, -hy, -hz),
        (hx, -hy, -hz),
        (hx, hy, -hz),
        (-hx, hy, -hz),
    ]
    faces = (
        (0, 1, 2, 3),
        (1, 5, 6, 2),
        (5, 4, 7, 6),
        (4, 0, 3, 7),
        (3, 2, 6, 7),
        (4, 5, 1, 0),
    )
    positions: list[float] = []
    for face in faces:
        for index in face:
            positions.extend(corners[index])
    return positions


def _box_normals() -> list[float]:
    """Return per-vertex normals for the six cube faces produced by _box_positions."""
    axes = (
        (0.0, 0.0, 1.0),
        (1.0, 0.0, 0.0),
        (0.0, 0.0, -1.0),
        (-1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, -1.0, 0.0),
    )
    normals: list[float] = []
    for axis in axes:
        for _ in range(4):
            normals.extend(axis)
    return normals


def _box_indices() -> list[int]:
    """Return triangle indices for six quads (24 vertices)."""
    indices: list[int] = []
    for face in range(6):
        base = face * 4
        indices.extend((base, base + 1, base + 2, base, base + 2, base + 3))
    return indices


def _quat_from_euler(rx: float, ry: float, rz: float) -> tuple[float, float, float, float]:
    """Convert XYZ Euler radians to a glTF quaternion (x, y, z, w)."""
    cx, sx = math.cos(rx / 2.0), math.sin(rx / 2.0)
    cy, sy = math.cos(ry / 2.0), math.sin(ry / 2.0)
    cz, sz = math.cos(rz / 2.0), math.sin(rz / 2.0)
    w = cx * cy * cz + sx * sy * sz
    x = sx * cy * cz - cx * sy * sz
    y = cx * sy * cz + sx * cy * sz
    z = cx * cy * sz - sx * sy * cz
    return (x, y, z, w)


def _facial_morph_deltas(positions: list[float], morph_name: str) -> list[float]:
    """Build per-vertex position deltas so box-head morphs read as a cartoon face.

    Uniform whole-head offsets are nearly invisible. Region masks (mouth / brow /
    eyes) make expressions distinct on the stylized placeholder.
    """
    deltas: list[float] = []
    for i in range(len(positions) // 3):
        x = positions[i * 3]
        y = positions[i * 3 + 1]
        z = positions[i * 3 + 2]
        # Soft masks in local head space (origin at head center).
        front = max(0.0, z * 2.2)
        lower = max(0.0, -y * 2.0)
        upper = max(0.0, y * 2.0)
        left = max(0.0, -x * 2.2)
        right = max(0.0, x * 2.2)
        mouth = lower * (0.35 + front)
        brow = upper * (0.35 + front)
        eye_l = front * upper * left
        eye_r = front * upper * right
        dx = dy = dz = 0.0

        if morph_name == "mouth_open":
            dy, dz = -0.11 * mouth, 0.05 * mouth
        elif morph_name == "mouth_close":
            dy, dz = 0.05 * mouth, -0.03 * mouth
        elif morph_name == "mouth_wide":
            side = right - left
            dx, dz = 0.09 * side * (0.4 + front), 0.03 * mouth
        elif morph_name == "mouth_round":
            dy, dz = -0.04 * mouth, 0.08 * mouth
            dx = 0.03 * (right - left) * front
        elif morph_name == "mouth_smile":
            corner = mouth * (0.5 + right + left)
            dx = 0.1 * (1.0 if x >= 0.0 else -1.0) * corner
            dy = 0.07 * mouth
            dz = 0.02 * mouth
        elif morph_name == "mouth_frown":
            corner = mouth * (0.5 + right + left)
            dx = 0.06 * (1.0 if x >= 0.0 else -1.0) * corner
            dy = -0.08 * mouth
        elif morph_name == "jaw_open":
            dy, dz = -0.14 * mouth, 0.04 * mouth
        elif morph_name == "brow_up":
            dy, dz = 0.09 * brow, 0.02 * brow
        elif morph_name == "brow_down":
            dy = -0.08 * brow
        elif morph_name == "eye_blink_left":
            dy = -0.1 * eye_l
        elif morph_name == "eye_blink_right":
            dy = -0.1 * eye_r
        elif morph_name == "eye_wide":
            dy = 0.07 * (eye_l + eye_r)
            dz = 0.03 * front * upper
        elif morph_name == "eye_squint":
            dy = -0.06 * (eye_l + eye_r)
        else:
            dy = 0.01 * front

        deltas.extend((dx, dy, dz))
    return deltas


class GltfBuilder:
    """Accumulate binary payloads and glTF JSON for a single GLB file."""

    def __init__(self) -> None:
        self._blob = bytearray()
        self.accessors: list[dict] = []
        self.buffer_views: list[dict] = []
        self.nodes: list[dict] = []
        self.meshes: list[dict] = []
        self.materials: list[dict] = []
        self.skins: list[dict] = []
        self.animations: list[dict] = []
        self.node_index: dict[str, int] = {}

    def add_node(
        self,
        name: str,
        translation: tuple[float, float, float] | None = None,
        rotation: tuple[float, float, float, float] | None = None,
        children: list[int] | None = None,
        mesh: int | None = None,
        skin: int | None = None,
    ) -> int:
        """Append a scene node and remember it by name."""
        node: dict = {"name": name}
        if translation is not None:
            node["translation"] = list(translation)
        if rotation is not None:
            node["rotation"] = list(rotation)
        if children:
            node["children"] = children
        if mesh is not None:
            node["mesh"] = mesh
        if skin is not None:
            node["skin"] = skin
        index = len(self.nodes)
        self.nodes.append(node)
        self.node_index[name] = index
        return index

    def _push_bytes(self, data: bytes, target: int) -> int:
        """Append a bufferView and return its index."""
        padding = _align4(len(self._blob)) - len(self._blob)
        self._blob.extend(b"\x00" * padding)
        offset = len(self._blob)
        self._blob.extend(data)
        view = {"buffer": 0, "byteOffset": offset, "byteLength": len(data), "target": target}
        self.buffer_views.append(view)
        return len(self.buffer_views) - 1

    def add_float_accessor(
        self,
        values: list[float],
        type_name: str,
        target: int = 34962,
        extras: dict | None = None,
    ) -> int:
        """Store float data and return the accessor index."""
        packed = struct.pack("<" + "f" * len(values), *values)
        view = self._push_bytes(packed, target)
        comps = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[type_name]
        count = len(values) // comps
        accessor: dict = {
            "bufferView": view,
            "componentType": COMPONENT_FLOAT,
            "count": count,
            "type": type_name,
        }
        if type_name == "VEC3" and count:
            xs = values[0::3]
            ys = values[1::3]
            zs = values[2::3]
            accessor["min"] = [min(xs), min(ys), min(zs)]
            accessor["max"] = [max(xs), max(ys), max(zs)]
        if extras:
            accessor["extras"] = extras
        self.accessors.append(accessor)
        return len(self.accessors) - 1

    def add_ushort_accessor(self, values: list[int]) -> int:
        """Store unsigned short index data and return the accessor index."""
        packed = struct.pack("<" + "H" * len(values), *values)
        view = self._push_bytes(packed, 34963)
        accessor = {
            "bufferView": view,
            "componentType": COMPONENT_USHORT,
            "count": len(values),
            "type": "SCALAR",
        }
        self.accessors.append(accessor)
        return len(self.accessors) - 1

    def add_material(self, name: str, color: tuple[float, float, float]) -> int:
        """Add an unlit-looking PBR material with a solid base color."""
        self.materials.append(
            {
                "name": name,
                "pbrMetallicRoughness": {
                    "baseColorFactor": [color[0], color[1], color[2], 1.0],
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.92,
                },
            }
        )
        return len(self.materials) - 1

    def add_box_mesh(
        self,
        name: str,
        size: tuple[float, float, float],
        material: int,
        morphs: dict[str, tuple[float, float, float]] | None = None,
    ) -> int:
        """Create a box primitive, optionally with named morph targets on all vertices."""
        positions = _box_positions(*size)
        normals = _box_normals()
        indices = _box_indices()
        pos_acc = self.add_float_accessor(positions, "VEC3")
        nrm_acc = self.add_float_accessor(normals, "VEC3")
        idx_acc = self.add_ushort_accessor(indices)
        primitive: dict = {
            "attributes": {"POSITION": pos_acc, "NORMAL": nrm_acc},
            "indices": idx_acc,
            "material": material,
        }
        mesh: dict = {"name": name, "primitives": [primitive]}
        if morphs:
            targets = []
            names = []
            for morph_name in morphs:
                names.append(morph_name)
                deltas = _facial_morph_deltas(positions, morph_name)
                targets.append({"POSITION": self.add_float_accessor(deltas, "VEC3")})
            primitive["targets"] = targets
            mesh["weights"] = [0.0] * len(names)
            mesh["extras"] = {"targetNames": names}
        self.meshes.append(mesh)
        return len(self.meshes) - 1

    def add_rotation_animation(
        self,
        name: str,
        node_name: str,
        keyframes: list[tuple[float, tuple[float, float, float]]],
    ) -> None:
        """Add a rotation clip for one node. Keyframes are (time, xyz euler radians)."""
        times = [k[0] for k in keyframes]
        quats: list[float] = []
        for _, euler in keyframes:
            q = _quat_from_euler(*euler)
            quats.extend(q)
        time_acc = self.add_float_accessor(times, "SCALAR", target=0)
        rot_acc = self.add_float_accessor(quats, "VEC4", target=0)
        self.accessors[time_acc]["min"] = [min(times)]
        self.accessors[time_acc]["max"] = [max(times)]
        node = self.node_index[node_name]
        self.animations.append(
            {
                "name": name,
                "samplers": [{"input": time_acc, "output": rot_acc, "interpolation": "LINEAR"}],
                "channels": [{"sampler": 0, "target": {"node": node, "path": "rotation"}}],
            }
        )

    def add_multi_rotation_animation(
        self,
        name: str,
        channels: dict[str, list[tuple[float, tuple[float, float, float]]]],
    ) -> None:
        """Add a clip that rotates several nodes with shared timing."""
        samplers = []
        gltf_channels = []
        for node_name, keyframes in channels.items():
            times = [k[0] for k in keyframes]
            quats: list[float] = []
            for _, euler in keyframes:
                q = _quat_from_euler(*euler)
                quats.extend(q)
            time_acc = self.add_float_accessor(times, "SCALAR", target=0)
            rot_acc = self.add_float_accessor(quats, "VEC4", target=0)
            self.accessors[time_acc]["min"] = [min(times)]
            self.accessors[time_acc]["max"] = [max(times)]
            sampler_index = len(samplers)
            samplers.append({"input": time_acc, "output": rot_acc, "interpolation": "LINEAR"})
            gltf_channels.append(
                {
                    "sampler": sampler_index,
                    "target": {"node": self.node_index[node_name], "path": "rotation"},
                }
            )
        self.animations.append({"name": name, "samplers": samplers, "channels": gltf_channels})

    def add_morph_animation(
        self,
        name: str,
        node_name: str,
        target_count: int,
        frames: list[tuple[float, list[float]]],
    ) -> None:
        """Animate morph weights on a mesh node."""
        times = [f[0] for f in frames]
        weights: list[float] = []
        for _, values in frames:
            if len(values) != target_count:
                raise ValueError("Morph frame length must match target_count")
            weights.extend(values)
        time_acc = self.add_float_accessor(times, "SCALAR", target=0)
        weight_acc = self.add_float_accessor(weights, "SCALAR", target=0)
        self.accessors[time_acc]["min"] = [min(times)]
        self.accessors[time_acc]["max"] = [max(times)]
        sampler = {"input": time_acc, "output": weight_acc, "interpolation": "LINEAR"}
        channel = {
            "sampler": 0,
            "target": {"node": self.node_index[node_name], "path": "weights"},
        }
        self.animations.append({"name": name, "samplers": [sampler], "channels": [channel]})

    def to_glb(self, root_node: str = "Armature") -> bytes:
        """Serialize the current document as a GLB blob.

        Args:
            root_node: Scene root node name (body uses ``Armature``; face uses ``AvatarFace``).
        """
        json_doc = {
            "asset": {"version": "2.0", "generator": "AI_3D_Avatar placeholder generator"},
            "scene": 0,
            "scenes": [{"nodes": [self.node_index[root_node]]}],
            "nodes": self.nodes,
            "meshes": self.meshes,
            "materials": self.materials,
            "skins": self.skins,
            "animations": self.animations,
            "accessors": self.accessors,
            "bufferViews": self.buffer_views,
            "buffers": [{"byteLength": len(self._blob)}],
        }
        json_bytes = json.dumps(json_doc, separators=(",", ":")).encode("utf-8")
        json_padding = _align4(len(json_bytes)) - len(json_bytes)
        json_bytes += b" " * json_padding
        bin_padding = _align4(len(self._blob)) - len(self._blob)
        bin_data = bytes(self._blob) + (b"\x00" * bin_padding)

        total = 12 + 8 + len(json_bytes) + 8 + len(bin_data)
        header = struct.pack("<III", GLB_MAGIC, GLB_VERSION, total)
        json_chunk = struct.pack("<II", len(json_bytes), JSON_CHUNK) + json_bytes
        bin_chunk = struct.pack("<II", len(bin_data), BIN_CHUNK) + bin_data
        return header + json_chunk + bin_chunk


def _identity_mat4() -> list[float]:
    """Return a column-major 4x4 identity matrix."""
    return [
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
    ]


def build_presenter() -> bytes:
    """Build a stylized (Bitmoji-like) contract-compliant placeholder GLB.

    Same bone / clip / morph names as ``contracts.py``. Larger head, brighter
    flat colors, chunkier limbs — intentional cartoon, not photoreal.
    """
    builder = GltfBuilder()
    # Flat cartoon palette (teal top, warm skin) — readable at low poly.
    top = builder.add_material("Top", (0.18, 0.62, 0.68))
    shirt = builder.add_material("Shirt", (0.96, 0.94, 0.90))
    skin = builder.add_material("Skin", (1.0, 0.84, 0.72))
    hair = builder.add_material("Hair", (0.42, 0.26, 0.16))
    eye_white = builder.add_material("EyeWhite", (0.98, 0.98, 1.0))
    pupil = builder.add_material("Pupil", (0.04, 0.04, 0.06))
    nose_mat = builder.add_material("Nose", (0.94, 0.72, 0.6))
    mouth_mat = builder.add_material("Mouth", (0.28, 0.08, 0.1))
    shoe = builder.add_material("Shoe", (0.25, 0.28, 0.32))

    # Keys only — vertex deltas come from ``_facial_morph_deltas`` (region masks).
    morph_offsets = {name: (0.0, 0.0, 0.0) for name in REQUIRED_SHAPE_KEYS}
    assert tuple(morph_offsets.keys()) == REQUIRED_SHAPE_KEYS

    # Big-head / short-limb proportions — one art direction for body + head (masks on Head).
    hips_mesh = builder.add_box_mesh("HipsMesh", (0.32, 0.14, 0.2), top)
    spine_mesh = builder.add_box_mesh("SpineMesh", (0.28, 0.15, 0.17), shirt)
    chest_mesh = builder.add_box_mesh("ChestMesh", (0.38, 0.24, 0.2), top)
    neck_mesh = builder.add_box_mesh("NeckMesh", (0.09, 0.07, 0.09), skin)
    head_mesh = builder.add_box_mesh("HeadMesh", (0.36, 0.4, 0.34), skin, morph_offsets)
    hair_mesh = builder.add_box_mesh("HairMesh", (0.38, 0.13, 0.36), hair)
    # Clear B&W cartoon eyes + simple nose / mouth (feature meshes, not morph-only).
    sclera_mesh = builder.add_box_mesh("EyeWhiteMesh", (0.1, 0.09, 0.045), eye_white)
    pupil_mesh = builder.add_box_mesh("PupilMesh", (0.048, 0.048, 0.04), pupil)
    nose_mesh = builder.add_box_mesh("NoseMesh", (0.055, 0.048, 0.07), nose_mat)
    mouth_mesh = builder.add_box_mesh("MouthMesh", (0.13, 0.032, 0.035), mouth_mat)
    upper_arm_mesh = builder.add_box_mesh("UpperArmMesh", (0.1, 0.26, 0.1), top)
    lower_arm_mesh = builder.add_box_mesh("LowerArmMesh", (0.09, 0.24, 0.09), shirt)
    hand_mesh = builder.add_box_mesh("HandMesh", (0.1, 0.12, 0.06), skin)
    shoulder_mesh = builder.add_box_mesh("ShoulderMesh", (0.14, 0.12, 0.12), top)
    thigh_mesh = builder.add_box_mesh("ThighMesh", (0.14, 0.32, 0.14), top)
    shin_mesh = builder.add_box_mesh("ShinMesh", (0.12, 0.32, 0.12), top)
    foot_mesh = builder.add_box_mesh("FootMesh", (0.12, 0.06, 0.22), shoe)

    def limb(name: str, mesh: int, translation: tuple[float, float, float]) -> int:
        return builder.add_node(name, translation=translation, mesh=mesh)

    left_foot = limb("LeftFoot", foot_mesh, (0.0, -0.18, 0.04))
    left_lower_leg = builder.add_node(
        "LeftLowerLeg", translation=(0.0, -0.36, 0.0), mesh=shin_mesh, children=[left_foot]
    )
    left_upper_leg = builder.add_node(
        "LeftUpperLeg", translation=(-0.1, -0.08, 0.0), mesh=thigh_mesh, children=[left_lower_leg]
    )
    right_foot = limb("RightFoot", foot_mesh, (0.0, -0.18, 0.04))
    right_lower_leg = builder.add_node(
        "RightLowerLeg", translation=(0.0, -0.36, 0.0), mesh=shin_mesh, children=[right_foot]
    )
    right_upper_leg = builder.add_node(
        "RightUpperLeg", translation=(0.1, -0.08, 0.0), mesh=thigh_mesh, children=[right_lower_leg]
    )

    left_hand = limb("LeftHand", hand_mesh, (0.0, -0.18, 0.0))
    left_lower_arm = builder.add_node(
        "LeftLowerArm", translation=(0.0, -0.28, 0.0), mesh=lower_arm_mesh, children=[left_hand]
    )
    left_upper_arm = builder.add_node(
        "LeftUpperArm", translation=(0.0, -0.16, 0.0), mesh=upper_arm_mesh, children=[left_lower_arm]
    )
    left_shoulder = builder.add_node(
        "LeftShoulder", translation=(-0.26, 0.08, 0.0), mesh=shoulder_mesh, children=[left_upper_arm]
    )

    right_hand = limb("RightHand", hand_mesh, (0.0, -0.18, 0.0))
    right_lower_arm = builder.add_node(
        "RightLowerArm", translation=(0.0, -0.28, 0.0), mesh=lower_arm_mesh, children=[right_hand]
    )
    right_upper_arm = builder.add_node(
        "RightUpperArm", translation=(0.0, -0.16, 0.0), mesh=upper_arm_mesh, children=[right_lower_arm]
    )
    right_shoulder = builder.add_node(
        "RightShoulder", translation=(0.26, 0.08, 0.0), mesh=shoulder_mesh, children=[right_upper_arm]
    )

    # Eye bones stay named LeftEye / RightEye (idle look uses them). Sclera + pupil are children.
    left_pupil = builder.add_node("LeftPupil", translation=(0.0, 0.0, 0.028), mesh=pupil_mesh)
    left_sclera = builder.add_node(
        "LeftSclera", translation=(0.0, 0.0, 0.0), mesh=sclera_mesh, children=[left_pupil]
    )
    left_eye = builder.add_node(
        "LeftEye", translation=(-0.085, 0.055, 0.178), children=[left_sclera]
    )
    right_pupil = builder.add_node("RightPupil", translation=(0.0, 0.0, 0.028), mesh=pupil_mesh)
    right_sclera = builder.add_node(
        "RightSclera", translation=(0.0, 0.0, 0.0), mesh=sclera_mesh, children=[right_pupil]
    )
    right_eye = builder.add_node(
        "RightEye", translation=(0.085, 0.055, 0.178), children=[right_sclera]
    )
    nose_node = builder.add_node("Nose", translation=(0.0, -0.015, 0.188), mesh=nose_mesh)
    mouth_node = builder.add_node("Mouth", translation=(0.0, -0.105, 0.178), mesh=mouth_mesh)
    hair_node = builder.add_node("Hair", translation=(0.0, 0.2, 0.0), mesh=hair_mesh)
    head = builder.add_node(
        "Head",
        translation=(0.0, 0.14, 0.0),
        mesh=head_mesh,
        children=[left_eye, right_eye, nose_node, mouth_node, hair_node],
    )
    neck = builder.add_node("Neck", translation=(0.0, 0.16, 0.0), mesh=neck_mesh, children=[head])
    chest = builder.add_node(
        "Chest",
        translation=(0.0, 0.2, 0.0),
        mesh=chest_mesh,
        children=[neck, left_shoulder, right_shoulder],
    )
    spine = builder.add_node("Spine", translation=(0.0, 0.12, 0.0), mesh=spine_mesh, children=[chest])
    hips = builder.add_node(
        "Hips",
        translation=(0.0, 0.95, 0.0),
        mesh=hips_mesh,
        children=[spine, left_upper_leg, right_upper_leg],
    )

    joint_names = [
        "Hips",
        "Spine",
        "Chest",
        "Neck",
        "Head",
        "LeftShoulder",
        "LeftUpperArm",
        "LeftLowerArm",
        "LeftHand",
        "RightShoulder",
        "RightUpperArm",
        "RightLowerArm",
        "RightHand",
        "LeftUpperLeg",
        "LeftLowerLeg",
        "LeftFoot",
        "RightUpperLeg",
        "RightLowerLeg",
        "RightFoot",
        "LeftEye",
        "RightEye",
    ]
    joint_indices = [builder.node_index[name] for name in joint_names]
    ibm = []
    for _ in joint_names:
        ibm.extend(_identity_mat4())
    ibm_acc = builder.add_float_accessor(ibm, "MAT4", target=0)
    builder.skins.append(
        {
            "name": "PresenterSkin",
            "skeleton": builder.node_index["Hips"],
            "joints": joint_indices,
            "inverseBindMatrices": ibm_acc,
        }
    )
    # Meshes are parented to bones (rigid bind). A skin definition is included so
    # the GLB carries an armature/joints list for runtime inspection.
    builder.add_node("Armature", children=[hips])

    identity = (0.0, 0.0, 0.0)
    rest_arm = (0.15, 0.0, 0.0)
    # Same magnitude for L/R mirrors so Turn/Tilt Right match Left (sign flip only).
    turn_yaw = 0.7
    tilt_roll = 0.55

    def loop(name: str, node: str, motion: tuple[float, float, float], duration: float = 2.0) -> None:
        builder.add_rotation_animation(
            name,
            node,
            [
                (0.0, identity),
                (duration / 2.0, motion),
                (duration, identity),
            ],
        )

    def hold_pose(
        name: str,
        node: str,
        motion: tuple[float, float, float],
        arrive: float = 0.35,
        hold_until: float = 1.15,
    ) -> None:
        """Move to pose and hold (clampWhenFinished keeps the readable end pose)."""
        builder.add_rotation_animation(
            name,
            node,
            [
                (0.0, identity),
                (arrive, motion),
                (hold_until, motion),
            ],
        )

    loop("Idle_Neutral", "Spine", (0.02, 0.0, 0.0), 4.0)
    builder.add_multi_rotation_animation(
        "Idle_Breathing",
        {
            "Chest": [(0.0, identity), (1.5, (0.04, 0.0, 0.0)), (3.0, identity)],
            "Spine": [(0.0, identity), (1.5, (0.015, 0.0, 0.0)), (3.0, identity)],
        },
    )
    builder.add_multi_rotation_animation(
        "Idle_ShiftWeight",
        {
            "Hips": [(0.0, identity), (1.2, (0.0, 0.0, 0.06)), (2.4, identity)],
        },
    )
    # Clear double-nod (not a tiny single bob).
    builder.add_rotation_animation(
        "Head_Nod_Small",
        "Head",
        [
            (0.0, identity),
            (0.22, (0.55, 0.0, 0.0)),
            (0.4, (0.08, 0.0, 0.0)),
            (0.62, (0.55, 0.0, 0.0)),
            (0.95, identity),
        ],
    )
    hold_pose("Head_Turn_Left", "Head", (0.0, turn_yaw, 0.0))
    hold_pose("Head_Turn_Right", "Head", (0.0, -turn_yaw, 0.0))
    hold_pose("Head_Tilt_Left", "Head", (0.0, 0.0, tilt_roll))
    hold_pose("Head_Tilt_Right", "Head", (0.0, 0.0, -tilt_roll))
    builder.add_rotation_animation(
        "Gesture_Nod",
        "Head",
        [
            (0.0, identity),
            (0.2, (0.5, 0.0, 0.0)),
            (0.38, (0.05, 0.0, 0.0)),
            (0.58, (0.5, 0.0, 0.0)),
            (0.85, identity),
        ],
    )

    builder.add_multi_rotation_animation(
        "Gesture_OpenHand",
        {
            "LeftUpperArm": [(0.0, rest_arm), (0.4, (0.55, 0.15, 0.75)), (1.2, rest_arm)],
            "LeftLowerArm": [(0.0, identity), (0.4, (0.35, 0.0, 0.15)), (1.2, identity)],
            "RightUpperArm": [(0.0, rest_arm), (0.4, (0.55, -0.15, -0.75)), (1.2, rest_arm)],
            "RightLowerArm": [(0.0, identity), (0.4, (0.35, 0.0, -0.15)), (1.2, identity)],
        },
    )
    builder.add_multi_rotation_animation(
        "Gesture_Emphasize",
        {
            "RightUpperArm": [(0.0, rest_arm), (0.35, (0.95, -0.35, -0.55)), (0.9, rest_arm)],
            "RightLowerArm": [(0.0, identity), (0.35, (0.75, 0.0, 0.0)), (0.9, identity)],
        },
    )
    builder.add_multi_rotation_animation(
        "Gesture_PointLeft",
        {
            "LeftUpperArm": [(0.0, rest_arm), (0.4, (0.75, 0.55, 1.0)), (1.1, rest_arm)],
            "LeftLowerArm": [(0.0, identity), (0.4, (0.25, 0.0, 0.2)), (1.1, identity)],
        },
    )
    builder.add_multi_rotation_animation(
        "Gesture_PointRight",
        {
            "RightUpperArm": [(0.0, rest_arm), (0.4, (0.75, -0.55, -1.0)), (1.1, rest_arm)],
            "RightLowerArm": [(0.0, identity), (0.4, (0.25, 0.0, -0.2)), (1.1, identity)],
        },
    )
    # Hands meet in front of the chest (hold mid pose so it reads clearly).
    builder.add_multi_rotation_animation(
        "Gesture_HandsTogether",
        {
            "LeftUpperArm": [
                (0.0, rest_arm),
                (0.4, (1.05, 0.65, 0.95)),
                (0.95, (1.05, 0.65, 0.95)),
                (1.45, rest_arm),
            ],
            "RightUpperArm": [
                (0.0, rest_arm),
                (0.4, (1.05, -0.65, -0.95)),
                (0.95, (1.05, -0.65, -0.95)),
                (1.45, rest_arm),
            ],
            "LeftLowerArm": [
                (0.0, identity),
                (0.4, (1.25, 0.15, 0.45)),
                (0.95, (1.25, 0.15, 0.45)),
                (1.45, identity),
            ],
            "RightLowerArm": [
                (0.0, identity),
                (0.4, (1.25, -0.15, -0.45)),
                (0.95, (1.25, -0.15, -0.45)),
                (1.45, identity),
            ],
        },
    )

    zero = [0.0] * len(REQUIRED_SHAPE_KEYS)
    index = {name: i for i, name in enumerate(REQUIRED_SHAPE_KEYS)}

    def morph_clip(clip_name: str, active: dict[str, float], duration: float = 1.0) -> None:
        weights = zero.copy()
        for key, value in active.items():
            weights[index[key]] = value
        builder.add_morph_animation(
            clip_name,
            "Head",
            len(REQUIRED_SHAPE_KEYS),
            [(0.0, zero), (duration / 2.0, weights), (duration, zero if clip_name == "Blink" else weights)],
        )

    morph_clip("Emotion_Neutral", {}, 0.4)
    morph_clip(
        "Emotion_Serious",
        {"brow_down": 1.0, "mouth_frown": 0.9, "mouth_close": 0.55, "eye_squint": 0.45},
        0.8,
    )
    morph_clip(
        "Emotion_Positive",
        {"mouth_smile": 1.0, "brow_up": 0.65, "eye_wide": 0.5, "mouth_open": 0.2},
        0.8,
    )
    morph_clip(
        "Emotion_Concerned",
        {"brow_up": 0.85, "mouth_frown": 0.9, "eye_squint": 0.55, "mouth_wide": 0.35},
        0.8,
    )
    morph_clip("Blink", {"eye_blink_left": 1.0, "eye_blink_right": 1.0}, 0.22)

    present = {anim["name"] for anim in builder.animations}
    for required in REQUIRED_ANIMATIONS + OPTIONAL_ANIMATIONS:
        if required not in present:
            raise RuntimeError(f"Placeholder GLB missing animation {required}")

    return builder.to_glb()


def main() -> None:
    """Write presenter.glb under blender/exports and the web public folder."""
    blender_output = Path(__file__).resolve().parents[1] / "exports" / "presenter.glb"
    blender_output.parent.mkdir(parents=True, exist_ok=True)
    payload = build_presenter()
    blender_output.write_bytes(payload)
    web_output = Path(__file__).resolve().parents[2] / "frontend" / "public" / "avatars" / "presenter.glb"
    web_output.parent.mkdir(parents=True, exist_ok=True)
    web_output.write_bytes(payload)
    print(f"PASS: Wrote {blender_output} ({blender_output.stat().st_size} bytes)")
    print(f"PASS: Wrote {web_output}")


if __name__ == "__main__":
    main()
