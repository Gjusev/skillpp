"""Quickstart: run the interference benchmark with a real LLM (rewriter + router).

Set SKILLPP_BASE_URL and SKILLPP_MODEL first (any OpenAI-compatible endpoint —
Ollama works: SKILLPP_BASE_URL=http://localhost:11434/v1 SKILLPP_MODEL=qwen2.5:7b).
"""

import os

from skillpp import (
    InterferenceBench,
    LLMClient,
    MetadataRewriter,
    OpenAICompatRouter,
    Session,
    Skill,
)

BASE = [
    Skill(name="sql-optimizer", description="Rewrites slow SQL queries: index hints, join order, partition pruning."),
    Skill(name="pdf-redactor", description="Removes personal data from PDF files permanently, with verification."),
    Skill(name="email-triage", description="Classifies inbound support email by intent, urgency and language."),
]

SESSIONS = [
    Session(
        new_skill=Skill(name="sql-explainer", description="Explains what a SQL query does, step by step."),
        probes=[
            ("make this slow join query faster", "sql-optimizer"),
            ("explain this query in plain words", "sql-explainer"),
        ],
        regression_probes=[("black out the names in this contract pdf", "pdf-redactor")],
    ),
    Session(
        new_skill=Skill(name="pdf-signature-check", description="Checks whether a PDF's digital signatures are valid."),
        probes=[
            ("is this signed contract valid", "pdf-signature-check"),
            ("remove the iban from this pdf", "pdf-redactor"),
        ],
        regression_probes=[("speed up this group by query", "sql-optimizer")],
    ),
]

bench = InterferenceBench(BASE, OpenAICompatRouter(), MetadataRewriter(LLMClient()))
report = bench.run(SESSIONS)
print(report.summary())
for s in report.sessions:
    print(f"\n[{s['new_skill']}] refined description:\n  {s['refined_description']}")
