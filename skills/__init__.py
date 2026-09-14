"""Skill registry — the single source of truth for what NOVA can do.

To add a skill: write a function anywhere, then add one entry here.
Claude discovers it automatically from the name + description + schema.

tier 1 = auto-run | tier 2 = confirm once per session | tier 3 = always confirm
"""
from skills import system, web, reminders
import memory

SKILLS = {
    "get_time": {
        "func": lambda **kw: system.get_time(),
        "tier": 1,
        "description": "Get the current date and time.",
        "schema": {"type": "object", "properties": {}},
    },
    "web_search": {
        "func": lambda **kw: web.web_search(kw["query"]),
        "tier": 1,
        "description": "Search the web for current information: weather, news, facts, anything.",
        "schema": {"type": "object",
                   "properties": {"query": {"type": "string"}},
                   "required": ["query"]},
    },
    "recall_memory": {
        "func": lambda **kw: memory.recall(kw.get("key", "")),
        "tier": 1,
        "description": "Recall stored facts about the user. Leave key empty to list everything.",
        "schema": {"type": "object", "properties": {"key": {"type": "string"}}},
    },
    "remember": {
        "func": lambda **kw: memory.remember(kw["key"], kw["value"]),
        "tier": 1,
        "description": "Store a fact about the user for future sessions, e.g. key='favorite_coffee' value='flat white'.",
        "schema": {"type": "object",
                   "properties": {"key": {"type": "string"}, "value": {"type": "string"}},
                   "required": ["key", "value"]},
    },
    "set_reminder": {
        "func": lambda **kw: reminders.set_reminder(kw["minutes"], kw["message"]),
        "tier": 1,
        "description": "Set a spoken reminder N minutes from now.",
        "schema": {"type": "object",
                   "properties": {"minutes": {"type": "number"}, "message": {"type": "string"}},
                   "required": ["minutes", "message"]},
    },
    "open_target": {
        "func": lambda **kw: system.open_target(kw["target"]),
        "tier": 2,
        "description": "Open an application, folder, or URL on the laptop. e.g. 'Downloads', 'https://gmail.com', 'spotify'.",
        "schema": {"type": "object",
                   "properties": {"target": {"type": "string"}},
                   "required": ["target"]},
    },
    "run_shell": {
        "func": lambda **kw: system.run_shell(kw["command"]),
        "tier": 3,
        "description": "Run a shell command on the laptop. Use only when no other skill fits.",
        "schema": {"type": "object",
                   "properties": {"command": {"type": "string"}},
                   "required": ["command"]},
    },
}


def as_claude_tools():
    """Convert the registry into the tool format the Claude API expects."""
    return [{"name": name, "description": s["description"], "input_schema": s["schema"]}
            for name, s in SKILLS.items()]
