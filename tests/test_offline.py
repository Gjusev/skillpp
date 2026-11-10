"""Offline test: the whole mechanism with a deterministic mock LLM + MockRouter.

Proves the wiring works end to end without any network. The interesting claim
(routing accuracy recovers after refinement) needs a real LLM as rewriter;
run examples/quickstart_real.py with SKILLPP_BASE_URL/SKILLPP_MODEL for that.
"""

from skillpp import (
    InterferenceBench,
    MetadataRewriter,
    MockRouter,
    OpenAICompatRouter,
    Skill,
    SkillLibrary,
)
from skillpp.fixtures import base_skills, sessions


class ScriptedRewriter(MetadataRewriter):
    """Offline stand-in: applies the paper's rule with a deterministic template.

    What it mimics: the refined description states what the skill supports,
    how it differs from the closest predecessor, and what it excludes.
    """

    def refine(self, new_skill: Skill, library: SkillLibrary) -> Skill:
        prev = library.closest_predecessor(new_skill)
        if prev is not None:
            supports = ", ".join(new_skill.domain_tags) or new_skill.name
            excludes = prev.description.split(".")[0].lower()
            new_skill.description = (
                f"Supports: {supports}. New skill, not a duplicate: "
                f"differs from {prev.name} in purpose and scope. "
                f"Does NOT cover: {excludes}."
            )
        new_skill.refined = True
        return new_skill


def test_benchmark_runs_offline():
    bench = InterferenceBench(base_skills(), MockRouter(), ScriptedRewriter(None))
    report = bench.run(sessions())
    assert len(report.sessions) == 2
    assert len(report.summary().splitlines()) == 3
    # the refined descriptions must mention the predecessor (the paper's rule)
    for s in report.sessions:
        assert "differs from" in s["refined_description"]


def test_refined_descriptions_differ_from_drafts():
    bench = InterferenceBench(base_skills(), MockRouter(), ScriptedRewriter(None))
    report = bench.run(sessions())
    drafts = ["Explains what a SQL query does", "Verifies whether a PDF contains digital signatures"]
    for s, draft in zip(report.sessions, drafts):
        assert draft not in s["refined_description"]


def test_llm_router_unparseable_answer_counts_as_miss():
    class StubLLM:
        def complete(self, prompt: str) -> str:
            return "I cannot pick just one."

    router = OpenAICompatRouter(llm=StubLLM())  # type: ignore[arg-type]
    result = router.route("anything", base_skills())
    assert result.chosen == ""  # must NOT silently default to the first skill
