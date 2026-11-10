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

ROADMAP.md item 1 — first real-LLM run:

1. Add `examples/quickstart_real.py`: InterferenceBench with
   OpenAICompatRouter + MetadataRewriter(LLMClient()) over the shipped
   sessions, configured via SKILLPP_BASE_URL / SKILLPP_MODEL env vars.
2. Add `scripts/run_matrix.py`: benchmark across a list of (base_url, model)
   pairs from a JSON config; writes `results/matrix.json` plus a markdown
   table. One backend down must not crash the run.
3. If a real endpoint is available (SKILLPP_BASE_URL set), run it and commit
   results + markdown table into `results/`. If not, commit the tooling with
   an empty results dir marked "not yet run" and stop there.
4. Update README "Honest status" with whatever was actually measured.

## After that

Follow ROADMAP.md in order (scale benchmark -> router matrix -> real skill
libraries -> skill-issue integration). One item per commit series.
