"""3-tier permission system.

Tier 1: auto-execute (read-only, harmless)
Tier 2: confirm once per session, then allowed
Tier 3: always confirm, every single time
"""
import tts

_session_approved = set()  # tier-2 skills approved this session

# The GUI (app.py) replaces this with a dialog prompt; terminal mode uses input().
asker = None


def check(skill_name: str, tier: int, description: str) -> bool:
    """Return True if the action is allowed to run."""
    if tier == 1:
        return True

    if tier == 2 and skill_name in _session_approved:
        return True

    # Ask the user (via HUD dialog if running the app, else the terminal)
    question = f"Allow {skill_name}? {description}"
    if asker:
        allowed = asker(question)
    else:
        tts.speak(f"Permission needed: {description}. Allow?")
        answer = input(f"  [{skill_name}] {description} — allow? (y/n): ").strip().lower()
        allowed = answer in ("y", "yes")

    if allowed and tier == 2:
        _session_approved.add(skill_name)  # remember for the rest of the session
    return allowed
