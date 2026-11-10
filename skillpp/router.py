"""Routers. The router reads ONLY name+description pairs (paper's setting)."""

from __future__ import annotations

import math
import re
from abc import ABC, abstractmethod
from collections import Counter

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


class TfidfRouter(BaseRouter):
    """Offline stand-in for the embedding-similarity routers most tooling
    actually uses (MCP tool pickers, skill matchers): TF-IDF bag-of-words
    cosine between query and each description. Deterministic, zero-dep."""

    def route(self, query: str, skills: list[Skill]) -> RouteResult:
        docs = [re.findall(r"\w+", s.description.lower()) for s in skills]
        q = re.findall(r"\w+", query.lower())
        n = len(docs) or 1
        df = Counter(w for d in docs for w in set(d))
        idf = lambda w: math.log(1 + n / max(df[w], 1))  # query-only words: no dot with any doc anyway

        def vec(words: list[str]) -> dict[str, float]:
            tf = Counter(words)
            return {w: (1 + math.log(c)) * idf(w) for w, c in tf.items()}

        qv = vec(q)
        scores: dict[str, float] = {}
        for s, d in zip(skills, docs):
            dv = vec(d)
            dot = sum(c * dv[w] for w, c in qv.items() if w in dv)
            norm = (sum(v * v for v in qv.values()) ** 0.5) or 1.0
            dnorm = (sum(v * v for v in dv.values()) ** 0.5) or 1.0
            scores[s.name] = dot / (norm * dnorm)
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
