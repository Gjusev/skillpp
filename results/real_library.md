# Real skill libraries — first slice (ROADMAP item 4)

Harvested 400 human-written skills (SKILL.md name+description) from local Claude skills/marketplace dirs; benched the 12 most-overlapping pairs (token Jaccard) with LLM-generated probes.

| router | acc before | acc after | delta |
|---|---|---|---|
| tfidf-cosine | 38% | 35% | -3% |
| token-overlap | 22% | 15% | -7% |
| llm | 89% | 92% | +3% |

Caveat: probes are LLM-generated from the descriptions themselves (favors both skills equally); rewriter = glm-5.3-flash via SKILLPP_* env.
Pairs and probes: real_library.json.
