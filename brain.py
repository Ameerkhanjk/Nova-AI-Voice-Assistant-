"""The brain: sends your command to Claude, executes the tools it picks,
loops until Claude has a final spoken answer.

This loop is exactly why NOVA handles multi-part commands: Claude can
request several tool calls in one turn, we run them all, feed the results
back, and Claude composes one combined answer.
"""
import anthropic
import config
import permissions
from skills import SKILLS, as_claude_tools

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment
history = []  # conversation memory within this session


def handle(user_text: str) -> str:
    history.append({"role": "user", "content": user_text})
    # Keep the conversation from growing forever (saves tokens and money)
    if len(history) > 24:
        del history[:len(history) - 24]
        while history and history[0]["role"] != "user":
            del history[0]

    while True:
        try:
            response = client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=config.MAX_TOKENS,
                system=config.SYSTEM_PROMPT,
                tools=as_claude_tools(),
                messages=history,
            )
        except anthropic.AuthenticationError:
            history.pop()
            return "My API key isn't working. Check it at console.anthropic.com."
        except anthropic.APIConnectionError:
            history.pop()
            return "I can't reach the internet right now."
        history.append({"role": "assistant", "content": response.content})

        # Collect any tool calls Claude made this turn
        tool_calls = [b for b in response.content if b.type == "tool_use"]
        if not tool_calls:
            # No more tools needed -> final spoken answer
            return "".join(b.text for b in response.content if b.type == "text")

        # Execute every tool call (this is the multi-command magic)
        results = []
        for call in tool_calls:
            skill = SKILLS[call.name]
            desc = f"{call.name} with {call.input}" if call.input else call.name
            if permissions.check(call.name, skill["tier"], desc):
                try:
                    output = skill["func"](**call.input)
                except Exception as e:
                    output = f"Error: {e}"
            else:
                output = "User denied permission for this action."
            print(f"  [tool] {call.name}({call.input}) -> {str(output)[:100]}")
            results.append({"type": "tool_result", "tool_use_id": call.id,
                            "content": str(output)})

        history.append({"role": "user", "content": results})
        # Loop back so Claude can see the results and either answer or chain more tools
