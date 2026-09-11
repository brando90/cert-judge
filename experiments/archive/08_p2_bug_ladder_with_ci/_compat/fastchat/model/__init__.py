"""Minimal stand-in for fastchat.model.get_conversation_template.

veribench.utils.call_llm only uses three things from a Conversation:
  - .roles (tuple of role names; index 0 = user)
  - .append_message(role, content)
  - .to_openai_api_messages()  -> list of {"role", "content"} dicts

This shim returns an object that satisfies that contract directly, so we can
import veribench on machines that cannot install the real fastchat (which
hard-imports torch at module load time).
"""

from typing import Dict, List, Tuple


class _MinimalConversation:
    roles: Tuple[str, str] = ("user", "assistant")

    def __init__(self) -> None:
        self._messages: List[Tuple[str, str]] = []

    def append_message(self, role: str, content: str) -> None:
        self._messages.append((role, content))

    def to_openai_api_messages(self) -> List[Dict[str, str]]:
        return [{"role": r, "content": c} for r, c in self._messages if c is not None]


def get_conversation_template(model_name: str) -> _MinimalConversation:  # noqa: ARG001 (model_name unused)
    return _MinimalConversation()
