#!/usr/bin/env python3
"""Antigravity PostToolUse hook: sync rp-* skills when docs/skills/rp-*.md changes.

Fast-path standard-library script. Always prints `{}` and exits 0 (fail-open).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


SKILL_NAME_RE = re.compile(r"^rp-[a-z0-9-]+\.md$")
SUBPROCESS_TIMEOUT = 8


def extract_target_path(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    tool_call = payload.get("toolCall")
    if not isinstance(tool_call, dict):
        return None
    args = tool_call.get("args")
    if not isinstance(args, dict):
        return None
    for key in ("Path", "TargetFile", "file_path"):
        val = args.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def is_harness_skill_file(file_path: str, harness_root: Path, cwd: str | None) -> bool:
    p = Path(file_path)
    if not p.is_absolute():
        p = (Path(cwd) if cwd else harness_root) / p
    try:
        resolved = p.resolve()
        expected_dir = (harness_root / "docs" / "skills").resolve()
    except OSError:
        return False
    return resolved.parent == expected_dir and bool(SKILL_NAME_RE.fullmatch(resolved.name))


def should_sync(payload: object, harness_root: Path) -> bool:
    if not isinstance(payload, dict) or payload.get("error"):
        return False
    file_path = extract_target_path(payload)
    if not file_path:
        return False
    cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else None
    return is_harness_skill_file(file_path, harness_root, cwd)


def self_test() -> None:
    harness_root = Path(__file__).resolve().parents[2]
    ok_cases = [
        {"toolCall": {"name": "write_file", "args": {"Path": str(harness_root / "docs/skills/rp-qa.md")}}},
        {"cwd": str(harness_root), "toolCall": {"name": "edit_file", "args": {"Path": "docs/skills/rp-qa.md"}}},
        {"toolCall": {"name": "edit_file", "args": {"Path": "docs/skills/rp-qa.md"}}},  # missing cwd -> harness_root
        {"toolCall": {"name": "write_to_file", "args": {"TargetFile": str(harness_root / "docs/skills/rp-qa.md")}}},
        {"toolCall": {"name": "write_file", "args": {"file_path": str(harness_root / "docs/skills/rp-qa.md")}}},
    ]
    for case in ok_cases:
        assert should_sync(case, harness_root), case

    skip_cases = [
        {"error": "exit status 1", "toolCall": {"name": "write_file", "args": {"Path": str(harness_root / "docs/skills/rp-qa.md")}}},
        {"toolCall": {"name": "write_file", "args": {"Path": str(harness_root / "repositories/demo/docs/skills/rp-x.md")}}},
        {"toolCall": {"name": "write_file", "args": {"Path": "../../etc/passwd"}}},
        {"toolCall": {"name": "write_file", "args": {"Path": str(harness_root / "docs/skills/other.md")}}},
        {"toolCall": {"name": "write_file", "args": {"Path": str(harness_root / "README.md")}}},
        {},
        "not-a-dict",
    ]
    for case in skip_cases:
        assert not should_sync(case, harness_root), case

    # Verify fail-open JSON output on malformed stdin from cwd=.agents/
    proc = subprocess.run(
        [sys.executable, "./hooks/sync-rp-skills.py"],
        cwd=str(harness_root / ".agents"),
        input="{malformed-json",
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(proc.stdout) == {}, proc.stdout
    print("self-test OK")


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        return 0

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError):
        print("{}")
        return 0

    harness_root = Path(__file__).resolve().parents[2]
    if not should_sync(payload, harness_root):
        print("{}")
        return 0

    sync_script = harness_root / "scripts" / "sync-skills.py"
    if sync_script.is_file():
        try:
            subprocess.run(
                [sys.executable, str(sync_script), "--target", "all", "--sync-claude-links"],
                cwd=str(harness_root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=SUBPROCESS_TIMEOUT,
                check=False,
                shell=False,
            )
        except (OSError, subprocess.SubprocessError):
            pass

    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
