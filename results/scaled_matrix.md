# InterferenceBench — router/rewriter matrix

Generated 2026-11-10T16:29:27+00:00 by `python scripts/run_matrix.py scaled_matrix.config.json` (scaled fixtures: 12 base skills, 24 interference sessions, 179 probes).

| backend | router | model | acc before (mean) | acc after (mean) | delta (mean) | final session before | final session after |
|---|---|---|---|---|---|---|---|
| token-overlap | mock | glm-5.3-flash | 46% | 41% | -5% | 38% | 25% |
| tfidf-cosine | tfidf | glm-5.3-flash | 53% | 57% | +5% | 75% | 75% |
| zai-coding | llm | glm-5.3-flash | — | — | — | — | error: HTTPStatusError: Client error '429 Too Many Requests' for url 'https://api.z.ai/api/cod... |
| zai-coding | llm | glm-4.6 | — | — | — | — | error: HTTPStatusError: Client error '429 Too Many Requests' for url 'https://api.z.ai/api/cod... |

Routing accuracy = share of probes routed to the intended skill.
“before” = draft metadata, “after” = Skill++ refinement against the closest predecessor.
