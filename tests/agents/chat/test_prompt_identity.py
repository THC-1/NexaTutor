"""Product identity remains stable when stale Partner metadata is present."""

from __future__ import annotations

from deeptutor.agents.chat.prompt_blocks import ChatPromptAssembler
from deeptutor.core.context import UnifiedContext


PROMPTS = {
    "general": "You are DeepTutor, an interactive tutor.",
    "runtime_policy": "policy",
    "loop": {"system": "loop"},
}


def _blocks(context: UnifiedContext):
    assembler = ChatPromptAssembler(prompts=PROMPTS, language="en")
    return assembler.blocks(context=context, tool_manifest="- none")


def test_chat_turn_keeps_product_identity() -> None:
    blocks = _blocks(UnifiedContext(user_message="hi"))
    general = next(block.content for block in blocks if block.name == "general")

    assert general == "You are DeepTutor, an interactive tutor."


def test_legacy_partner_identity_metadata_is_inert() -> None:
    context = UnifiedContext(
        user_message="hi",
        metadata={"agent_identity": {"name": "frank", "description": "study buddy"}},
    )
    blocks = _blocks(context)
    general = next(block.content for block in blocks if block.name == "general")

    assert general == "You are DeepTutor, an interactive tutor."
    assert all(block.name != "partner_turn_policy" for block in blocks)
