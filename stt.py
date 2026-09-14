"""Speech-to-text using faster-whisper (runs locally, handles accents well)."""
from faster_whisper import WhisperModel
import config

_model = None


def transcribe(audio) -> str:
    """Convert recorded audio (numpy float32 array) to text."""
    global _model
    if _model is None:
        print(f"Loading Whisper '{config.WHISPER_MODEL}' model (first time only)...")
        _model = WhisperModel(config.WHISPER_MODEL, device=config.WHISPER_DEVICE,
                              compute_type="int8")
    segments, _ = _model.transcribe(audio, language=None)  # auto-detect language
    return " ".join(seg.text.strip() for seg in segments).strip()
