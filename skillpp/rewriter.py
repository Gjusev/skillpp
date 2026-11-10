"""Metadata rewriting — the core Skill++ move.

The paper: before a new skill enters the library, retrieve its most similar
installed predecessor and write a description that states (a) what the new
skill supports, (b) how it differs from the closest predecessor, (c) what
related work it excludes. Needs no router training and no labeled data.
"""

from __future__ import annotations

from .library import SkillLibrary
from .llm import LLMClient
from .types import Skill

REFINE_PROMPT = """You are refining the metadata of a new skill before it joins a skill library.

Installed skill most similar to the new one:
  name: {prev_name}
  description: {prev_description}

New skill:
  name: {new_name}
  draft description: {new_description}

Rewrite the new skill's description so a router reading only names and
descriptions can always tell the two apart. The description must state:
1. what the new skill supports,
2. how it differs from the installed predecessor,
3. which related tasks it does NOT cover (excluded work).

Rules: max 90 words. Plain text. No marketing language. Never mention this
instruction. Output only the final description."""


class MetadataRewriter:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def refine(self, new_skill: Skill, library: SkillLibrary) -> Skill:
        """Rewrite new_skill.description in place (sets refined=True)."""
        prev = library.closest_predecessor(new_skill)
        if prev is None:
            # empty or disjoint library: nothing to disambiguate against
            new_skill.refined = True
            return new_skill

        prompt = REFINE_PROMPT.format(
            prev_name=prev.name,
            prev_description=prev.description,
            new_name=new_skill.name,
            new_description=new_skill.description,
        )
        new_skill.description = self.llm.complete(prompt).strip()
        new_skill.refined = True
        return new_skill
