"""Skill++: routing-aware skill refinement (first open implementation).

Implements the core mechanism from "Skill++: Towards Lifelong Agents via
Routing-Aware Skill Refinement" (arXiv:2611.00544): when a new skill enters a
library, rewrite its metadata against its closest installed predecessor so the
router can tell them apart. No router training, no labeled data.

This is an independent, unofficial implementation. Cite the paper first.
"""

from .types import Skill, RouteResult
from .library import SkillLibrary
from .llm import LLMClient
from .rewriter import MetadataRewriter
from .router import BaseRouter, MockRouter, TfidfRouter, OpenAICompatRouter
from .bench import BenchmarkReport, InterferenceBench, Session, run_benchmark
from .fixtures import base_skills, sessions
from .scaled import scaled_base_skills, scaled_sessions

__version__ = "0.1.0"
__all__ = [
    "Skill",
    "RouteResult",
    "SkillLibrary",
    "LLMClient",
    "MetadataRewriter",
    "BaseRouter",
    "MockRouter",
    "TfidfRouter",
    "OpenAICompatRouter",
    "InterferenceBench",
    "Session",
    "BenchmarkReport",
    "run_benchmark",
    "base_skills",
    "sessions",
    "scaled_base_skills",
    "scaled_sessions",
]
