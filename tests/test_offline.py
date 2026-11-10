"""Offline test: the whole mechanism with a deterministic mock LLM + MockRouter.

Proves the wiring works end to end without any network. The interesting claim
(routing accuracy recovers after refinement) needs a real LLM as rewriter;
run examples/quickstart.py with SKILLPP_BASE_URL/SKILLPP_MODEL for that.
"""

from skillpp import (
    InterferenceBench,
    MetadataRewriter,
    MockRouter,
    Session,
    Skill,
    SkillLibrary,
)


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


def base_skills():
    return [
        Skill(
            name="sql-optimizer",
            description="Rewrites slow SQL queries: index hints, join order, partition pruning.",
            domain_tags=("sql", "performance"),
        ),
        Skill(
            name="pdf-redactor",
            description="Removes personal data from PDF files permanently, with verification.",
            domain_tags=("privacy", "pdf"),
        ),
        Skill(
            name="email-triage",
            description="Classifies inbound support email by intent, urgency and language.",
            domain_tags=("email", "triage"),
        ),
    ]


def sessions():
    return [
        Session(
            new_skill=Skill(
                name="sql-explainer",
                description="Explains what a SQL query does, step by step, in plain language.",
                domain_tags=("sql", "explainability"),
            ),
            probes=[
                ("make this slow join query faster", "sql-optimizer"),
                ("what does this query do in plain words", "sql-explainer"),
                ("why is my database query slow", "sql-optimizer"),
                ("explain the difference between these two queries", "sql-explainer"),
            ],
            regression_probes=[
                ("black out the names in this contract pdf", "pdf-redactor"),
                ("sort incoming customer emails by urgency", "email-triage"),
            ],
        ),
        Session(
            new_skill=Skill(
                name="pdf-signature-check",
                description="Verifies whether a PDF contains digital signatures and if they are valid.",
                domain_tags=("pdf", "signatures"),
            ),
            probes=[
                ("check if this signed contract is valid", "pdf-signature-check"),
                ("remove the iban from this pdf before sending", "pdf-redactor"),
                ("does this document have a valid signature", "pdf-signature-check"),
                ("anonymize the patient names in this report", "pdf-redactor"),
            ],
            regression_probes=[
                ("speed up this group by query", "sql-optimizer"),
                ("label these emails as complaint or renewal", "email-triage"),
                ("explain this window function query", "sql-explainer"),
            ],
        ),
    ]


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
