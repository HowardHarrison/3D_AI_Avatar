"""API tests for POST /api/v1/tts/synthesize and GET audio (mocked TTS)."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.api.dependencies import get_tts_cache_dir, get_tts_provider
from app.domain.interfaces.tts_provider import TtsProvider, TtsResult
from app.main import app

_TEST_CACHE = Path(__file__).resolve().parent / "_tts_test_cache"


class _FakeTts(TtsProvider):
    """Writes a tiny fake MP3 marker file into the cache."""

    def __init__(self, cache_dir: Path) -> None:
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, text: str, *, voice_id: str | None = None) -> TtsResult:
        file_id = "a" * 32 + ".mp3"
        (self._cache_dir / file_id).write_bytes(b"ID3FAKE")
        return TtsResult(
            audio_url=f"/api/v1/tts/audio/{file_id}",
            duration_seconds=1.5,
        )


client = TestClient(app)


def setup_function() -> None:
    """Install fake TTS and a test cache dir before each test."""
    _TEST_CACHE.mkdir(parents=True, exist_ok=True)
    app.dependency_overrides[get_tts_cache_dir] = lambda: _TEST_CACHE
    app.dependency_overrides[get_tts_provider] = lambda: _FakeTts(_TEST_CACHE)


def teardown_function() -> None:
    """Clear overrides and test cache files."""
    app.dependency_overrides.clear()
    get_tts_cache_dir.cache_clear()
    get_tts_provider.cache_clear()
    if _TEST_CACHE.exists():
        for child in _TEST_CACHE.iterdir():
            child.unlink(missing_ok=True)
        _TEST_CACHE.rmdir()


def test_synthesize_ok() -> None:
    """Route returns audioUrl and estimated duration."""
    response = client.post(
        "/api/v1/tts/synthesize",
        json={"text": "Hello avatar"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["audioUrl"].startswith("/api/v1/tts/audio/")
    assert body["durationSeconds"] == 1.5


def test_synthesize_rejects_empty_text() -> None:
    """Pydantic rejects blank text."""
    response = client.post("/api/v1/tts/synthesize", json={"text": ""})
    assert response.status_code == 422


def test_get_audio_ok() -> None:
    """Synthesize then fetch the cached MP3 bytes."""
    create = client.post("/api/v1/tts/synthesize", json={"text": "Hi"})
    assert create.status_code == 200
    audio_url = create.json()["audioUrl"]
    audio = client.get(audio_url)
    assert audio.status_code == 200
    assert audio.content == b"ID3FAKE"
    assert "audio/mpeg" in audio.headers.get("content-type", "")
