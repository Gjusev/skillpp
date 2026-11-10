"""The interference benchmark: does metadata rewriting fix skill confusion?

Session structure (mirrors the paper's growing-library setting):
  - start with a base library of disjoint skills
  - in each session, add a NEW skill that overlaps an installed one
    (the "trap": similar vocabulary, different job)
  - before/after applying Skill++ refinement, route a probe set and score
    accuracy: does the router pick the intended skill for each query?

Metric: routing accuracy before refinement vs after (the paper's headline
number is the final-session gap: 36.4% -> 76.3%).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .library import SkillLibrary
from .rewriter import MetadataRewriter
from .router import BaseRouter
from .types import Skill


@dataclass
class Session:
    """One session = one overlapping skill added + its probes."""

    new_skill: Skill
    # (query, correct_skill_name) pairs probing the crowded region
    probes: list[tuple[str, str]]
    # earlier skills' probes, to check the new skill doesn't steal them
    regression_probes: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class BenchmarkReport:
    sessions: list[dict]
    accuracy_before: list[float]
    accuracy_after: list[float]

    def summary(self) -> str:
        lines = ["session | library | acc before | acc after | delta"]
        for i, s in enumerate(self.sessions):
            delta = self.accuracy_after[i] - self.accuracy_before[i]
            lines.append(
                f"{i + 1} | {s['library_size']} | "
                f"{self.accuracy_before[i]:.2%} | {self.accuracy_after[i]:.2%} | "
                f"{delta:+.2%}"
            )
        return "\n".join(lines)


class InterferenceBench:
    def __init__(self, base_skills: list[Skill], router: BaseRouter,
                 rewriter: MetadataRewriter | None = None) -> None:
        self.library = SkillLibrary()
        for s in base_skills:
            self.library.add(s)
        self.router = router
        self.rewriter = rewriter

    def _score(self, probes: list[tuple[str, str]]) -> float:
        if not probes:
            return 1.0
        views = self.library.router_views()
        skills = list(self.library.skills.values())
        correct = 0
        for query, expected in probes:
            result = self.router.route(query, skills)
            if result.chosen == expected:
                correct += 1
        return correct / len(probes)

    def run(self, sessions: list[Session]) -> BenchmarkReport:
        acc_before: list[float] = []
        acc_after: list[float] = []
        session_reports: list[dict] = []

        for sess in sessions:
            # 1) add the new skill with its ORIGINAL (draft) metadata
            draft = Skill(
                name=sess.new_skill.name,
                description=sess.new_skill.description,
                domain_tags=sess.new_skill.domain_tags,
            )
            self.library.add(draft)

            all_probes = sess.probes + sess.regression_probes
            before = self._score(all_probes)

            # 2) apply Skill++ refinement to the new skill
            if self.rewriter is not None:
                self.rewriter.refine(self.library.skills[draft.name], self.library)
            after = self._score(all_probes)

            acc_before.append(before)
            acc_after.append(after)
            session_reports.append({
                "new_skill": draft.name,
                "library_size": len(self.library),
                "refined_description": draft.description,
                "acc_before": before,
                "acc_after": after,
            })

        return BenchmarkReport(sessions=session_reports,
                               accuracy_before=acc_before,
                               accuracy_after=acc_after)


def run_benchmark(base_skills: list[Skill], router: BaseRouter,
                  sessions: list[Session],
                  rewriter: MetadataRewriter | None = None) -> BenchmarkReport:
    """Convenience one-shot runner."""
    bench = InterferenceBench(base_skills, router, rewriter)
    return bench.run(sessions)
