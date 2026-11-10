# InterferenceBench — router/rewriter matrix

Generated 2026-11-10T19:29:41+00:00 by `python scripts/run_matrix.py scaled_53.config.json` (scaled fixtures: 12 base skills, 24 interference sessions, 179 probes).

| backend | router | model | acc before (mean) | acc after (mean) | delta (mean) | final session before | final session after |
|---|---|---|---|---|---|---|---|
| zai-coding | llm | glm-5.3 | 100% | 100% | +0% | 100% | 100% |

Routing accuracy = share of probes routed to the intended skill.
“before” = draft metadata, “after” = Skill++ refinement against the closest predecessor.
