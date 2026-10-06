"""Write a short royalty-free presenter test tone as MP3 (or WAV fallback).

    python blender/scripts/generate_test_audio.py
"""

from __future__ import annotations

import math
import struct
import subprocess
import sys
import wave
from pathlib import Path


def _write_wav(path: Path, duration_sec: float = 4.0, sample_rate: int = 22050) -> None:
    """Write a simple A4 tone with a short fade so it is pleasant for debug playback."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n_frames = int(duration_sec * sample_rate)
    with wave.open(str(path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_frames):
            t = i / sample_rate
            envelope = min(1.0, t / 0.05, (duration_sec - t) / 0.2)
            sample = envelope * 0.2 * math.sin(2.0 * math.pi * 440.0 * t)
            frames.extend(struct.pack("<h", int(sample * 32767)))
        wav_file.writeframes(frames)


def main() -> None:
    """Create public/audio/test-presenter.mp3 when ffmpeg is available, else WAV."""
    repo = Path(__file__).resolve().parents[2]
    audio_dir = repo / "apps" / "web" / "public" / "audio"
    wav_path = audio_dir / "test-presenter.wav"
    mp3_path = audio_dir / "test-presenter.mp3"
    _write_wav(wav_path)
    ffmpeg = "ffmpeg"
    try:
        subprocess.run(
            [ffmpeg, "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", "-q:a", "5", str(mp3_path)],
            check=True,
            capture_output=True,
        )
        print(f"PASS: Wrote {mp3_path}")
    except (OSError, subprocess.CalledProcessError):
        mp3_path.write_bytes(wav_path.read_bytes())
        print("WARNING: ffmpeg not found; copied WAV bytes to test-presenter.mp3")
        print("Replace with a real MP3 when ffmpeg is available.")
        print(f"PASS: Wrote {wav_path}")


if __name__ == "__main__":
    sys.exit(main() or 0)
