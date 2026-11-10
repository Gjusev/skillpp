# CONTINUE.md — read this first when an agent picks up this repo

## What this repo is

First open implementation of Skill++ (arXiv:2611.00544): routing-aware skill
refinement via metadata rewriting. Growing skill library, nearest-predecessor
lookup, rewriter, two routers, and InterferenceBench (routing accuracy
before/after refinement per session). Read README.md and ROADMAP.md fully.

## Working rules

- **Offline-first**: the test suite must stay zero-dependency and pass with
  `python3 -m pytest tests/` (MockRouter + scripted rewriter). httpx stays a
  lazy import inside LLMClient.complete.
- **Honest claims**: never state benchmark numbers that haven't been run.
  Anything measured goes in README with the command that produced it.
- Cite the paper first (arXiv:2611.00544); independent, unofficial
  implementation — never imply affiliation with the authors.
- Commits in English, conventional-commit style (feat:/fix:/docs:).
- Before pushing: run the full offline suite; it must be green.

## Models — Z.ai Coding Plan (mandatory, no other provider)

All LLM calls in runs, examples and matrix configs MUST go through the Z.ai
Coding Plan subscription — never a pay-per-call provider:

```bash
export SKILLPP_BASE_URL="https://api.z.ai/api/coding/paas/v4"
export SKILLPP_MODEL="glm-5.3-flash"        # or glm-4.6 for stronger rewrites
export SKILLPP_API_KEY="<Z.ai key>"          # same key as the Coding Plan
```

This endpoint is OpenAI-compatible (chat/completions) — LLMClient and
OpenAICompatRouter work with it unchanged. Billing is the flat subscription:
if a run errors with a billing/endpoint error, stop and report — do NOT
switch providers to "get it working".

## Current task (do this now)

ROADMAP items 2, 3 and the first slice of 4 are DONE, measured and
committed (2026-11-10; all numbers in README "Honest status" and results/):

- scaled matrix (results/scaled_matrix.md + scaled_53.md): token-overlap
  46%->41%, tfidf 52%->56%, glm-5.3-flash 99%->100%, glm-4.6 100%->100%,
  glm-5.3 100%->100%
- real-library slice (results/real_library.md, 12 human-written pairs,
  re-run with the fixed block-scalar frontmatter parser): token-overlap
  22%->15%, tfidf 38%->35%, glm-5.3-flash 89%->92%
- decay: token-overlap drafts ~49% -> ~43% early-to-late sessions
  (results/scaled_matrix.json; direction pinned offline by tests)

Headline: Skill++ rewriting as prescribed helps only LLM-class routers on
real metadata (+3); it always hurts token-overlap, and hurts tfidf on real
metadata (helps it on generated fixtures). The paper's 36.4%->76.3% remains
unreproduced — LLM routers don't degrade at <=36 skills.

Next: ROADMAP item 5 (skill-issue integration) — needs a design decision
from the author before any code: what counts as "task performance" in
skill-issue, and how to pair its measurements with routing accuracy.
Item 4 remainder: scale the real-library bench beyond 12 pairs / probe
generation other than self-description.

## After that

Follow ROADMAP.md in order (scale benchmark -> router matrix -> real skill
libraries -> skill-issue integration). One item per commit series.
