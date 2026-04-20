# PRD: rp-* 스킬 심링크 자동 동기화

**상태:** In Review
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

PR #19 회고에서 도출:
1. 새 `rp-*` 스킬 추가 시 `.claude/commands/` 심링크를 수동으로 생성해야 해서 PR #18처럼 빠뜨리기 쉬움
2. `/reload-plugins` 해도 슬래시 커맨드로 노출되지 않아 실사용 불가 상태가 됨

## 영향 파일

| 파일 | 변경 |
|------|------|
| `.claude/hooks/sync-rp-commands.sh` | **신규**. Write 툴이 `docs/skills/rp-*.md`에 쓸 때 `.claude/commands/` 심링크 자동 생성 |
| `.claude/settings.json` | `PostToolUse` 훅에 위 스크립트 등록 (matcher: `Write`) |
| `docs/skills/rp-init.md` | "새 rp-* 스킬 추가 시 심링크 동시 생성" 규칙 명시 (자동 훅 + 수동 fallback 안내) |
| `docs/skills/rp-workflow.md` | 신규 스킬 추가 절차에 심링크 체크 항목 추가 |
| `docs/harness-workflow.md` | 공통 규칙 섹션에 심링크 자동 동기화 설명 |

## 롤백 전략

- 훅 파일 삭제 + `settings.json`에서 PostToolUse 항목 제거
- 훅 실패해도 기존 수동 `ln -s` 절차는 유지되므로 영향 없음
- 훅이 오작동하면 사용자가 직접 `rm .claude/commands/rp-*.md` 후 재생성 가능

## 검증

- 훅 스크립트 `set -euo pipefail` + 실패 시 exit 0 (워크플로우 차단 방지)
- JSON 입력 파싱: `jq -r '.tool_input.file_path // empty'`
- 경로 패턴 매칭: `*/docs/skills/rp-*.md`만 대상
- 이미 심링크 존재하면 noop
- Claude 자체 점검 + Codex 1회 리뷰 (pwd 확인 후)
- 각 파일 200줄 이내
