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

## Layout

```
skillpp/
  types.py       Skill + RouteResult (router sees name+description only)
  library.py     growing library + nearest-predecessor lookup (token Jaccard)
  rewriter.py    the Skill++ move: REFINE_PROMPT + MetadataRewriter
  router.py      MockRouter (offline) + OpenAICompatRouter
  bench.py       InterferenceBench: sessions, probes, before/after accuracy
tests/           offline end-to-end test with a scripted rewriter
examples/        quickstart script
```

## Findings so far

- The mechanism is sensitive to a subtle bug: the closest-predecessor lookup
  must exclude the skill under refinement (a freshly added skill matches
  itself with similarity 1.0 and refinement becomes a no-op).
- Predecessor choice matters: character-similarity metrics pick the wrong
  predecessor on short descriptions; token Jaccard works better.

## Honest status

Implemented and unit-tested offline. The paper's headline numbers (36.4% →
76.3% on 731 skills) have **not** been reproduced — the shipped probe sets are
small handcrafted ones. Contributing: scale the probe sets, plug real skill
libraries (Claude skills, MCP tool descriptions), try frontier routers.

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
