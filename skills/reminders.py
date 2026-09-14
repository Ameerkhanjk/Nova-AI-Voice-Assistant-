"""Reminders: schedules a spoken reminder N minutes from now."""
import threading
import tts


def set_reminder(minutes: float, message: str) -> str:
    def fire():
        tts.speak(f"Reminder: {message}")
    threading.Timer(minutes * 60, fire).start()
    return f"Reminder set for {minutes:g} minutes from now: {message}"
