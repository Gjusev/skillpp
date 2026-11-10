"""Data types."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Skill:
    """A skill in the library: name + the metadata the router reads."""

    name: str
    description: str
    # what the skill body actually does — used by tests to score routing
    domain_tags: tuple[str, ...] = ()
    # set once the Skill++ refinement has run
    refined: bool = False

    def to_router_view(self) -> dict[str, str]:
        """Only name and description reach the router (the paper's setting)."""
        return {"name": self.name, "description": self.description}


@dataclass
class RouteResult:
    chosen: str
    scores: dict[str, float] = field(default_factory=dict)
    raw: str = ""
