#!/usr/bin/env python3
"""Generate project-local Codex skills from harness rp skill docs."""

from __future__ import annotations

import argparse
import os
import json
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "skills"
DEST_DIR = ROOT / ".codex" / "skills"
USER_SKILLS_DIR = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills"


def split_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path} missing YAML frontmatter")

    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path} missing closing YAML frontmatter")

    raw_meta = text[4:end].splitlines()
    body = text[end + len("\n---\n") :]
    meta: dict[str, str] = {}

    for line in raw_meta:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if (value.startswith("'") and value.endswith("'")) or (
            value.startswith('"') and value.endswith('"')
        ):
            value = value[1:-1]
        meta[key.strip()] = value

    return meta, body


def codex_description(name: str, original: str) -> str:
    original = original.replace(" + Codex /codex:review 1회. AND 진행", " 독립 리뷰")
    original = original.replace(" + Codex /codex:review 1회", " 독립 리뷰")
    original = original.replace("Codex /codex:review 1회", "Codex-led 독립 리뷰")
    original = original.replace("Claude 7항목 + Codex 1회", "Codex-led 7항목 독립 리뷰")
    original = original.replace("Claude 5항목", "Codex-led 5항목")
    original = original.replace("Claude 9항목", "Codex-led 9항목")
    suffix = (
        f" Use when Codex should run or follow the harness {name} stage, "
        f"or when the user invokes /{name}, ${name}, or asks for this workflow step."
    )
    return f"{original.rstrip('.')}.{suffix}"


def adapt_body_for_codex(body: str) -> str:
    replacements = {
        "`/codex:review --wait --base main`": "`Codex-led findings-first code review against main`",
        "`/codex:review --wait`": "`Codex-led findings-first review`",
        "/codex:review --wait --base main": "Codex-led findings-first code review against main",
        "/codex:review --wait": "Codex-led findings-first review",
        "Agent 툴의 서브에이전트": "`spawn_agent` 서브에이전트",
        "`subagent_type=general-purpose`": "`agent_type=explorer` 또는 `worker`",
        "Claude 채점만 수행. Codex 실행·저장 금지": "Codex-led 독립 채점만 수행. Claude 전용 명령 실행·저장 금지",
        "Claude 채점만. Codex 실행·저장 금지": "Codex-led 독립 채점만 수행. Claude 전용 명령 실행·저장 금지",
        "Claude 리뷰는": "Codex-led 리뷰는",
        "Claude 코드 리뷰는": "Codex-led 코드 리뷰는",
        "Claude 기획 리뷰는": "Codex-led 기획 리뷰는",
        "Claude 엔지 리뷰는": "Codex-led 엔지 리뷰는",
        "Claude 통과 + Codex High/Critical 반영 완료": "Codex-led 리뷰 통과 + High/Critical 반영 완료",
        "Claude 통과 후": "Codex-led 리뷰 통과 후",
        "Claude 통과": "Codex-led 리뷰 통과",
        "Claude 통과 후 Codex 추가 리뷰": "Codex-led 추가 리뷰",
        "Claude 코드 리뷰 통과 후 수행": "Codex-led 코드 리뷰로 수행",
        "Claude 3회 실패": "Codex-led 리뷰 3회 실패",
        "Claude + Codex 1회": "Codex-led 독립 리뷰",
        "Claude 7항목 + Codex 1회": "Codex-led 7항목 독립 리뷰",
        "review-claude-plan-r{N}.md": "review-codex-plan.md",
        "review-claude-eng-r{N}.md": "review-codex-eng.md",
        "review-claude-code-r{N}.md": "review-codex-code.md",
        "review-claude-meta-r{N}.md": "review-codex-meta.md",
        "review-claude-*-r*.md": "review-codex-*.md",
        "review-claude-${stage}-r*.md": "review-codex-${stage}.md",
        "review-claude-meta-r*.md": "review-codex-meta.md",
        "review-claude-{plan,eng,code,meta}-r{N}.md": "review-codex-{plan,eng,code,meta}.md",
        "Claude 회차 파일은 단계별로 최소 1개": "Codex-led 리뷰 파일은 단계별로 1개",
        "Claude+Codex": "Codex-led",
        "Agent 툴 오류": "spawn_agent 오류",
        "Doc Agent": "문서 수정",
        "Dev Agent": "개발 수정",
    }

    adapted = body
    for before, after in replacements.items():
        adapted = adapted.replace(before, after)

    adapted = adapted.replace(
        "| 일반 기능 | `review-codex-plan.md` + `review-codex-plan.md` + `review-codex-eng.md` + `review-codex-eng.md` + `review-codex-code.md` + `review-codex-code.md` |",
        "| 일반 기능 | `review-codex-plan.md` + `review-codex-eng.md` + `review-codex-code.md` |",
    )
    adapted = adapted.replace(
        "| 하네스 메타 변경 | `review-codex-meta.md` + `review-codex-meta.md` |",
        "| 하네스 메타 변경 | `review-codex-meta.md` |",
    )
    adapted = adapted.replace(
        "# 일반 기능 — 6개 전부 존재해야 통과 (단, review-codex-*.md는 최소 1개 이상 회차)",
        "# 일반 기능 — 3개 전부 존재해야 통과",
    )
    adapted = adapted.replace(
        "# 하네스 메타 변경 — 2종 존재 필수",
        "# 하네스 메타 변경 — 1종 존재 필수",
    )
    return adapted


def render_skill(source: Path) -> str:
    name = source.stem
    meta, body = split_frontmatter(source)
    original_description = meta.get("description")
    if not original_description:
        raise ValueError(f"{source} missing description")

    description = codex_description(name, original_description)
    rel_source = source.relative_to(ROOT)

    adapted_body = adapt_body_for_codex(body)

    return (
        "---\n"
        f"name: {name}\n"
        f"description: {json.dumps(description, ensure_ascii=False)}\n"
        "---\n\n"
        f"> Generated from `{rel_source}`. Do not edit this file directly; run "
        "`rtk python3 scripts/sync-codex-skills.py` after changing the Claude skill source.\n\n"
        "## Codex Adapter Notes\n\n"
        "- Treat this as the Codex project-local equivalent of the matching Claude `/rp-*` skill.\n"
        "- Resolve copied relative links against the source file under `docs/skills/` when needed.\n"
        "- Do not record Claude-only `.claude` hooks or slash commands as executed unless they actually ran.\n"
        "- Use Codex `spawn_agent` for independent review when a review step requires role separation.\n"
        "- Write Codex-led evidence to `review-codex-*.md`; never synthesize `review-claude-*.md` evidence.\n\n"
        + adapted_body
    )


def build_tree(target: Path) -> list[str]:
    target.mkdir(parents=True, exist_ok=True)
    names: list[str] = []

    for source in sorted(SOURCE_DIR.glob("rp-*.md")):
        name = source.stem
        names.append(name)
        skill_dir = target / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(render_skill(source), encoding="utf-8")

    return names


def sync() -> None:
    if DEST_DIR.exists():
        for child in DEST_DIR.iterdir():
            if child.is_dir() and child.name.startswith("rp-"):
                shutil.rmtree(child)
    build_tree(DEST_DIR)


def install_user() -> None:
    USER_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    names = [source.stem for source in sorted(SOURCE_DIR.glob("rp-*.md"))]

    for name in names:
        target = DEST_DIR / name
        link = USER_SKILLS_DIR / name
        if link.is_symlink() or not link.exists():
            if link.exists() or link.is_symlink():
                link.unlink()
            link.symlink_to(target, target_is_directory=True)
            continue
        print(f"skip existing non-symlink: {link}", file=sys.stderr)


def check() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dest = Path(tmp) / "skills"
        names = build_tree(tmp_dest)

        missing: list[str] = []
        changed: list[str] = []

        for name in names:
            expected = tmp_dest / name / "SKILL.md"
            actual = DEST_DIR / name / "SKILL.md"
            if not actual.exists():
                missing.append(name)
                continue
            if actual.read_text(encoding="utf-8") != expected.read_text(encoding="utf-8"):
                changed.append(name)

        extra = sorted(
            child.name
            for child in DEST_DIR.glob("rp-*")
            if child.is_dir() and child.name not in names
        )

    if missing or changed or extra:
        if missing:
            print("missing:", ", ".join(missing), file=sys.stderr)
        if changed:
            print("out-of-date:", ", ".join(changed), file=sys.stderr)
        if extra:
            print("extra:", ", ".join(extra), file=sys.stderr)
        return 1

    print(f"Codex skills in sync: {len(names)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated skills are current")
    parser.add_argument(
        "--install-user",
        action="store_true",
        help="symlink generated rp-* skills into $CODEX_HOME/skills for Codex discovery",
    )
    args = parser.parse_args()

    if args.check:
        return check()

    sync()
    if args.install_user:
        install_user()
    print(f"Generated Codex skills in {DEST_DIR.relative_to(ROOT)}")
    if args.install_user:
        print(f"Installed user skill links in {USER_SKILLS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
