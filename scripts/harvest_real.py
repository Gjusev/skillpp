"""ROADMAP item 4, first slice: real, human-written skill libraries as fixtures.

Two modes:

  python scripts/harvest_real.py report  [roots...]     # offline
      Walk roots for SKILL.md files (default: ~/.claude/skills and the two
      largest local plugin marketplaces), parse name+description from YAML
      frontmatter, and print the most-overlapping skill pairs by token
      Jaccard — the interference precondition in a real library.

  python scripts/harvest_real.py bench  [roots...]      # needs SKILLPP_* env
      Take the top overlapping pairs, LLM-generate 3+3 probe queries per pair
      (caveat: probes generated FROM the descriptions, which favors both
      skills equally), then run InterferenceBench: tfidf + mock + llm routers,
      real LLM rewriter. Writes results/real_library.{json,md}.

Only descriptions are read; the committed artifact (results/) contains just
the pairs actually benched, not the full harvest.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skillpp import (
    InterferenceBench,
    LLMClient,
    MetadataRewriter,
    MockRouter,
    OpenAICompatRouter,
    Session,
    Skill,
    TfidfRouter,
)

DEFAULT_ROOTS = [
    Path.home() / ".claude" / "skills",
    Path.home() / ".claude" / "plugins" / "marketplaces" / "academic-research-skills",
    Path.home() / ".claude" / "plugins" / "marketplaces" / "anthropic-agent-skills",
]
MAX_SKILLS = 400
PAIRS = 12          # pairs benched
DISTRACTORS = 48    # additional harvested skills in the base library
PROBES_PER = 3


def harvest(roots: list[Path]) -> list[dict]:
    """name+description from SKILL.md frontmatter; simple key: value parsing."""
    skills: list[dict] = []
    seen: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("SKILL.md")):
            if len(skills) >= MAX_SKILLS:
                break
            text = path.read_text(encoding="utf-8", errors="replace")
            m = re.match(r"^---\n(.*?)\n---", text, re.S)
            if not m:
                continue
            fields = dict(
                re.findall(r"^(name|description):\s*(.+)$", m.group(1), re.M)
            )
            name = fields.get("name", "").strip().strip("\"'")
            desc = fields.get("description", "").strip().strip("\"'")
            if not name or not desc or name in seen:
                continue
            seen.add(name)
            skills.append({"name": name, "description": desc, "source": str(path)})
    return skills


def tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))


def jaccard(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    return len(ta & tb) / len(ta | tb) if ta | tb else 0.0


def top_pairs(skills: list[dict], k: int) -> list[tuple[dict, dict, float]]:
    pairs = [
        (a, b, jaccard(a["description"], b["description"]))
        for i, a in enumerate(skills)
        for b in skills[i + 1:]
        if a["name"] != b["name"]
    ]
    pairs.sort(key=lambda p: -p[2])
    chosen, used = [], set()
    for a, b, sim in pairs:
        if a["name"] in used or b["name"] in used:
            continue
        chosen.append((a, b, sim))
        used |= {a["name"], b["name"]}
        if len(chosen) >= k:
            break
    return chosen


def gen_probes(llm: LLMClient, a: dict, b: dict) -> dict[str, list[str]]:
    prompt = (
        "Two skills compete for the same user queries.\n\n"
        f"Skill A — {a['name']}: {a['description']}\n"
        f"Skill B — {b['name']}: {b['description']}\n\n"
        f"Write {PROBES_PER} short user queries best handled by skill A and "
        f"{PROBES_PER} best handled by skill B. Queries must sound like real "
        "user requests, not skill descriptions. Output format exactly:\n"
        "A: q1 | q2 | q3\nB: q1 | q2 | q3"
    )
    raw = llm.complete(prompt)
    lines = dict(re.findall(r"^([AB]):\s*(.+)$", raw.strip(), re.M))
    return {
        "A": [q.strip() for q in lines.get("A", "").split("|") if q.strip()],
        "B": [q.strip() for q in lines.get("B", "").split("|") if q.strip()],
    }


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "report"
    roots = [Path(p) for p in argv[2:]] or DEFAULT_ROOTS
    skills = harvest(roots)
    print(f"harvested {len(skills)} skills from {len(roots)} roots")

    pairs = top_pairs(skills, PAIRS)
    print(f"\ntop overlapping pairs (token Jaccard) — the interference precondition:")
    for a, b, sim in pairs:
        print(f"  {sim:.2f}  {a['name']}  <->  {b['name']}")

    if mode == "report":
        return 0

    llm = LLMClient()
    print(f"\nprobe model: {llm.model} @ {llm.base_url}")
    # base library: each pair's A skill (installed long ago, draft metadata)
    # plus a fixed slice of the rest as distractors; sessions add B
    pair_names = {s["name"] for p in pairs for s in p[:2]}
    distractors = [s for s in skills if s["name"] not in pair_names][:DISTRACTORS]
    base = [Skill(name=s["name"], description=s["description"])
            for s in [p[0] for p in pairs] + distractors]

    sessions, fixture = [], []
    for a, b, sim in pairs:
        probes = gen_probes(llm, a, b)
        if not probes["A"] or not probes["B"]:
            print(f"  skip {a['name']}/{b['name']}: probe generation failed")
            continue
        new_skill = Skill(name=b["name"], description=b["description"])
        sessions.append(Session(
            new_skill=new_skill,
            probes=[(q, b["name"]) for q in probes["B"]],
            regression_probes=[(q, a["name"]) for q in probes["A"]],
        ))
        fixture.append({"pair": [a["name"], b["name"]], "jaccard": sim,
                        "probes": probes, "a": a, "b": b})

    routers: list[tuple[str, object]] = [
        ("tfidf-cosine", TfidfRouter()),
        ("token-overlap", MockRouter()),
        ("llm", OpenAICompatRouter(llm)),
    ]
    rows = []
    for label, router in routers:
        print(f"== router {label}", flush=True)
        report = InterferenceBench(base, router, MetadataRewriter(llm)).run(sessions)
        b_mean = sum(report.accuracy_before) / len(report.accuracy_before)
        a_mean = sum(report.accuracy_after) / len(report.accuracy_after)
        rows.append({"router": label, "acc_before": b_mean, "acc_after": a_mean,
                     "per_session_before": report.accuracy_before,
                     "per_session_after": report.accuracy_after})
        print(f"   mean {b_mean:.0%} -> {a_mean:.0%}")

    out = Path(__file__).resolve().parents[1] / "results"
    out.mkdir(exist_ok=True)
    (out / "real_library.json").write_text(json.dumps({
        "roots": [str(r) for r in roots],
        "harvested": len(skills),
        "pairs": fixture,
        "results": rows,
    }, indent=2), encoding="utf-8")
    md = ["# Real skill libraries — first slice (ROADMAP item 4)", "",
          f"Harvested {len(skills)} human-written skills (SKILL.md name+description) "
          f"from local Claude skills/marketplace dirs; benched the {len(fixture)} most-"
          "overlapping pairs (token Jaccard) with LLM-generated probes.", "",
          "| router | acc before | acc after | delta |", "|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['router']} | {r['acc_before']:.0%} | {r['acc_after']:.0%} | "
                  f"{r['acc_after'] - r['acc_before']:+.0%} |")
    md += ["", "Caveat: probes are LLM-generated from the descriptions themselves "
           "(favors both skills equally); rewriter = glm-5.3-flash via SKILLPP_* env.",
           "Pairs and probes: real_library.json.", ""]
    (out / "real_library.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nwrote {out / 'real_library.json'} and {out / 'real_library.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
