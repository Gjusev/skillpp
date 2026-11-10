"""Offline test for scripts/run_matrix.py: a dead backend must not kill the run."""

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_matrix", REPO / "scripts" / "run_matrix.py")
run_matrix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_matrix)


def test_dead_backend_recorded_not_fatal(tmp_path, monkeypatch):
    # scrub real-run env so empty base_url can't fall back to a live endpoint
    for var in ("SKILLPP_BASE_URL", "SKILLPP_MODEL", "SKILLPP_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"backends": [
        {"name": "instant-error", "base_url": "", "model": "x"},          # ValueError at once
        {"name": "dead-port", "base_url": "http://127.0.0.1:1/v1", "model": "x"},  # connection refused
    ]}))
    out = tmp_path / "results"
    rc = run_matrix.main(["run_matrix.py", str(cfg), str(out)])
    assert rc == 0
    rows = json.loads((out / "matrix.json").read_text(encoding="utf-8"))
    assert len(rows) == 2
    assert all("error" in r for r in rows)
    md = (out / "matrix.md").read_text(encoding="utf-8")
    assert "error" in md and "ValueError" in md
