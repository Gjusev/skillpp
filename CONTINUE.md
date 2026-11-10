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

ROADMAP.md item 1 (first real-LLM run) is DONE — see results/matrix.md and
README "Honest status" (measured 2026-11-10: glm-5.3-flash and glm-4.6 both
route the shipped fixtures at 100% before and after refinement — ceiling
effect, fixtures too easy for frontier routers). Tooling shipped:
examples/quickstart_real.py, scripts/run_matrix.py + matrix.config.json,
skillpp/fixtures.py (one source of truth for the shipped sessions).

Next: ROADMAP.md item 2 — scale the benchmark so interference can appear:

1. Grow the fixture set: from 2 sessions to 20+ (skillpp/fixtures.py or a
   generator), trap pairs via paraphrase + near-duplicates with shifted
   scope; add distractor skills sharing vocabulary with BOTH members of a
   trap pair.
2. Probe sets: from 4/session to 20+, including probes that should stay with
   the OLD skill (regression).
3. Run the scaled suite through scripts/run_matrix.py and commit results.
4. Success = the qualitative claim shows up: accuracy decays as the library
   grows, refinement recovers it. If frontier routers still sit at 100%,
   that IS the finding — report it and move to item 3 (router matrix with
   MockRouter/embedding routers where interference actually bites).

## After that

Follow ROADMAP.md in order (scale benchmark -> router matrix -> real skill
libraries -> skill-issue integration). One item per commit series.
