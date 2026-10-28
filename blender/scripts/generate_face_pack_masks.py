"""Generate placeholder face-pack mask textures (stylized, pale skin to match Mixamo body).

    python blender/scripts/generate_face_pack_masks.py

Writes PNGs to ``frontend/public/avatars/face/masks/{expression}.png``.
Runtime FacePackRegistry currently points at ``.webp`` — we also write ``.webp``
when Pillow WebP is available, else update callers to use PNG.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

# Warm stylized skin matching generate_placeholder_glb Skin (1.0, 0.84, 0.72).
SKIN = (255, 214, 184, 255)
HAIR = (107, 66, 41, 255)
WHITE = (250, 250, 252, 255)
PUPIL = (20, 18, 22, 255)
BROW = (40, 32, 28, 255)
LIP = (160, 70, 80, 255)
SIZE = 512


def _base() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Face oval
    draw.ellipse((48, 40, 464, 480), fill=SKIN)
    # Hair cap
    draw.ellipse((56, 24, 456, 220), fill=HAIR)
    draw.rectangle((56, 120, 456, 200), fill=HAIR)
    return img, draw


def _eyes(draw: ImageDraw.ImageDraw, *, open_y: int = 28, pupil_dy: int = 0, squint: bool = False) -> None:
    if squint:
        draw.arc((140, 210, 230, 250), 20, 160, fill=PUPIL, width=6)
        draw.arc((282, 210, 372, 250), 20, 160, fill=PUPIL, width=6)
        return
    for cx in (185, 327):
        draw.ellipse((cx - 42, 200, cx + 42, 200 + open_y * 2), fill=WHITE)
        draw.ellipse(
            (cx - 16, 214 + pupil_dy, cx + 16, 246 + pupil_dy),
            fill=PUPIL,
        )


def _brows(draw: ImageDraw.ImageDraw, *, dy: int = 0, inner_up: bool = False, angle: int = 0) -> None:
    # angle: negative = concerned / inner up tilt
    left = [(130, 185 + dy), (230, 178 + dy - (12 if inner_up else 0) + angle), (230, 188 + dy + angle), (130, 195 + dy)]
    right = [(282, 178 + dy - (12 if inner_up else 0) - angle), (382, 185 + dy), (382, 195 + dy), (282, 188 + dy - angle)]
    draw.polygon(left, fill=BROW)
    draw.polygon(right, fill=BROW)


def _nose(draw: ImageDraw.ImageDraw) -> None:
    draw.ellipse((240, 268, 272, 310), fill=(210, 195, 185, 255))


def _mouth(
    draw: ImageDraw.ImageDraw,
    *,
    smile: float = 0.0,
    frown: float = 0.0,
    open_amt: float = 0.0,
    shift: int = 0,
) -> None:
    cx, cy = 256 + shift, 360
    w = 70
    if open_amt > 0.2:
        h = int(18 + open_amt * 28)
        draw.ellipse((cx - w, cy - h // 2, cx + w, cy + h // 2), fill=LIP)
        draw.ellipse((cx - w + 8, cy - h // 2 + 6, cx + w - 8, cy + h // 2 - 2), fill=(40, 20, 24, 255))
        return
    if smile > 0.3:
        draw.arc((cx - w, cy - 30, cx + w, cy + 40), 20, 160, fill=LIP, width=10)
        return
    if frown > 0.3:
        draw.arc((cx - w, cy - 10, cx + w, cy + 50), 200, 340, fill=LIP, width=10)
        return
    draw.rounded_rectangle((cx - w, cy - 6, cx + w, cy + 10), radius=8, fill=LIP)


def build_mask(name: str) -> Image.Image:
    """Draw one expression mask onto a transparent canvas."""
    img, draw = _base()
    if name == "neutral":
        _brows(draw)
        _eyes(draw)
        _nose(draw)
        _mouth(draw)
    elif name == "serious":
        _brows(draw, dy=8, angle=6)
        _eyes(draw, open_y=22, squint=True)
        _nose(draw)
        _mouth(draw, frown=0.9)
    elif name == "positive":
        _brows(draw, dy=-6)
        _eyes(draw, open_y=32)
        _nose(draw)
        _mouth(draw, smile=1.0)
    elif name == "concerned":
        _brows(draw, dy=-4, inner_up=True, angle=-8)
        _eyes(draw, open_y=30)
        _nose(draw)
        _mouth(draw, frown=0.85)
    elif name == "amused":
        _brows(draw, dy=-2)
        _eyes(draw, squint=True)
        _nose(draw)
        _mouth(draw, smile=0.95)
    elif name == "curious":
        _brows(draw, dy=-10, inner_up=True)
        _eyes(draw, open_y=36, pupil_dy=-4)
        _nose(draw)
        _mouth(draw, open_amt=0.35, shift=-12)
    else:
        raise ValueError(name)
    return img


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    out = root / "frontend" / "public" / "avatars" / "face" / "masks"
    out.mkdir(parents=True, exist_ok=True)
    names = ("neutral", "serious", "positive", "concerned", "amused", "curious")
    for name in names:
        img = build_mask(name)
        png = out / f"{name}.png"
        img.save(png, format="PNG")
        print(f"PASS: Wrote {png}")
        webp = out / f"{name}.webp"
        try:
            img.save(webp, format="WEBP", quality=90)
            print(f"PASS: Wrote {webp}")
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: WebP skip for {name}: {exc}")
    print("RESULT: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
