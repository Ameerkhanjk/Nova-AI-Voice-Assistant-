"""NOVA terminal version (no window).

Run with:  python main.py

Hold OPTION (Alt) + SPACE and speak. Release to send.
"""
import threading
from pynput import keyboard

import brain
import config
import recorder
import stt
import tts

rec = recorder.Recorder()
recording = False
busy = False
held = set()

# --- hotkey: Option + Space (Option alone won't trigger) ---
OPTION_KEYS = {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
               keyboard.Key.alt_gr}

def is_ptt_down():
    return bool(held & OPTION_KEYS) and keyboard.Key.space in held


def handle_command(audio):
    global busy
    busy = True
    try:
        text = stt.transcribe(audio)
        if not text.strip():
            msg = "Sorry, can you repeat that again?"
            print(f"\n{config.ASSISTANT_NAME}: {msg}")
            tts.speak(msg)
            return
        print(f"You: {text}")
        reply = brain.handle(text)
        tts.speak(reply)
    except Exception as e:
        print(f"[error] {e}")
        tts.speak("Something went wrong.")
    finally:
        busy = False


def on_press(key):
    global recording
    held.add(key)
    if is_ptt_down():
        tts.stop()  # barge-in: talking to NOVA interrupts its speech
    if is_ptt_down() and not recording and not busy:
        recording = True
        print("[listening...]")
        rec.start()


def on_release(key):
    global recording
    held.discard(key)
    if recording and not is_ptt_down():
        recording = False
        audio = rec.stop()
        if audio is None or len(audio) < config.SAMPLE_RATE * config.MIN_SPEECH_SECONDS:
            msg = "Sorry, can you repeat that again? Hold the keys while you speak."
            print(f"\n{config.ASSISTANT_NAME}: {msg}")
            threading.Thread(target=tts.speak, args=(msg,), daemon=True).start()
            return
        print()  # newline
        threading.Thread(target=handle_command, args=(audio,), daemon=True).start()


def main():
    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print('No API key found. Run:  export ANTHROPIC_API_KEY="sk-ant-..."  then try again.')
        return
    print(f"=== {config.ASSISTANT_NAME} is running ===")
    print("Hold OPTION + SPACE and speak. Ctrl+C to quit.")
    print()
    tts.speak(f"{config.ASSISTANT_NAME} online.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
