"""Run InterferenceBench across several (base_url, model) backends.

    python scripts/run_matrix.py [config.json] [results_dir]

Config (default scripts/matrix.config.json):

    {"backends": [
        {"name": "...", "base_url": "...", "model": "...", "api_key_env": "..."},
        ...
    ]}

Writes <results_dir>/matrix.json (raw numbers) and matrix.md (one table row
per backend: mean and final-session routing accuracy before/after Skill++
refinement). A backend that errors is recorded as an error row — one endpoint
down must not kill the run.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without pip install

from skillpp import InterferenceBench, LLMClient, MetadataRewriter, OpenAICompatRouter
from skillpp.fixtures import base_skills, sessions


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def run_backend(cfg: dict) -> dict:
    llm = LLMClient(
        base_url=cfg["base_url"],
        model=cfg["model"],
        api_key=os.environ.get(cfg.get("api_key_env", "SKILLPP_API_KEY"), "none"),
    )
    bench = InterferenceBench(base_skills(), OpenAICompatRouter(llm), MetadataRewriter(llm))
    report = bench.run(sessions())
    return {
        "name": cfg["name"],
        "model": cfg["model"],
        "base_url": cfg["base_url"],
        "accuracy_before": report.accuracy_before,
        "accuracy_after": report.accuracy_after,
        "refined_descriptions": {
            s["new_skill"]: s["refined_description"] for s in report.sessions
        },
    }


def markdown(rows: list[dict], config_path: Path) -> str:
    base, sess = base_skills(), sessions()
    n_probes = sum(len(s.probes) + len(s.regression_probes) for s in sess)
    lines = [
        "# InterferenceBench — router/rewriter matrix",
        "",
        f"Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} by "
        f"`python scripts/run_matrix.py {config_path.name}` (shipped sessions: "
        f"{len(base)} base skills, {len(sess)} interference sessions, {n_probes} probes).",
        "",
        "| backend | model | acc before (mean) | acc after (mean) | delta (mean) | final session before | final session after |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        if "error" in r:
            err = r["error"].replace("|", "/")
            lines.append(f"| {r['name']} | {r['model']} | — | — | — | — | error: {err} |")
            continue
        b, a = mean(r["accuracy_before"]), mean(r["accuracy_after"])
        fb, fa = r["accuracy_before"][-1], r["accuracy_after"][-1]
        lines.append(
            f"| {r['name']} | {r['model']} | {b:.0%} | {a:.0%} | {a - b:+.0%} | {fb:.0%} | {fa:.0%} |"
        )
    lines += [
        "",
        "Routing accuracy = share of probes routed to the intended skill.",
        "“before” = draft metadata, “after” = Skill++ refinement against the closest predecessor.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    config_path = Path(argv[1]) if len(argv) > 1 else Path(__file__).parent / "matrix.config.json"
    out_dir = Path(argv[2]) if len(argv) > 2 else Path(__file__).resolve().parents[1] / "results"
    cfg = json.loads(config_path.read_text(encoding="utf-8"))

    rows: list[dict] = []
    for b in cfg["backends"]:
        print(f"== {b.get('name', '?')} : {b.get('model', '?')}", flush=True)
        try:
            r = run_backend(b)
            rows.append(r)
            print(
                f"   mean {mean(r['accuracy_before']):.0%} -> {mean(r['accuracy_after']):.0%}, "
                f"final {r['accuracy_before'][-1]:.0%} -> {r['accuracy_after'][-1]:.0%}"
            )
        except Exception as e:  # one backend down must not kill the run
            rows.append({"name": b["name"], "model": b.get("model", "?"), "error": f"{type(e).__name__}: {e}"})
            print(f"   ERROR {type(e).__name__}: {e}")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "matrix.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    (out_dir / "matrix.md").write_text(markdown(rows, config_path), encoding="utf-8")
    print(f"\nwrote {out_dir / 'matrix.json'} and {out_dir / 'matrix.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
