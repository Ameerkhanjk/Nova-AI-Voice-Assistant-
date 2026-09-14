"""Long-term memory: a simple SQLite key-value store.
Lets NOVA remember facts between sessions ("my advisor's name is...", etc.)."""
import sqlite3

DB = "nova_memory.db"


def _conn():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)")
    return c


def remember(key: str, value: str) -> str:
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO memory VALUES (?, ?)", (key, value))
    return f"Remembered: {key} = {value}"


def recall(key: str = "") -> str:
    with _conn() as c:
        if key:
            row = c.execute("SELECT value FROM memory WHERE key = ?", (key,)).fetchone()
            return row[0] if row else f"Nothing stored for '{key}'."
        rows = c.execute("SELECT key, value FROM memory").fetchall()
        return "\n".join(f"{k}: {v}" for k, v in rows) or "Memory is empty."
