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

ROADMAP items 1-5 all have a DONE first slice (2026-11-10; numbers in
README "Honest status" + results/). Item 5 (skill-issue integration) landed
last: scripts/skill_issue_demo.py generates skill-issue experiments that
isolate the metadata axis; results/skill_issue.md has the four measured
cells (agent routed correctly under draft AND refined metadata — no routing
failure to fix, n=1 per cell) plus two mechanism findings (name leakage;
garbage-in-garbage-out refinement when the draft copies the predecessor).

Everything is committed through the item-5 commit. The repo has no
outstanding task — what follows are the natural next slices, in value order:

1. skill-issue repetitions 3-5 per cell (spec limits allow up to 5) and a
   WEAKER routing agent (small local model via Ollama) — the router class
   where our matrix says interference actually lives.
2. Real-library pairs (results/real_library.json) as skill-issue tasks —
   human-written traps, task-level outcomes.
3. Scale the real-library bench beyond 12 pairs; probe generation other
   than self-description (independent probe author).

## After that

Follow ROADMAP.md in order (scale benchmark -> router matrix -> real skill
libraries -> skill-issue integration). One item per commit series.
