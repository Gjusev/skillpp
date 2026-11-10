# skillpp

**First open implementation of [Skill++](https://arxiv.org/abs/2611.00544) — "Skill++: Towards Lifelong Agents via Routing-Aware Skill Refinement" (2026).**

The problem it solves: agent routers pick skills by reading only their names
and descriptions. When you add a new skill whose metadata resembles an
installed one, the router starts confusing them — the new skill can displace
the old one even though nothing about the old skill or the router changed.

The Skill++ move: before a new skill joins the library, retrieve its closest
installed predecessor and rewrite its description to state what it supports,
how it differs from that predecessor, and what it excludes. No router
training, no labeled data. The paper reports routing accuracy rising from
36.4% to 76.3% as a library grows to 731 skills.

## What this repo tests

The `InterferenceBench` builds the paper's setting directly:

1. start with a base library of disjoint skills
2. each session adds a new skill that overlaps an installed one (the trap)
3. route a probe set **before** refinement (draft metadata) and **after**
   refinement, and report the accuracy delta per session

Two routers ship with it: a deterministic token-overlap `MockRouter` (offline,
no network) and `OpenAICompatRouter` (any OpenAI-compatible endpoint — Ollama,
GLM, OpenAI...).

## Quickstart

```bash
pip install -e .
python -m pytest tests/          # offline, zero dependencies
```

With a real LLM (rewriter + LLM router):

```python
import os
os.environ["SKILLPP_BASE_URL"] = "http://localhost:11434/v1"  # Ollama, or any OpenAI-compatible API
os.environ["SKILLPP_MODEL"] = "qwen2.5:7b"

from skillpp import LLMClient, MetadataRewriter, OpenAICompatRouter, InterferenceBench, Session, Skill

base = [Skill(name="sql-optimizer", description="Rewrites slow SQL queries..."), ...]
sessions = [Session(new_skill=Skill(...), probes=[("query", "expected-skill"), ...])]
bench = InterferenceBench(base, OpenAICompatRouter(), MetadataRewriter(LLMClient()))
report = bench.run(sessions)
print(report.summary())
```

Or run the shipped fixtures end-to-end (writes into `results/`):

```bash
export SKILLPP_BASE_URL="https://api.z.ai/api/coding/paas/v4"  # or any OpenAI-compatible endpoint
export SKILLPP_MODEL="glm-5.3-flash"
export SKILLPP_API_KEY="<key>"
python examples/quickstart_real.py   # one model -> results/first_run.json
python scripts/run_matrix.py         # every backend in scripts/matrix.config.json -> results/matrix.{json,md}
```

## Layout

```
skillpp/
  types.py       Skill + RouteResult (router sees name+description only)
  library.py     growing library + nearest-predecessor lookup (token Jaccard)
  rewriter.py    the Skill++ move: REFINE_PROMPT + MetadataRewriter
  router.py      MockRouter (offline) + OpenAICompatRouter
  bench.py       InterferenceBench: sessions, probes, before/after accuracy
  fixtures.py    shipped probe sets (base library + interference sessions)
tests/           offline tests: scripted rewriter + matrix failure tolerance
examples/        quickstart.py (demo) and quickstart_real.py (writes results/)
scripts/         run_matrix.py + matrix.config.json (multi-backend runs)
results/         committed benchmark output (matrix.md is the summary table)
```

## Findings so far

- The mechanism is sensitive to a subtle bug: the closest-predecessor lookup
  must exclude the skill under refinement (a freshly added skill matches
  itself with similarity 1.0 and refinement becomes a no-op).
- Predecessor choice matters: character-similarity metrics pick the wrong
  predecessor on short descriptions; token Jaccard works better.
- Token Jaccard still misses morphological variants: on the first real run it
  picked `email-triage` (shares "language") over `sql-optimizer` ("queries"
  ≠ "query" as tokens) as predecessor for `sql-explainer`. Lemma- or
  substring-aware matching would fix this.
- Frontier-class routers don't interfere on small libraries (see Honest
  status) — interference needs scale, weaker router classes, or both.

## Honest status

First real-LLM run done 2026-11-10, Z.ai Coding Plan endpoint, both router
and rewriter on the same model (`python scripts/run_matrix.py`, shipped
fixtures: 3 base skills, 2 interference sessions, 13 probes; raw output in
`results/matrix.md` / `results/matrix.json` / `results/first_run.json`):

| model (router + rewriter) | acc before | acc after |
|---|---|---|
| glm-5.3-flash | 100% (mean and final) | 100% |
| glm-4.6 | 100% (mean and final) | 100% |

That is a **ceiling effect, not evidence about the paper's claim**: the
shipped fixture is too small to confuse these routers, so refinement has
nothing to fix (each rewrite is a proper supports/differs/excludes rewrite —
see the refined descriptions in `results/matrix.json`). The paper's headline
numbers (36.4% → 76.3% on 731 skills) remain **unreproduced**. Next steps
are ROADMAP items 2 (scale: 20+ sessions, 20+ probes each, distractor
skills) and 3 (router matrix incl. token-overlap and embedding routers,
where interference actually bites).

## Citation

This is an independent, unofficial implementation. Cite the paper first:

```bibtex
@article{skillpp2026,
  title={Skill++: Towards Lifelong Agents via Routing-Aware Skill Refinement},
  journal={arXiv preprint arXiv:2611.00544},
  year={2026}
}
```

## License

MIT
