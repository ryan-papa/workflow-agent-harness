#!/usr/bin/env python3
"""Compatibility wrapper delegating Codex skill sync to scripts/sync-skills.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_sync_skills():
    script_path = Path(__file__).resolve().parent / "sync-skills.py"
    spec = importlib.util.spec_from_file_location("sync_skills", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    sync_skills = _load_sync_skills()
    forwarded = list(sys.argv[1:] if argv is None else argv)
    return sync_skills.main(["--target", "codex", *forwarded])


if __name__ == "__main__":
    raise SystemExit(main())
