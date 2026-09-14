"""Text-to-speech.

On macOS this uses the built-in `say` command — more reliable and better
quality than pyttsx3, which often fails silently on Mac.

Voice: "Daniel" is the built-in British male voice. Refined, calm, butler-ish.
To hear every voice your Mac has, run:   python tts.py
Other good British options: Oliver, Arthur, Serena (female).
Change the voice in config.py.
"""
import subprocess
import sys

import config

_proc = None


def speak(text: str):
    """Speak text out loud. Blocks until finished."""
    global _proc
    if not text:
        return
    print(f"{config.ASSISTANT_NAME}: {text}")

    if sys.platform == "darwin":  # macOS
        try:
            _proc = subprocess.Popen(
                ["say", "-v", config.TTS_VOICE, "-r", str(config.TTS_RATE), text])
            _proc.wait()
        except Exception as e:
            print(f"[tts error: {e}]")
    else:  # Windows / Linux fallback
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", config.TTS_RATE)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[tts unavailable: {e}]")


def stop():
    """Interrupt whatever NOVA is currently saying."""
    global _proc
    if _proc and _proc.poll() is None:
        _proc.terminate()


def list_voices():
    """Print every voice installed on this Mac."""
    if sys.platform == "darwin":
        subprocess.run(["say", "-v", "?"])


if __name__ == "__main__":
    list_voices()
    speak("NOVA online. All systems nominal.")
