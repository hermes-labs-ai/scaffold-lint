"""Graceful-degradation tests — required by hermes-seal continuity gate.

scaffold-lint has no external deps (no network, no LLM). Boundary input
failures (missing file, no args) must produce clean error messages on stderr
and a non-zero exit, never a stacktrace.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "scaffold_lint.cli", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_degrade_missing_file(tmp_path: Path):
    proc = _run(["lint", str(tmp_path / "does_not_exist.md")])
    assert proc.returncode == 1
    assert "file not found" in proc.stderr
    assert "Traceback" not in proc.stderr


def test_degrade_no_file_no_text():
    proc = _run(["lint"])
    assert proc.returncode == 1
    assert "file path or --text" in proc.stderr
    assert "Traceback" not in proc.stderr


def test_degrade_help_exits_cleanly():
    proc = _run([])
    # No subcommand → prints help, exits 0, no stacktrace
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr


def test_version_flag_works():
    proc = _run(["--version"])
    assert proc.returncode == 0
    assert "scaffold-lint" in proc.stdout
    assert "Traceback" not in proc.stderr


def test_rules_command_produces_output():
    proc = _run(["rules"])
    assert proc.returncode == 0
    assert "SCAFFOLD_TOO_LONG" in proc.stdout
    assert "Traceback" not in proc.stderr
