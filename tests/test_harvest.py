"""Offline test for scripts/harvest_real.py: frontmatter parsing + pair picking."""

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("harvest_real", REPO / "scripts" / "harvest_real.py")
harvest_real = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harvest_real)


def test_harvest_reads_frontmatter_and_picks_similar_pair(tmp_path):
    for name, desc in [
        ("alpha", "Parses nginx logs into json records with timestamps."),
        ("beta", "Parses nginx logs into csv records with timestamps."),
        ("gamma", "Resizes images in bulk to target dimensions and formats."),
    ]:
        d = tmp_path / name
        d.mkdir()
        (d / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {desc}\n---\n\n# body\n", encoding="utf-8"
        )
    skills = harvest_real.harvest([tmp_path])
    assert {s["name"] for s in skills} == {"alpha", "beta", "gamma"}

    (a, b, sim) = harvest_real.top_pairs(skills, 1)[0]
    assert {a["name"], b["name"]} == {"alpha", "beta"}
    assert sim > 0.5
