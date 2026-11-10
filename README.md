# skillpp

**First open implementation of [Skill++](https://arxiv.org/abs/2611.00544) — "Skill++: Towards Lifelong Agents via Routing-Aware Skill Refinement" (2026). Independent and unofficial; cite the paper first.**

The problem it solves: agent routers pick skills by reading only their names
and descriptions. When you add a new skill whose metadata resembles an
installed one, the router starts confusing them — the new skill can displace
the old one even though nothing about the old skill or the router changed.

The Skill++ move: before a new skill joins the library, retrieve its closest
installed predecessor and rewrite its description to state what it supports,
how it differs from that predecessor, and what it excludes. No router
training, no labeled data. The paper reports routing accuracy rising from
36.4% to 76.3% as a library grows to 731 skills.

## TL;DR — what we measured (2026-11-10)

The benefit of Skill++ rewriting **depends on the router class**, and it is
not the direction a naive reading of the paper suggests:

| router class | generated traps | real human-written metadata |
|---|---|---|
| token-overlap | 46% → 41% (**worse**) | 22% → 15% (**much worse**) |
| tfidf / similarity (what most tooling ships) | 52% → 56% (+3) | 38% → 35% (−3) |
| LLM router (frontier) | 99% → 100% (nothing to fix) | 89% → 92% (**+3**) |

Why: the refined description names the predecessor and echoes its
vocabulary — poison for anything that scores by shared words, usable signal
for a router that reads the whole sentence. The paper's 36.4% → 76.3%
remains **unreproduced** here: frontier LLM routers barely fail at ≤36
skills, so there is nothing for refinement to recover. Full tables and
caveats in [Measured results](#measured-results); raw artifacts in
`results/`.

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

## What this repo tests

The `InterferenceBench` builds the paper's setting directly:

1. start with a base library of disjoint skills
2. each session adds a new skill that overlaps an installed one (the trap)
3. route a probe set **before** refinement (draft metadata) and **after**
   refinement, and report the accuracy delta per session

Three routers ship with it: a deterministic token-overlap `MockRouter`
(offline, no network), a TF-IDF-cosine `TfidfRouter` (offline stand-in for
the embedding-similarity routers most tooling uses), and
`OpenAICompatRouter` (any OpenAI-compatible endpoint — Ollama, GLM,
OpenAI...).

## Measured results

All numbers below were actually run (2026-11-10, Z.ai Coding Plan endpoint,
glm-5.3-flash as rewriter unless noted). Raw output: `results/`. Every doc
number is cross-checked against `results/*.json`.

**1. Shipped fixtures** (3 base skills, 2 sessions, 13 probes —
`results/matrix.md`): glm-5.3-flash and glm-4.6 as router+rewriter both
route 100% before and after. Ceiling effect; too easy.

**2. Scaled fixtures** (`results/scaled_matrix.md`; 12 domains × 3 sibling
skills, 24 sessions, 179 probes; library crowding induces real decay —
token-overlap routing on drafts drops from ~49% (early sessions) to ~43%
(late sessions), per-session arrays in `results/scaled_matrix.json`;
`tests/test_scaled.py` pins the decay direction offline, not these values):

| router | acc before (mean) | acc after (mean) |
|---|---|---|
| token-overlap (MockRouter) | 46% | 41% |
| tfidf-cosine (TfidfRouter) | 52% | 56% |
| LLM glm-5.3-flash | 99% | 100% |
| LLM glm-4.6 | 100% | 100% |
| LLM glm-5.3 | 100% | 100% |

**3. Real skill libraries, first slice** (`results/real_library.md`; 12
most-overlapping human-written pairs from 400 harvested local skills, 60-
skill routing library, 6 LLM-generated probes per pair):

| router | acc before | acc after |
|---|---|---|
| token-overlap | 22% | 15% |
| tfidf-cosine | 38% | 35% |
| LLM glm-5.3-flash | 89% | 92% |

What this does and does not say: the paper's headline numbers (36.4% →
76.3% on 731 skills) remain **unreproduced** — our LLM routers barely fail
at ≤36 skills, so there is nothing for refinement to recover. What we can
say: on generated fixtures, similarity-class routers gain (+3) and lexical
overlap loses (−5); on human-written near-duplicates the rewrite hurts
everything except the LLM router (−7 overlap, −3 tfidf, **+3 LLM**). The
refined text names the predecessor and echoes its vocabulary — poison for
anything that scores by shared words, signal for a router that reads the
whole sentence. Caveats: scaled fixtures and their probes were authored
together (favors the mechanism); real-library probes are LLM-generated from
the descriptions themselves; rewriter run-to-run variance as noted in
Findings.

**4. skill-issue integration** (`results/skill_issue.md`, ROADMAP item 5
first slice): skillpp generates [skill-issue](https://github.com/Gjusev/skill-issue)
experiments isolating the metadata axis — same task, same trap library,
B's description draft vs skillpp-refined; an external verifier checks the
TASK outcome (not just routing). Measured (Claude Code headless, 1 rep per
cell): the agent routed correctly under both metadatas in all four cells —
no routing failure occurred to fix, consistent with the router matrix
above. The integration itself is the deliverable: metadata → routing →
task is now one measurable chain, ready for repetitions and weaker routing
agents.

## Findings while building it

- The mechanism is sensitive to a subtle bug: the closest-predecessor lookup
  must exclude the skill under refinement (a freshly added skill matches
  itself with similarity 1.0 and refinement becomes a no-op).
- Predecessor choice matters: character-similarity metrics pick the wrong
  predecessor on short descriptions; token Jaccard works better.
- Token Jaccard still misses morphological variants: on the first real run it
  picked `email-triage` (shares "language") over `sql-optimizer` ("queries"
  ≠ "query" as tokens) as predecessor for `sql-explainer`. Lemma- or
  substring-aware matching would fix this.
- **The rewriter assumes the draft is truthful.** Fed a draft that copies
  the predecessor's description verbatim (the Jaccard-1.00 real-world
  pathology), it produced a polished, confident, WRONG refinement — it never
  sees the skill body (found while building the skill-issue integration).
- **Near-duplicate metadata exists in real, human-maintained libraries**:
  harvesting 400 local Claude skills/marketplace entries found a pair with
  byte-identical descriptions (token Jaccard 1.00) plus
  langsmith↔phoenix-observability, autoglm-search-image↔websearch,
  cirq↔qiskit and 8 more confusable pairs.
- **Skill names leak the answer in routing experiments**: with descriptive
  names, metadata quality cannot bind — names alone disambiguate. Any
  metadata-axis experiment needs neutral names.
- **In a live agent, draft-vs-refined metadata made no difference on a trap
  task** (Claude Code headless via skill-issue, n=1×4): the agent routed
  correctly under sloppy and refined metadata alike.
- Benchmark numbers vary run to run: the rewriter samples at temperature
  0.2, and each session is scored with earlier sessions' refined
  descriptions still installed, so late-session accuracy depends on the
  rewrite history. Means and sign directions were stable across our runs;
  per-session numbers are noisy.

## Reproduce our numbers

Everything below needs `SKILLPP_BASE_URL` / `SKILLPP_MODEL` /
`SKILLPP_API_KEY` pointing at any OpenAI-compatible endpoint (we used the
Z.ai Coding Plan; rewriter = glm-5.3-flash throughout).

```bash
python scripts/run_matrix.py                              # table 1 (shipped fixtures)
python scripts/run_matrix.py scripts/scaled_matrix.config.json   # table 2 (mock, tfidf, flash, 4.6)
python scripts/run_matrix.py scripts/scaled_53.config.json       # table 2, glm-5.3 arm
python scripts/harvest_real.py report    # real-library pair report (offline)
python scripts/harvest_real.py bench     # table 3 (12 human-written pairs)
python scripts/skill_issue_demo.py --refine llm --names neutral    # item-5 experiment specs
node <skill-issue>/src/cli.ts run experiments/skill-issue-routing-neutral/tasks/routing-draft.json
node <skill-issue>/src/cli.ts run experiments/skill-issue-routing-neutral/tasks/routing-refined.json
```

Expect run-to-run variance in the rewrites (temperature 0.2); tables record
one run each, raw arrays in `results/*.json`.

## Layout

```
skillpp/
  types.py       Skill + RouteResult (router sees name+description only)
  library.py     growing library + nearest-predecessor lookup (token Jaccard)
  rewriter.py    the Skill++ move: REFINE_PROMPT + MetadataRewriter
  router.py      MockRouter + TfidfRouter (offline) + OpenAICompatRouter
  bench.py       InterferenceBench: sessions, probes, before/after accuracy
  fixtures.py    shipped probe sets (base library + interference sessions)
  scaled.py      scaled fixtures: 12 domains, 24 sessions, 179 probes
tests/           offline tests: mechanism, decay, matrix tolerance, harvest
examples/        quickstart.py (demo) and quickstart_real.py (writes results/)
scripts/         run_matrix.py (+ 3 configs), harvest_real.py, skill_issue_demo.py
experiments/     skill-issue experiment specs (committed, reproducible)
results/         committed benchmark output — the summary tables are
                 matrix.md / scaled_matrix.md / real_library.md / skill_issue.md
```

Next steps and non-goals: see [ROADMAP.md](ROADMAP.md). Where the work
picked up: [CONTINUE.md](CONTINUE.md).

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
