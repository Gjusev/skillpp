# Roadmap

Where this repo is and what's next. Current state: items 1–3 done and
measured, item 4 first slice done (see README "Honest status").

## Done

- Core mechanism: nearest-predecessor lookup, metadata rewriter, two routers
- InterferenceBench: sessions, probes, before/after accuracy
- Offline test suite (scripted rewriter, deterministic router), zero deps
- Two real bugs found and fixed while building it (documented in README):
  self-match in predecessor lookup, wrong metric for predecessor choice
- Item 1 — first real-LLM run (2026-11-10, Z.ai Coding Plan, glm-5.3-flash +
  glm-4.6): tooling in examples/quickstart_real.py + scripts/run_matrix.py,
  results in results/. Finding: 100% routing accuracy before AND after on
  the shipped fixtures — too easy for frontier routers; scale needed.
- Item 2 — scaled benchmark (24 sessions, 179 probes, 36-skill final
  library): crowding induces real decay for weak routers (token-overlap
  drafts ~49% -> ~43% early-to-late, results/scaled_matrix.json; direction
  pinned offline by tests/test_scaled.py). results/scaled_matrix.md.
- Item 3 — router matrix: token-overlap 46%->41% (rewriting HURTS),
  tfidf-cosine 52%->56% (helps on generated fixtures), glm-5.3-flash
  99%->100%, glm-4.6 and glm-5.3 100%->100% (nothing to fix at this
  scale). Skill++'s benefit lives below the LLM-router class here.
- Item 4, first slice — real libraries: scripts/harvest_real.py found the
  interference precondition in 400 human-written local skills (incl. a
  byte-identical description pair); benched the top 12 pairs
  (results/real_library.md): token-overlap 22%->15%, tfidf 38%->35%,
  glm-5.3-flash 89%->92% — on real metadata only the LLM router benefits.
- Item 5, first slice — skill-issue integration:
  scripts/skill_issue_demo.py generates skill-issue experiments isolating
  the metadata axis (same task, same trap library, draft vs skillpp-refined
  description; external verifier checks the TASK). Measured n=1x4
  (results/skill_issue.md): agent routed correctly under both metadatas —
  no routing failure to fix. Two findings: name leakage defeats the
  metadata axis unless names are neutral; the rewriter polishes an
  untruthful draft into confident wrong metadata (it never sees the body).

## Next (in order)

### 1. First real-LLM run — the headline number
Run `examples/quickstart.py` with an actual model (Ollama `qwen2.5:7b` on a
16GB machine, or any OpenAI-compatible API) on the shipped probe sets and put
the before/after table in the README. Small, but it converts "mechanism
implemented" into "mechanism works".

### 2. Scale the benchmark
- Grow sessions from 2 to 20+ with generated trap pairs (paraphrase existing
  skills, add near-duplicates with shifted scope)
- Probe sets: 4 probes/session -> 20+; add distractor skills that share
  vocabulary with BOTH members of a trap pair
- Target: reproduce the paper's qualitative claim (accuracy decays as the
  library grows, recovers after refinement)

### 3. Router matrix
The paper's routers differ from ours. Run the same suites across:
- MockRouter (token overlap, shipped)
- OpenAICompatRouter with a small model (7-9B)
- OpenAICompatRouter with a frontier model
- an embedding-similarity router (the naive baseline most tooling actually
  uses — MCP tool descriptions, Claude skills)
One result table, one finding: which router class benefits most from
rewriting?

### 4. Real skill libraries as fixtures
Import actual skill libraries as benchmark material — this repo's own author
has candidate corpora: Claude Code skills folders, MCP server tool
descriptions, and the 6-agent Hermes setup (SOUL.md + skills) as a live test.
Measure: does Skill++ rewriting break or fix routing on skills written by
humans (not generated)?

### 5. Integration: `skill-issue` harness
[skill-issue](https://github.com/Gjusev/skill-issue) measures whether a skill
helps the agent. Natural merge: skill-issue measures task performance with
skills; skillpp measures routing accuracy. Combined = does fixing routing
also fix task performance?

## Non-goals

- No router training (the paper's point is that you don't need it)
- No serving layer — this is a library + benchmark, not a proxy
