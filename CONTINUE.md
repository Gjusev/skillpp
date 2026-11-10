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

ROADMAP items 2 + 3 tooling is DONE and committed (scaled fixtures, TfidfRouter,
router-matrix configs, real-library harvester). What is MEASURED so far
(results/scaled_matrix.md, real glm-5.3-flash rewriter):

- token-overlap router: 46% -> 41% (refinement HURTS lexical overlap)
- tfidf-cosine router: 53% -> 57% (refinement helps)
- offline decay confirmed: MockRouter accuracy drops ~48% -> ~38% as the
  scaled library grows (tests/test_scaled.py pins it)

PENDING: the two LLM-router arms (glm-5.3-flash, glm-4.6) of
scripts/scaled_matrix.config.json and the whole scripts/harvest_real.py
bench. A first attempt died to endpoint 429s (two concurrent runs on one
subscription — since fixed: jobs must run sequentially); the re-run was
killed by the OS memory-pressure reaper before backend 1 finished. Restart
with (single process, ~3h):

    export SKILLPP_BASE_URL="https://api.z.ai/api/coding/paas/v4"
    export SKILLPP_MODEL="glm-5.3-flash"
    export SKILLPP_API_KEY="$ZAI_API_KEY"
    python scripts/run_matrix.py scripts/scaled_matrix.config.json \
        && python scripts/harvest_real.py bench

Then: update README "Honest status" with the full four-row scaled table +
real-library table (numbers must match results/*.json exactly), then item 5
(skill-issue integration) is next.

## After that

Follow ROADMAP.md in order (scale benchmark -> router matrix -> real skill
libraries -> skill-issue integration). One item per commit series.
