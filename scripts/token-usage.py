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
from collections import deque
from pathlib import Path


LABEL = r"[0-9][0-9A-Za-z.\-]*"
START = re.compile(rf"(?:^|&&|;)\s*(?:python3\s+)?\S*token-usage\.py\s+--start\s+({LABEL})(?=\s|$|;|&)", re.M)
CLAUDE_ROOT = Path.home() / ".claude" / "projects"
CODEX_ROOT = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"
AGY_DEFAULT_APP_DIRS = (
    Path.home() / ".gemini" / "antigravity-cli",
    Path.home() / ".gemini" / "antigravity",
    Path.home() / ".gemini" / "antigravity-ide",
)
AGY_CID_RE = re.compile(r"^[A-Za-z0-9-]+$")
AGY_SUBAGENT_RE = re.compile(
    r'^(?:(?:Created|Completed) At:[^\r\n]*\r?\n|[ \t]*\r?\n)*'
    r'Created the following subagent:\s*\{\s*"conversationId"\s*:\s*"([^"]+)"'
)
COMMON_LABELS = ("in", "out", "cache_r")
CLAUDE_KEYS = {
    "in": "input_tokens",
    "out": "output_tokens",
    "cache_r": "cache_read_input_tokens",
    "cache_w": "cache_creation_input_tokens",
}
CODEX_KEYS = {"in": "input_tokens", "out": "output_tokens", "cache_r": "cached_input_tokens"}
AGY_KEYS = {"in": "input_tokens", "out": "output_tokens", "cache_r": "cache_read_tokens"}


class Fail(Exception):
    """Aggregation failure with a short reason code (never transcript content)."""


def start_stage(command: str) -> str | None:
    found = START.findall(command)
    return found[-1] if found else None


def obj(value) -> dict:
    """Malformed transcript fields degrade to {} instead of raising."""
    return value if isinstance(value, dict) else {}


def num(value) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                yield row


def tool_commands(row: dict) -> list[str]:
    content = obj(row.get("message")).get("content")
    if not isinstance(content, list):
        return []
    return [str(obj(c.get("input")).get("command", "")) for c in map(obj, content) if c.get("type") == "tool_use"]


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
                stage, start = found, str(row.get("timestamp", ""))
    if stage is None:
        raise Fail("경계 없음")

    # Same message.id repeats per content block; the last non-zero usage wins.
    by_id: dict[str, dict] = {}
    for path in [main, *sorted((main.parent / session_id / "subagents").glob("*.jsonl"))]:
        for lineno, row in enumerate(read_jsonl(path)):
            if row.get("type") != "assistant" or str(row.get("timestamp", "")) < start:
                continue
            message = obj(row.get("message"))
            usage = obj(message.get("usage"))
            if not any(num(usage.get(key)) for key in CLAUDE_KEYS.values()):
                continue
            by_id[f"{path.name}:{message.get('id') or row.get('uuid') or lineno}"] = usage
    totals = {label: sum(num(u.get(key)) for u in by_id.values()) for label, key in CLAUDE_KEYS.items()}
    return stage, totals


def codex_session(root: Path, cwd: str, harness_root: Path) -> Path:
    """Main rollout under the harness root whose cwd contains the current cwd; newest first, deeper cwd breaks ties."""
    here = Path(os.path.realpath(cwd))
    top = Path(os.path.realpath(harness_root))
    candidates = []
    for mtime, path in sorted(((p.stat().st_mtime, p) for p in root.rglob("rollout-*.jsonl")), reverse=True):
        if candidates and mtime < candidates[0][0]:
            break
        first = next(read_jsonl(path), {})
        meta = obj(first.get("payload")) if first.get("type") == "session_meta" else {}
        if not isinstance(meta.get("cwd"), str) or not meta["cwd"]:
            continue
        source = meta.get("source")
        if isinstance(source, dict) and "subagent" in source:
            continue
        session_cwd = Path(os.path.realpath(meta["cwd"]))
        if session_cwd.is_relative_to(top) and here.is_relative_to(session_cwd):
            candidates.append((mtime, len(session_cwd.parts), path))
    if not candidates:
        raise Fail("세션 식별 불가")
    return max(candidates)[2]


def codex_usage(root: Path, cwd: str, harness_root: Path) -> tuple[str, dict[str, int]]:
    path = codex_session(root, cwd, harness_root)

    stage, base, total = None, {}, {}
    for row in read_jsonl(path):
        payload = obj(row.get("payload"))
        if row.get("type") == "event_msg" and payload.get("type") == "token_count":
            total = obj(obj(payload.get("info")).get("total_token_usage")) or total
        elif row.get("type") == "response_item" and payload.get("type") == "function_call":
            try:
                command = str(obj(json.loads(payload.get("arguments") or "{}")).get("cmd", ""))
            except (json.JSONDecodeError, TypeError):
                continue
            found = start_stage(command)
            if found:
                stage, base = found, total
    if stage is None:
        raise Fail("경계 없음")
    totals = {label: num(total.get(key)) - num(base.get(key)) for label, key in CODEX_KEYS.items()}
    return stage, totals


def agy_unwrap_command(raw) -> str:
    if not isinstance(raw, str):
        return ""
    try:
        decoded = json.loads(raw)
        if isinstance(decoded, str):
            return decoded
    except json.JSONDecodeError:
        pass
    return raw


def agy_row_commands(row: dict) -> list[str]:
    calls = row.get("tool_calls")
    if not isinstance(calls, list):
        return []
    commands: list[str] = []
    for call in map(obj, calls):
        if call.get("name") == "run_command":
            commands.append(agy_unwrap_command(obj(call.get("args")).get("CommandLine")))
    return commands


def agy_transcript_path(brain_dir: Path, cid: str) -> Path | None:
    if not isinstance(cid, str) or not AGY_CID_RE.fullmatch(cid):
        return None
    try:
        base = brain_dir.resolve()
        candidate = (base / cid / ".system_generated" / "logs" / "transcript.jsonl").resolve()
    except OSError:
        return None
    if not candidate.is_relative_to(base) or not candidate.is_file():
        return None
    return candidate


def agy_resolve_brain_dir(
    cid: str,
    env_dir: str = "",
    defaults: tuple[Path, ...] = AGY_DEFAULT_APP_DIRS,
) -> Path:
    if not isinstance(cid, str) or not AGY_CID_RE.fullmatch(cid):
        raise Fail("세션 식별 불가")
    candidates = (Path(env_dir),) if env_dir else defaults
    for app_dir in candidates:
        brain_dir = app_dir / "brain"
        if agy_transcript_path(brain_dir, cid) is not None:
            return brain_dir
    raise Fail("세션 식별 불가")


def agy_extract_subagents(row: dict) -> list[str]:
    if row.get("type") != "GENERIC":
        return []
    content = row.get("content")
    if not isinstance(content, str):
        return []
    match = AGY_SUBAGENT_RE.match(content)
    return [match.group(1)] if match else []


def agy_explicit_step(row: dict) -> int | None:
    val = row.get("step_index")
    return val if isinstance(val, int) and not isinstance(val, bool) else None


def _agy_row_in_stage(row: dict, idx: int, start_idx: int, start_step: int | None) -> bool:
    step = agy_explicit_step(row)
    if start_step is not None and step is not None:
        return step >= start_step
    return idx >= start_idx


def agy_usage(brain_dir: Path, cid: str) -> tuple[str, dict[str, int], bool]:
    main = agy_transcript_path(brain_dir, cid)
    if main is None:
        raise Fail("세션 식별 불가")

    try:
        rows = list(read_jsonl(main))
    except (OSError, UnicodeDecodeError) as exc:
        raise Fail("세션 식별 불가") from exc

    stage: str | None = None
    start_idx = -1
    start_step: int | None = None
    for idx, row in enumerate(rows):
        if row.get("type") != "PLANNER_RESPONSE":
            continue
        for command in agy_row_commands(row):
            found = start_stage(command)
            if found:
                stage, start_idx, start_step = found, idx, agy_explicit_step(row)
    if stage is None:
        raise Fail("경계 없음")

    main_totals = {label: 0 for label in AGY_KEYS}
    queue: deque[str] = deque()
    for idx, row in enumerate(rows):
        if not _agy_row_in_stage(row, idx, start_idx, start_step):
            continue
        if row.get("type") == "PLANNER_RESPONSE":
            for label, key in AGY_KEYS.items():
                main_totals[label] += num(row.get(key))
        else:
            queue.extend(agy_extract_subagents(row))

    children_totals = {label: 0 for label in AGY_KEYS}
    visited: set[str] = {cid}
    missing_child = False
    while queue:
        child_cid = queue.popleft()
        if not AGY_CID_RE.fullmatch(child_cid):
            continue
        if child_cid in visited:
            continue
        visited.add(child_cid)
        child_path = agy_transcript_path(brain_dir, child_cid)
        if child_path is None:
            missing_child = True
            break
        child_totals = {label: 0 for label in AGY_KEYS}
        child_subs: list[str] = []
        try:
            for row in read_jsonl(child_path):
                if row.get("type") == "PLANNER_RESPONSE":
                    for label, key in AGY_KEYS.items():
                        child_totals[label] += num(row.get(key))
                else:
                    child_subs.extend(agy_extract_subagents(row))
        except (OSError, UnicodeDecodeError):
            missing_child = True
            break
        for label in AGY_KEYS:
            children_totals[label] += child_totals[label]
        queue.extend(child_subs)

    if missing_child:
        return stage, main_totals, True
    combined = {label: main_totals[label] + children_totals[label] for label in AGY_KEYS}
    return stage, combined, False


def format_line(
    stage: str,
    totals: dict[str, int],
    *,
    cache_w_na: bool,
    main_only: bool,
) -> str:
    parts = [f"{label} {totals[label]:,}" for label in COMMON_LABELS]
    parts.append("cache_w n/a" if cache_w_na else f"cache_w {totals['cache_w']:,}")
    return f"토큰 [{stage}]: {' · '.join(parts)}" + (" (메인만)" if main_only else "")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def _self_test_antigravity(tmp: Path) -> None:
    brain = tmp / "agy" / "brain"
    planner = lambda step, i, o, c, cmd="", raw_cmd=False: {
        **({"step_index": step} if step is not None else {}),
        "type": "PLANNER_RESPONSE",
        "input_tokens": i,
        "output_tokens": o,
        "cache_read_tokens": c,
        "tool_calls": [{"name": "run_command", "args": {"CommandLine": cmd if raw_cmd else json.dumps(cmd)}}] if cmd else [],
    }
    sub_out = lambda step, sub_id, header="": {
        "step_index": step,
        "type": "GENERIC",
        "content": f'{header}Created the following subagent:\n{{\n  "conversationId":  "{sub_id}"\n}}',
    }
    real_header = (
        "Created At: 2026-11-26T09:08:43+09:00\r\n"
        "Completed At: 2026-11-26T09:08:51+09:00\n"
        "\n"
    )
    main_path = brain / "main-1" / ".system_generated" / "logs" / "transcript.jsonl"
    write_jsonl(main_path, [
        planner(1, 500, 50, 100, "python3 scripts/token-usage.py --start 3"),
        sub_out(2, "old-child"),
        planner(50, 100, 10, 20, "python3 scripts/token-usage.py --start 8"),
        sub_out(51, "child-a", header=real_header),
        sub_out(52, "child-a"),
        sub_out(53, "../../etc/passwd"),
        sub_out(54, "main-1"),
        planner(None, 200, 30, 40),  # missing step_index after start_idx must still be included
        {"step_index": 56, "type": "PLANNER_RESPONSE", "tool_calls": [{"name": "run_command", "args": {"CommandLine": 123}}]},
        {"step_index": 57, "type": "GENERIC", "content": '"conversationId": "not-a-subagent"'},
        # Non-subagent tool outputs containing subagent text must NOT match
        {
            "step_index": 58,
            "type": "GENERIC",
            "content": (
                "Created At: 2026-11-26T09:10:00+09:00\n"
                "Completed At: 2026-11-26T09:10:01+09:00\n"
                "Command exited with code 0.\n\nCommand output:\n"
                'Created the following subagent:\n{\n  "conversationId": "old-child"\n}'
            ),
        },
        {
            "step_index": 59,
            "type": "GENERIC",
            "content": (
                "Created At: 2026-11-26T09:10:02+09:00\n"
                "Showing lines 1-10 of 10\n"
                '1: Created the following subagent:\n{\n  "conversationId": "missing-fake"\n}'
            ),
        },
    ])
    # Append malformed JSON line to ensure safe skipping
    with main_path.open("a", encoding="utf-8") as fh:
        fh.write("{corrupt-json\n")
    write_jsonl(brain / "old-child" / ".system_generated" / "logs" / "transcript.jsonl", [
        planner(1, 9999, 999, 999),
    ])
    write_jsonl(brain / "child-a" / ".system_generated" / "logs" / "transcript.jsonl", [
        planner(1, 50, 5, 10),
        sub_out(2, "child-b"),
    ])
    write_jsonl(brain / "child-b" / ".system_generated" / "logs" / "transcript.jsonl", [
        planner(1, 25, 3, 4),
    ])
    stage, totals, main_only = agy_usage(brain, "main-1")
    assert (stage, totals, main_only) == ("8", {"in": 375, "out": 48, "cache_r": 74}, False), (stage, totals, main_only)
    assert format_line(stage, totals, cache_w_na=True, main_only=main_only) == (
        "토큰 [8]: in 375 · out 48 · cache_r 74 · cache_w n/a"
    )

    # Single-encoded plain CommandLine + valid child + missing child -> main_totals only (no mixed child tokens)
    write_jsonl(brain / "main-2" / ".system_generated" / "logs" / "transcript.jsonl", [
        planner(1, 10, 2, 3, "python3 scripts/token-usage.py --start 9", raw_cmd=True),
        sub_out(2, "child-a"),
        sub_out(3, "missing-child"),
    ])
    stage2, totals2, main_only2 = agy_usage(brain, "main-2")
    assert (stage2, totals2, main_only2) == ("9", {"in": 10, "out": 2, "cache_r": 3}, True), (stage2, totals2, main_only2)
    assert format_line(stage2, totals2, cache_w_na=True, main_only=main_only2) == (
        "토큰 [9]: in 10 · out 2 · cache_r 3 · cache_w n/a (메인만)"
    )

    # Partial UTF-8 corrupt child (valid line followed by corrupt bytes) + prior valid child -> main_totals only
    write_jsonl(brain / "main-3" / ".system_generated" / "logs" / "transcript.jsonl", [
        planner(1, 12, 4, 6, "python3 scripts/token-usage.py --start 4"),
        sub_out(2, "child-a"),
        sub_out(3, "bad-utf8-child"),
    ])
    bad_child = brain / "bad-utf8-child" / ".system_generated" / "logs" / "transcript.jsonl"
    bad_child.parent.mkdir(parents=True, exist_ok=True)
    bad_child.write_bytes((json.dumps(planner(1, 777, 77, 77)) + "\n").encode("utf-8") + b"\xff\xfe\x00invalid-utf8\n")
    assert agy_usage(brain, "main-3") == ("4", {"in": 12, "out": 4, "cache_r": 6}, True)

    # Early break on missing_child skips reading subsequent sibling transcripts
    write_jsonl(brain / "main-early" / ".system_generated" / "logs" / "transcript.jsonl", [
        planner(1, 7, 1, 2, "python3 scripts/token-usage.py --start 6"),
        sub_out(2, "missing-first"),
        sub_out(3, "child-b"),
    ])
    real_reader, seen_children = read_jsonl, []
    globals()["read_jsonl"] = lambda path: seen_children.append(path.parent.parent.parent.name) or real_reader(path)
    try:
        assert agy_usage(brain, "main-early") == ("6", {"in": 7, "out": 1, "cache_r": 2}, True)
    finally:
        globals()["read_jsonl"] = real_reader
    assert seen_children == ["main-early"], seen_children

    # Missing boundary -> Fail("경계 없음")
    write_jsonl(brain / "main-nobound" / ".system_generated" / "logs" / "transcript.jsonl", [
        planner(1, 10, 2, 3),
    ])
    try:
        agy_usage(brain, "main-nobound")
        raise AssertionError("missing boundary should fail")
    except Fail as exc:
        assert str(exc) == "경계 없음", str(exc)

    # Corrupt UTF-8 main transcript -> Fail("세션 식별 불가")
    bad_main = brain / "main-badutf8" / ".system_generated" / "logs" / "transcript.jsonl"
    bad_main.parent.mkdir(parents=True, exist_ok=True)
    bad_main.write_bytes(b"\xff\xfe\n")
    try:
        agy_usage(brain, "main-badutf8")
        raise AssertionError("bad utf8 main should fail")
    except Fail as exc:
        assert str(exc) == "세션 식별 불가", str(exc)

    # ReDoS regression guard: many leading blank lines must fail fast without backtracking
    assert AGY_SUBAGENT_RE.match("\n" * 200 + "a" * 60) is None
    assert AGY_SUBAGENT_RE.match(" \t\r\n" * 200 + "a" * 60) is None

    # App data dir fallback order + runtime auto-detection priority
    assert agy_resolve_brain_dir("main-1", defaults=(tmp / "none", tmp / "agy")) == brain
    for bad_cid in ("", "../escape", "unknown-id"):
        try:
            agy_resolve_brain_dir(bad_cid, defaults=(tmp / "agy",))
            raise AssertionError(f"bad cid should fail: {bad_cid}")
        except Fail:
            pass
    assert detect_runtime("auto", "c1", "a1") == "claude"
    assert detect_runtime("auto", "", "a1") == "antigravity"
    assert detect_runtime("auto", "", "") == "codex"
    assert detect_runtime("antigravity", "c1", "") == "antigravity"


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
            [1, 2],
            {"type": "assistant", "timestamp": "T06", "message": "x"},
            {"type": "assistant", "timestamp": "T06", "uuid": "u3", "message": {"usage": {"output_tokens": "9", "input_tokens": True}}},
            {"type": "assistant", "timestamp": "T06", "message": {"content": ["x", {"type": "tool_use", "input": "x"}], "usage": "x"}},
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
            "not-a-dict",
            {"type": "event_msg", "payload": "not-a-dict"},
            {"type": "event_msg", "payload": {"type": "token_count", "info": "x"}},
            {"type": "response_item", "payload": {"type": "function_call", "arguments": "[1]"}},
            {"type": "response_item", "payload": {"type": "function_call", "arguments": 5}},
            tc(160, 25, 80),
        ])
        meta = lambda cwd, source="cli": {"type": "session_meta", "payload": {"cwd": cwd, "source": source}}
        write_jsonl(croot / "2026" / "rollout-child.jsonl", [meta("/w", {"subagent": "review"})])
        write_jsonl(croot / "2026" / "rollout-wx.jsonl", [meta("/wx")])
        write_jsonl(croot / "2026" / "rollout-root.jsonl", [meta("/")])
        write_jsonl(croot / "2026" / "rollout-sub.jsonl", [meta("/w/sub")])
        write_jsonl(croot / "2026" / "rollout-old.jsonl", [meta("/w")])
        write_jsonl(croot / "2026" / "rollout-bad1.jsonl", [[1, 2]])
        write_jsonl(croot / "2026" / "rollout-bad2.jsonl", [meta(123)])
        write_jsonl(croot / "2026" / "rollout-bad3.jsonl", [{"type": "session_meta", "payload": "x"}])
        ages = {"old": 100, "x": 20, "sub": 20, "wx": 10, "root": 5, "bad1": 3, "bad2": 2, "bad3": 1, "child": 0}
        for name, age in ages.items():
            ts = 1_700_000_000 - age
            os.utime(croot / "2026" / f"rollout-{name}.jsonl", (ts, ts))
        home = Path("/w")
        stage, totals = codex_usage(croot, "/w", home)  # newer root("/")·child·wx skipped
        assert (stage, totals) == ("5", {"in": 60, "out": 15, "cache_r": 30}), (stage, totals)
        assert codex_session(croot, "/w/sub/repo", home).name == "rollout-sub.jsonl"  # same mtime: deeper wins
        os.utime(croot / "2026" / "rollout-x.jsonl", (1_700_000_001, 1_700_000_001))
        assert codex_session(croot, "/w/sub/repo", home).name == "rollout-x.jsonl"  # newest wins over deeper
        eroot = Path(tmp) / "early"
        write_jsonl(eroot / "rollout-new.jsonl", [meta("/w")])
        write_jsonl(eroot / "rollout-older.jsonl", [meta("/w")])
        os.utime(eroot / "rollout-older.jsonl", (1_600_000_000, 1_600_000_000))
        real, seen = read_jsonl, []
        globals()["read_jsonl"] = lambda path: seen.append(path.name) or real(path)
        try:
            assert codex_session(eroot, "/w", home).name == "rollout-new.jsonl"
        finally:
            globals()["read_jsonl"] = real
        assert seen == ["rollout-new.jsonl"], seen  # older file never parsed: early exit
        assert re.fullmatch(LABEL, "9") and not re.fullmatch(LABEL, "9-코드")
        assert not START.findall("python3 scripts/token-usage.py --start 9-코드")
        assert format_line(stage, totals, cache_w_na=True, main_only=True) == (
            "토큰 [5]: in 60 · out 15 · cache_r 30 · cache_w n/a (메인만)"
        )

        for fn, args in (
            (claude_usage, (root, "none")),
            (codex_usage, (croot, "/elsewhere", home)),
            (codex_usage, (croot, "/", home)),
        ):
            try:
                fn(*args)
                raise AssertionError(f"{fn.__name__} should fail")
            except Fail:
                pass

        _self_test_antigravity(Path(tmp))
    print("self-test OK")


def detect_runtime(requested: str, claude_sid: str, agy_cid: str) -> str:
    if requested != "auto":
        return requested
    if claude_sid:
        return "claude"
    if agy_cid:
        return "antigravity"
    return "codex"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", choices=["auto", "claude", "codex", "antigravity"], default="auto")
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

    claude_sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    agy_cid = os.environ.get("ANTIGRAVITY_CONVERSATION_ID", "")
    runtime = detect_runtime(args.runtime, claude_sid, agy_cid)
    try:
        if runtime == "claude":
            if not claude_sid:
                raise Fail("세션 식별 불가")
            stage, totals = claude_usage(CLAUDE_ROOT, claude_sid)
            cache_w_na, main_only = False, False
        elif runtime == "antigravity":
            brain_dir = agy_resolve_brain_dir(agy_cid, os.environ.get("ANTIGRAVITY_APP_DATA_DIR", ""))
            stage, totals, main_only = agy_usage(brain_dir, agy_cid)
            cache_w_na = True
        else:
            stage, totals = codex_usage(CODEX_ROOT, os.getcwd(), Path(__file__).resolve().parents[1])
            cache_w_na, main_only = True, True
    except Fail as exc:
        print(f"토큰: 집계 실패 — {exc}")
        return 1
    print(format_line(stage, totals, cache_w_na=cache_w_na, main_only=main_only))
    return 0


if __name__ == "__main__":
    sys.exit(main())
