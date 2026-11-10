"""Routers. The router reads ONLY name+description pairs (paper's setting)."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from .llm import LLMClient
from .types import RouteResult, Skill


class BaseRouter(ABC):
    @abstractmethod
    def route(self, query: str, skills: list[Skill]) -> RouteResult:
        """Return the skill the router picks for this query."""


class MockRouter(BaseRouter):
    """Deterministic router for offline tests: token overlap between the query
    and each description. Deliberately naive — exactly the kind of router that
    suffers interference when two skills share vocabulary."""

    def route(self, query: str, skills: list[Skill]) -> RouteResult:
        q = set(re.findall(r"\w+", query.lower()))
        scores: dict[str, float] = {}
        for s in skills:
            d = set(re.findall(r"\w+", s.description.lower()))
            n = s.name.lower()
            name_bonus = 1.0 if any(w in n for w in q) else 0.0
            scores[s.name] = (len(q & d) / max(len(d), 1)) + name_bonus
        chosen = max(skills, key=lambda s: scores[s.name])
        return RouteResult(chosen=chosen.name, scores=scores)


class OpenAICompatRouter(BaseRouter):
    """LLM router via any OpenAI-compatible endpoint. Outputs the chosen name."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    def route(self, query: str, skills: list[Skill]) -> RouteResult:
        listing = "\n".join(
            f"- {s.name}: {s.description}" for s in skills
        )
        prompt = (
            "Pick the single best skill for the task. Reply with the skill name "
            "only, nothing else.\n\n"
            f"Skills:\n{listing}\n\nTask: {query}\nSkill name:"
        )
        raw = self.llm.complete(prompt).strip()
        names = {s.name: s.name for s in skills}
        chosen = None
        # exact match first, then substring (models like to decorate names)
        if raw in names:
            chosen = raw
        else:
            for name in names:
                if name.lower() in raw.lower():
                    chosen = name
                    break
        if chosen is None:
            # the model failed to name a skill: count it as a miss (picking
            # skills[0] would silently score probes that expect the first skill)
            chosen = ""
        return RouteResult(chosen=chosen, raw=raw)
