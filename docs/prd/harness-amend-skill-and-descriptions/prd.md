# PRD: rp-amend 신규 스킬 + 스킬 설명 추가

**상태:** In Review
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

1. `/rp-*` 스킬을 호출할 때 Claude Code UI·자동완성에서 설명이 노출되지 않아 사용자가 스킬 용도를 구별하기 어려움
2. 기존 프로젝트에 기능 **수정·추가**만 할 때 사용할 경량 진입 스킬이 없음. 지금은 처음부터 `rp-workflow` 실행 or 수동 단계 호출만 가능

## 영향 파일

| 파일 | 변경 |
|------|------|
| `docs/skills/rp-init.md` | YAML frontmatter (description + argument-hint) 추가 |
| `docs/skills/rp-specify.md` | 동일 |
| `docs/skills/rp-prd.md` | 동일 |
| `docs/skills/rp-plan-review.md` | 동일 |
| `docs/skills/rp-eng-review.md` | 동일 |
| `docs/skills/rp-task.md` | 동일 |
| `docs/skills/rp-dev.md` | 동일 |
| `docs/skills/rp-qa.md` | 동일 |
| `docs/skills/rp-code-review.md` | 동일 |
| `docs/skills/rp-ship.md` | 동일 |
| `docs/skills/rp-retro.md` | 동일 |
| `docs/skills/rp-workflow.md` | frontmatter + `rp-amend` 분기 추가 |
| `docs/skills/rp-amend.md` | **신규**. `rp-init` 스킵, `rp-specify` → `rp-prd`(Full) → 리뷰 → 개발 → QA → 코드리뷰 → ship → 회고 |
| `docs/harness-workflow.md` | `rp-amend` 경로 명시 |
| `CLAUDE.md` | 스킬 트리 갱신, `rp-amend` 용도 설명 |
| `README.md` | 워크플로우 개요에 `rp-amend` 추가 |

## 롤백 전략

문서만 변경. `git revert <merge-sha>`로 즉시 원복. 영향 범위는 스킬 표기·신규 파일뿐.

## 검증

- lint-docs CI 통과
- Claude 자체 점검 + Codex 1회 리뷰 → High/Critical 반영
- 각 파일 200줄 이내
- 신규 스킬 frontmatter YAML 파싱 가능 여부 (Claude Code 표준 형식)
