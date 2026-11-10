"""Growing skill library with nearest-predecessor lookup."""

from __future__ import annotations

import re

from .types import Skill


class SkillLibrary:
    def __init__(self) -> None:
        self.skills: dict[str, Skill] = {}

    def add(self, skill: Skill) -> None:
        self.skills[skill.name] = skill

    def closest_predecessor(self, skill: Skill) -> Skill | None:
        """Most similar INSTALLED skill, excluding the skill itself.

        The paper retrieves the most similar earlier skills; a single best
        match by token-overlap ratio is enough for the mechanism under test.
        """
        best, best_score = None, 0.0
        target = set(re.findall(r"\w+", skill.description.lower()))
        for other in self.skills.values():
            if other.name == skill.name:
                continue  # the skill under refinement must not match itself
            other_tokens = set(re.findall(r"\w+", other.description.lower()))
            union = target | other_tokens
            score = len(target & other_tokens) / len(union) if union else 0.0
            if score > best_score:
                best, best_score = other, score
        return best

    def router_views(self) -> list[dict[str, str]]:
        return [s.to_router_view() for s in self.skills.values()]

    def __len__(self) -> int:
        return len(self.skills)
