"""NOVA desktop app — runs as a local web page in your regular browser.

Why a browser tab instead of a native window: native window libraries
(pywebview) can crash on macOS with a "trace trap" when Python isn't a
Cocoa "framework build" — very common with Anaconda/Miniconda. Running
NOVA as a local page sidesteps that entirely. It looks and feels the same.

Run with:  python app.py
It opens http://127.0.0.1:8765 in your default browser automatically.

Push-to-talk: hold OPTION (Alt) + SPACE anywhere, speak, release.
Works globally even when the browser tab isn't focused.
"""
import json
import os
import threading
import time
import webbrowser
from queue import Empty, Queue

import psutil
from flask import Flask, jsonify, request, send_from_directory
from pynput import keyboard

import brain
import config
import permissions
import recorder
import stt
import tts

flask_app = Flask(__name__, static_folder="ui", static_url_path="")

events = Queue()               # events waiting to be picked up by the browser
pending_confirm = {}            # confirm id -> {"event": Event, "result": bool}
confirm_counter = 0

rec = recorder.Recorder()
recording = False
busy = False
held = set()

OPTION_KEYS = {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
               keyboard.Key.alt_gr}


def is_ptt_down():
    return bool(held & OPTION_KEYS) and keyboard.Key.space in held


def push(kind: str, payload):
    events.put({"kind": kind, "payload": payload})


def gui_permission_prompt(question: str) -> bool:
    """Tier 2/3 confirmations show as a modal in the browser tab."""
    global confirm_counter
    confirm_counter += 1
    cid = confirm_counter
    ev = threading.Event()
    pending_confirm[cid] = {"event": ev, "result": False}
    tts.speak("Permission needed.")
    push("confirm", {"id": cid, "question": question})
    ev.wait(timeout=120)  # give up after 2 minutes if nobody answers
    return pending_confirm.pop(cid, {}).get("result", False)


def handle_command(audio):
    global busy
    busy = True
    try:
        push("state", "thinking")
        text = stt.transcribe(audio)
        if not text.strip():
            push("state", "idle")
            msg = "Sorry, can you repeat that again?"
            push("msg", {"who": "nova", "text": msg})
            tts.speak(msg)
            return
        push("msg", {"who": "user", "text": text})
        reply = brain.handle(text)
        push("state", "speaking")
        push("msg", {"who": "nova", "text": reply})
        tts.speak(reply)
    except Exception as e:
        print("[error]", e)
        push("msg", {"who": "error", "text": f"Something went wrong: {e}"})
        tts.speak("Something went wrong. Check the terminal.")
    finally:
        push("state", "idle")
        busy = False


def on_press(key):
    global recording
    held.add(key)
    if is_ptt_down():
        tts.stop()  # barge-in: talking to NOVA interrupts its speech
    if is_ptt_down() and not recording and not busy:
        recording = True
        push("state", "listening")
        rec.start()


def on_release(key):
    global recording
    held.discard(key)
    if recording and not is_ptt_down():
        recording = False
        audio = rec.stop()
        push("state", "thinking")
        if audio is None or len(audio) < config.SAMPLE_RATE * config.MIN_SPEECH_SECONDS:
            push("state", "idle")
            msg = "Sorry, can you repeat that again? Hold the keys while you speak."
            push("msg", {"who": "nova", "text": msg})
            threading.Thread(target=tts.speak, args=(msg,), daemon=True).start()
            return
        threading.Thread(target=handle_command, args=(audio,), daemon=True).start()


# --- routes --------------------------------------------------------------

@flask_app.route("/")
def index():
    return send_from_directory("ui", "index.html")


@flask_app.route("/events")
def get_events():
    """The browser polls this a few times a second."""
    batch = []
    try:
        while True:
            batch.append(events.get_nowait())
    except Empty:
        pass
    return jsonify(batch)


@flask_app.route("/confirm", methods=["POST"])
def confirm():
    data = request.get_json(force=True)
    cid = data.get("id")
    if cid in pending_confirm:
        pending_confirm[cid]["result"] = bool(data.get("allow"))
        pending_confirm[cid]["event"].set()
    return jsonify({"ok": True})


@flask_app.route("/stats")
def stats():
    return jsonify({"cpu": int(psutil.cpu_percent()),
                    "ram": int(psutil.virtual_memory().percent),
                    "model": config.WHISPER_MODEL,
                    "hotkey": "OPTION + SPACE"})


def warm_up():
    push("msg", {"who": "system", "text": "Loading speech model…"})
    try:
        import numpy as np
        stt.transcribe(np.zeros(config.SAMPLE_RATE, dtype="float32"))
        push("msg", {"who": "system", "text": "Ready. Hold Option + Space and speak."})
        tts.speak(f"{config.ASSISTANT_NAME} online.")
    except Exception as e:
        push("msg", {"who": "error", "text": f"Speech model failed to load: {e}"})


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        push("msg", {"who": "error",
             "text": 'No API key found. In Terminal run: '
                     'export ANTHROPIC_API_KEY="sk-ant-..." then restart NOVA.'})
    else:
        permissions.asker = gui_permission_prompt
        threading.Thread(target=warm_up, daemon=True).start()
        keyboard.Listener(on_press=on_press, on_release=on_release).start()

    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:8765")).start()
    print("NOVA is running at http://127.0.0.1:8765  (opening in your browser...)")
    flask_app.run(port=8765, debug=False, use_reloader=False)
