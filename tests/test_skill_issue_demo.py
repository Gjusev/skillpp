"""Offline test: the skill-issue experiment generator produces valid specs."""

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec_ = importlib.util.spec_from_file_location(
    "skill_issue_demo", REPO / "scripts" / "skill_issue_demo.py")
demo = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(demo)


def test_generates_valid_experiment_pair(tmp_path, monkeypatch):
    for var in ("SKILLPP_BASE_URL", "SKILLPP_MODEL", "SKILLPP_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    rc = demo.main(["demo", "--refine", "scripted", "--out", str(tmp_path)])
    assert rc == 0

    for variant in ("draft", "refined"):
        s = json.loads((tmp_path / "tasks" / f"routing-{variant}.json").read_text(encoding="utf-8"))
        assert s["specVersion"] == 1 and s["id"] == f"routing-{variant}"
        assert s["agent"]["runner"] == "claude-code"
        for key in ("workspaceCopyFrom", ):
            assert (tmp_path / "tasks" / s["task"][key]).resolve().is_dir()
        assert (tmp_path / "tasks" / s["skill"]["path"]).resolve().is_dir()
        assert (tmp_path / "tasks" / s["verifier"]["copyFrom"] / "verify.mjs").is_file()

    # the two variants differ ONLY in B's description
    draft = (tmp_path / "skills" / "sql-explainer-draft" / "SKILL.md").read_text(encoding="utf-8")
    refined = (tmp_path / "skills" / "sql-explainer-refined" / "SKILL.md").read_text(encoding="utf-8")
    assert demo.DRAFT_B in draft                # draft = the sloppy truthful text
    assert demo.DRAFT_B not in refined          # refined actually differs
    # bodies identical: everything after frontmatter
    assert draft.split("---", 2)[2] == refined.split("---", 2)[2]

    # workspace template has A pre-installed and the query to explain
    ws = tmp_path / "workspaces" / "base"
    assert (ws / ".claude" / "skills" / "sql-optimizer" / "SKILL.md").is_file()
    assert "RANK() OVER" in (ws / "query.sql").read_text(encoding="utf-8")
