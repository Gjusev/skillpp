# InterferenceBench — router/rewriter matrix

Generated 2026-11-10T15:56:51+00:00 by `python scripts/run_matrix.py matrix.config.json` (shipped sessions: 3 base skills, 2 interference sessions, 13 probes).

| backend | model | acc before (mean) | acc after (mean) | delta (mean) | final session before | final session after |
|---|---|---|---|---|---|---|
| zai-coding | glm-5.3-flash | 100% | 100% | +0% | 100% | 100% |
| zai-coding | glm-4.6 | 100% | 100% | +0% | 100% | 100% |

Routing accuracy = share of probes routed to the intended skill.
“before” = draft metadata, “after” = Skill++ refinement against the closest predecessor.
