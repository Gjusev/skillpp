"""Shipped benchmark fixtures: the base library + interference sessions.

One source of truth for examples, scripts and tests ("the shipped sessions").
Each session adds a skill that overlaps an installed one — the paper's trap.
"""

from __future__ import annotations

from .bench import Session
from .types import Skill


def base_skills() -> list[Skill]:
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


def sessions() -> list[Session]:
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
