"""All NOVA settings in one place."""

# --- Push-to-talk ---
# Mac: "option_space" = hold Option(Alt) + Space.  Right Ctrl doesn't exist on Mac.
# Other choices: "option" (Option alone), "f13", "ctrl_r" (Windows/Linux)
PTT_KEY = "option_space"

# --- Speech-to-text (Whisper) ---
WHISPER_MODEL = "base"       # tiny / base / small / medium (bigger = better, slower)
WHISPER_DEVICE = "cpu"
SAMPLE_RATE = 16000
MIN_SPEECH_SECONDS = 0.4     # shorter than this -> "I didn't catch that"

# --- The brain (Claude) ---
CLAUDE_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024
SYSTEM_PROMPT = (
    "You are NOVA, a voice assistant running on the user's Mac. "
    "Be concise and composed — your replies are spoken aloud, so answer in "
    "1-3 short sentences. You can call multiple tools in one turn; if the user "
    "gives several commands at once, handle all of them and confirm briefly."
)

# --- Text-to-speech ---
# macOS built-in voices. "Daniel" = British male, calm and refined.
# Run `python tts.py` to hear the full list installed on your Mac.
TTS_VOICE = "Daniel"
TTS_RATE = 180               # words per minute

# --- Assistant identity ---
ASSISTANT_NAME = "NOVA"
