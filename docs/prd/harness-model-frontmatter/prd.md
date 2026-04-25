# PRD — Skill frontmatter `model:` 자동 강제 (간소 PRD)

| 항목 | 값 |
|---|---|
| 작성일 | 2026-04-25 |
| 종류 | 하네스 메타 변경 (단축 경로) |
| 통합 브랜치 | main |
| 작업 브랜치 | feat/harness-model-frontmatter |

## 1. 변경 이유

직전 머지된 PR #31 의 모델 정책은 룰만 있고 자동 강제 메커니즘 부재 — 사용자가 `/model` 슬래시로 직접 전환해야만 적용. Claude Code 공식 기능 [Skill frontmatter `model:` 필드](https://code.claude.com/docs/en/custom-skills.md) 가 슬래시 커맨드 실행 시 모델을 자동 전환하므로(현 턴만 적용, 다음 턴 세션 모델 복귀), 13개 `docs/skills/rp-*.md` 의 frontmatter 에 `model:` 필드를 직접 부여해 정책 자동 강제.

## 2. 영향 파일

| 파일 | 변경 |
|---|---|
| `docs/skills/rp-specify.md` | `model: opus` |
| `docs/skills/rp-prd.md` | `model: opus` |
| `docs/skills/rp-{init,plan-review,eng-review,task,dev,qa,code-review,ship,retro,workflow,amend}.md` | `model: sonnet` |
| `CLAUDE.md` | "모델 선택 정책 (자동 적용)" 섹션 강도 갱신 — "권장" → "frontmatter 자동 적용". 사용자 수동 전환은 보조 |

`.claude/commands/rp-*.md` 는 `docs/skills/rp-*.md` 심링크 — 추가 변경 불필요. `.codex/skills/` 변환본은 codex 용으로 model 필드 무관 (기존 sync-codex-skills.py 처리).

## 3. 롤백

| 상황 | 조치 |
|---|---|
| Skill frontmatter `model:` 필드를 Claude Code 가 인식 못함 | 단일 commit revert. 영향 = 13개 skill 파일 + CLAUDE.md |
| 정책 매핑 변경 (예: rp-eng-review 도 Opus 환원) | 해당 파일 1줄 수정 PR |
| 자동 전환이 다음 턴 복귀 안 하고 세션 영구 변경 | Claude Code 버그 — 공식 이슈 보고 + 우회 (사용자 `/model` 수동 환원) |

## 4. 검증

| # | 절차 |
|:-:|---|
| 1 | 본 PR 머지 직후 새 세션에서 `/rp-prd` 슬래시 실행 → 응답 모델이 Opus 인지 확인 (응답 헤더 또는 `/model` 출력) |
| 2 | 같은 세션에서 다음 턴(예: `/rp-task`) 실행 → 모델 Sonnet 으로 자동 전환 확인 |
| 3 | `/rp-specify` 도 Opus 로 동작하는지 확인 (대화형 질문 5단계 진행) |
| 4 | `lint-docs` CI 통과 (마크다운 + 링크 정상) |
| 5 | Codex 메타 단일 리뷰 통과 |
| 6 | 4주 후 회고에서 (a) 단계별 사용 모델 (b) 재작업 회차 (c) Codex High/Critical 발견 수 정량 측정. 정책 유지·조정 결정 |
