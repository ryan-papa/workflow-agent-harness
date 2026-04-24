# Codex Code Review: harness-codex-skill-sync

Review stage: code review
Reviewer mode: Codex-led independent review with spawned subagent

## Findings

### High: Generated Codex skills still executed Claude-only workflow text verbatim

근거:
- `scripts/sync-codex-skills.py`가 원본 body를 그대로 붙여 `.codex/skills/rp-plan-review/SKILL.md`, `.codex/skills/rp-code-review/SKILL.md`에 Claude Agent tool과 `/codex:review` 실행 지시가 남았다.

영향:
- Codex 사용자가 Claude-only 명령을 실행한 것처럼 기록하거나 `review-claude-*` 증거를 합성할 위험.

### High: Skill sync hook did not run on Edit/MultiEdit

근거:
- `.claude/settings.json`의 `PostToolUse` matcher가 `Write`만 등록되어 기존 `docs/skills/rp-*.md` 수정 경로에서 동기화가 누락될 수 있었다.

영향:
- 문서가 약속한 `.codex/skills` 동기화가 실제 편집에서 stale 상태가 될 위험.

## 반영

| Finding | 반영 |
|---|---|
| Claude-only text | `scripts/sync-codex-skills.py`에 Codex body 변환을 추가. `/codex:review`, `review-claude-*`, Claude Agent tool 문구를 Codex-led review, `review-codex-*`, `spawn_agent` 문구로 변환 |
| Hook matcher | `.claude/settings.json`에 `Edit`, `MultiEdit` PostToolUse hook 추가 |

## Decision

Pass after fixes.

## Verification

- `rtk python3 scripts/sync-codex-skills.py --check`
- `rtk proxy sh -c 'for f in .codex/skills/rp-*; do python3 /Users/hose.kim/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$f" >/dev/null || exit 1; done; echo valid'`
- `rtk proxy python3 -m json.tool .claude/settings.json`
- `rtk rg -n "/codex:review|review-claude-(plan|eng|code|meta)|Agent 툴의 서브에이전트|subagent_type=general-purpose" .codex/skills`
