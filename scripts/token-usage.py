#!/usr/bin/env python3
"""Print token usage since the last `token-usage.py --start N` call of the current session.

The boundary is a tool call, not assistant text: transcripts do not persist every text block.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path


LABEL = r"[0-9][0-9A-Za-z.\-]*"
START = re.compile(rf"(?:^|&&|;)\s*(?:python3\s+)?\S*token-usage\.py\s+--start\s+({LABEL})(?=\s|$|;|&)", re.M)
CLAUDE_ROOT = Path.home() / ".claude" / "projects"
CODEX_ROOT = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"
CLAUDE_KEYS = {
    "in": "input_tokens",
    "out": "output_tokens",
    "cache_r": "cache_read_input_tokens",
    "cache_w": "cache_creation_input_tokens",
}
CODEX_KEYS = {"in": "input_tokens", "out": "output_tokens", "cache_r": "cached_input_tokens"}


class Fail(Exception):
    """Aggregation failure with a short reason code (never transcript content)."""


def start_stage(command: str) -> str | None:
    found = START.findall(command)
    return found[-1] if found else None


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def tool_commands(row: dict) -> list[str]:
    content = row.get("message", {}).get("content")
    if not isinstance(content, list):
        return []
    return [str((c.get("input") or {}).get("command", "")) for c in content if c.get("type") == "tool_use"]


def claude_usage(root: Path, session_id: str) -> tuple[str, dict[str, int]]:
    mains = list(root.glob(f"*/{session_id}.jsonl"))
    if len(mains) != 1:
        raise Fail("세션 식별 불가")
    main = mains[0]
    stage = start = None
    for row in read_jsonl(main):
        if row.get("type") != "assistant":
            continue
        for command in tool_commands(row):
            found = start_stage(command)
            if found:
                stage, start = found, row.get("timestamp", "")
    if stage is None:
        raise Fail("경계 없음")

    # Same message.id repeats per content block; the last non-zero usage wins.
    by_id: dict[str, dict] = {}
    for path in [main, *sorted((main.parent / session_id / "subagents").glob("*.jsonl"))]:
        for lineno, row in enumerate(read_jsonl(path)):
            if row.get("type") != "assistant" or row.get("timestamp", "") < start:
                continue
            message = row.get("message", {})
            usage = message.get("usage") or {}
            if not any(usage.get(key) for key in CLAUDE_KEYS.values()):
                continue
            by_id[f"{path.name}:{message.get('id') or row.get('uuid') or lineno}"] = usage
    totals = {label: sum(u.get(key, 0) for u in by_id.values()) for label, key in CLAUDE_KEYS.items()}
    return stage, totals


def codex_session(root: Path, cwd: str) -> Path:
    """Main rollout whose cwd contains the current cwd; newest first, deeper cwd breaks ties."""
    here = Path(os.path.realpath(cwd))
    candidates = []
    for path in root.rglob("rollout-*.jsonl"):
        first = next(read_jsonl(path), {})
        meta = first.get("payload", {}) if first.get("type") == "session_meta" else {}
        source = meta.get("source")
        if not meta.get("cwd") or (isinstance(source, dict) and "subagent" in source):
            continue
        session_cwd = Path(os.path.realpath(meta["cwd"]))
        if here.is_relative_to(session_cwd):
            candidates.append((path.stat().st_mtime, len(session_cwd.parts), path))
    if not candidates:
        raise Fail("세션 식별 불가")
    return max(candidates)[2]


def codex_usage(root: Path, cwd: str) -> tuple[str, dict[str, int]]:
    path = codex_session(root, cwd)

    stage, base, total = None, {}, {}
    for row in read_jsonl(path):
        payload = row.get("payload", {})
        if row.get("type") == "event_msg" and payload.get("type") == "token_count":
            total = (payload.get("info") or {}).get("total_token_usage") or total
        elif row.get("type") == "response_item" and payload.get("type") == "function_call":
            try:
                command = str(json.loads(payload.get("arguments") or "{}").get("cmd", ""))
            except json.JSONDecodeError:
                continue
            found = start_stage(command)
            if found:
                stage, base = found, total
    if stage is None:
        raise Fail("경계 없음")
    totals = {label: total.get(key, 0) - base.get(key, 0) for label, key in CODEX_KEYS.items()}
    return stage, totals


def format_line(stage: str, totals: dict[str, int], codex: bool) -> str:
    parts = [f"{label} {totals[label]:,}" for label in CODEX_KEYS]
    parts.append("cache_w n/a" if codex else f"cache_w {totals['cache_w']:,}")
    return f"토큰 [{stage}]: {' · '.join(parts)}" + (" (메인만)" if codex else "")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def self_test() -> None:
    def asst(ts: str, mid: str, command: str = "", **usage: int) -> dict:
        content = [{"type": "tool_use", "input": {"command": command}}] if command else []
        return {"type": "assistant", "timestamp": ts, "message": {"id": mid, "content": content, "usage": usage}}

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "claude"
        write_jsonl(root / "proj" / "sid.jsonl", [
            {"type": "user", "timestamp": "T05", "message": {"content": "python3 scripts/token-usage.py --start 9"}},
            {"type": "assistant", "timestamp": "T06", "uuid": "u1", "message": {"content": [], "usage": {"output_tokens": 4}}},
            {"type": "assistant", "timestamp": "T06", "uuid": "u2", "message": {"content": [], "usage": {"output_tokens": 6}}},
            {"type": "assistant", "timestamp": "T06", "message": {"content": [], "usage": {"output_tokens": 1}}},
            {"type": "assistant", "timestamp": "T06", "message": {"content": [], "usage": {"output_tokens": 1}}},
            asst("T01", "m0", "python3 scripts/token-usage.py --start 3", input_tokens=100, output_tokens=100),
            asst("T02", "m1", "make && python3 scripts/token-usage.py --start 4b", input_tokens=0, output_tokens=0),
            asst("T02", "m1", "", input_tokens=10, output_tokens=5, cache_read_input_tokens=7),
            asst("T02", "m1", "", input_tokens=10, output_tokens=5, cache_read_input_tokens=7),
            asst("T03", "m2", 'grep "token-usage.py --start 9" x', input_tokens=1, cache_creation_input_tokens=3),
            asst("T03", "m4", 'x = "a && python3 token-usage.py --start 9", b'),
        ])
        write_jsonl(root / "proj" / "sid" / "subagents" / "agent-a.jsonl", [
            asst("T01", "s0", input_tokens=500),
            asst("T04", "s1", input_tokens=20, output_tokens=2),
        ])
        stage, totals = claude_usage(root, "sid")
        assert stage == "4b", stage
        assert totals == {"in": 31, "out": 19, "cache_r": 7, "cache_w": 3}, totals

        croot = Path(tmp) / "codex"
        tc = lambda i, o, c: {"type": "event_msg", "payload": {"type": "token_count", "info": {
            "total_token_usage": {"input_tokens": i, "output_tokens": o, "cached_input_tokens": c}}}}
        write_jsonl(croot / "2026" / "rollout-x.jsonl", [
            {"type": "session_meta", "payload": {"cwd": "/w"}},
            tc(100, 10, 50),
            {"type": "response_item", "payload": {"type": "function_call",
                "arguments": json.dumps({"cmd": "python3 scripts/token-usage.py --start 5"})}},
            tc(160, 25, 80),
        ])
        meta = lambda cwd, source="cli": {"type": "session_meta", "payload": {"cwd": cwd, "source": source}}
        write_jsonl(croot / "2026" / "rollout-child.jsonl", [meta("/w", {"subagent": "review"})])
        write_jsonl(croot / "2026" / "rollout-wx.jsonl", [meta("/wx")])
        write_jsonl(croot / "2026" / "rollout-root.jsonl", [meta("/")])
        for name, age in (("root", 30), ("x", 20), ("wx", 10), ("child", 0)):
            ts = 1_700_000_000 - age
            os.utime(croot / "2026" / f"rollout-{name}.jsonl", (ts, ts))
        stage, totals = codex_usage(croot, "/w")
        assert (stage, totals) == ("5", {"in": 60, "out": 15, "cache_r": 30}), (stage, totals)
        assert codex_session(croot, "/w/sub/repo").name == "rollout-x.jsonl"
        assert codex_session(croot, "/elsewhere").name == "rollout-root.jsonl"
        os.utime(croot / "2026" / "rollout-root.jsonl", (1_700_000_100, 1_700_000_100))
        assert codex_session(croot, "/w").name == "rollout-root.jsonl"  # newest wins over deeper cwd
        assert re.fullmatch(LABEL, "9") and not re.fullmatch(LABEL, "9-코드")
        assert not START.findall("python3 scripts/token-usage.py --start 9-코드")
        assert format_line(stage, totals, True) == "토큰 [5]: in 60 · out 15 · cache_r 30 · cache_w n/a (메인만)"

        for fn, args in ((claude_usage, (root, "none")), (codex_usage, (Path(tmp) / "empty", "/w"))):
            try:
                fn(*args)
                raise AssertionError(f"{fn.__name__} should fail")
            except Fail:
                pass
    print("self-test OK")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", choices=["auto", "claude", "codex"], default="auto")
    parser.add_argument("--start", metavar="N", help="mark the stage boundary (the call itself is the marker)")
    parser.add_argument("--self-test", action="store_true", help="run built-in fixture checks")
    args = parser.parse_args()
    if args.start:
        if not re.fullmatch(LABEL, args.start):
            print("토큰: 집계 실패 — 라벨 형식")
            return 1
        print(f"▶ [{args.start}] 토큰 경계")
        return 0
    if args.self_test:
        self_test()
        return 0

    session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    runtime = args.runtime if args.runtime != "auto" else ("claude" if session_id else "codex")
    try:
        if runtime == "claude":
            if not session_id:
                raise Fail("세션 식별 불가")
            stage, totals = claude_usage(CLAUDE_ROOT, session_id)
        else:
            stage, totals = codex_usage(CODEX_ROOT, os.getcwd())
    except Fail as exc:
        print(f"토큰: 집계 실패 — {exc}")
        return 1
    print(format_line(stage, totals, runtime == "codex"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
