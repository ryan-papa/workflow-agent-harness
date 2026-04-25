---
description: 하네스 전체 워크플로우 오케스트레이터. 신규 프로젝트·기능을 init부터 회고까지 12단계로 진행
argument-hint: '[프로젝트·기능 설명]'
---

# rp-workflow

전체 하네스 워크플로우 오케스트레이터.

## 트리거

- 사용자가 **새 기능·프로젝트**를 요청할 때
- `/rp-workflow` 명령

**기존 프로젝트 수정·추가는 `/rp-amend` 사용** (이 스킬은 init부터 시작하므로 부적합)

## 역할

각 단계의 스킬을 순서대로 호출하고 단계 간 전환 조건을 관리한다.

## 자동 전환 규칙

**모든 단계는 완료 시 다음 단계로 자동 진입한다.**
사용자가 멈추는 지점은 **산출물 보고[10]만**(사용자 승인 대기).

각 스킬 파일 하단 `▶ 자동 전환` 섹션에 전환 지시가 명시되어 있다.

## 플로우

| 순서 | 스킬 | 자동 전환 | 중단 조건 |
|:----:|------|:--------:|----------|
| 1 | `/rp-init` | → [2] | — |
| 2 | `/rp-specify` | → [3] | — |
| 3 | `/rp-prd` | → [4] | — |
| 4 | `/rp-plan-review` → `/codex:review --wait` (1회) | → [5] | Claude 3회 실패 → 사용자 보고 |
| 5 | `/rp-eng-review` → `/codex:review --wait` (1회) | → [6] | Claude 3회 실패 → 사용자 보고 |
| 6 | `/rp-task` | → [7] | — |
| 7 | `/rp-dev` | → [8] | 빌드/테스트 실패 |
| 8 | `/rp-qa` | → [9] | 3회 실패 → 사용자 보고 |
| 9 | `/rp-code-review` → `/codex:review --wait --base main` (1회) | → [10] | Claude 3회 실패 |
| 10 | 산출물 보고 | → [11] 커밋·PR | — |
| 11 | `/rp-ship` (**필수 호출**, 수동 git/gh 우회 금지) | 커밋·PR 자동 → **⏸ 배포 승인 대기** | CI 실패 |
| 12 | `/rp-retro` | 종료 | — |

## 상태 메시지

각 단계 전환 시 출력:
- 진입: `▶ [N] 단계명...`
- 완료: `✓ [N] 단계명 완료`
- 실패: `✗ [N] 단계명 실패 — [사유]`

## 규칙

- **메타 변경 단축 경로** — 하네스 문서(`docs/`, `CLAUDE.md`, 스킬, `.claude/settings.json`) 변경은 `rp-init`·`rp-specify`·`rp-task`·`rp-dev` **스킵** + feat 브랜치 + `rp-prd` 간소 경로 + `rp-plan-review` + `rp-code-review` + `rp-ship`으로 진행. `main` 직접 수정 금지
- **신규 `rp-*` 스킬 추가 시 심링크 자동 동기화** — `docs/skills/rp-*.md` 생성 감지 시 `PostToolUse` 훅이 `.claude/commands/rp-*.md` 심링크 자동 생성. 훅 실패 시 수동 fallback: `cd .claude/commands && ln -s ../../docs/skills/rp-새이름.md rp-새이름.md`
- **전 단계 자동 연결** — 각 스킬 완료 시 다음 스킬 자동 호출
- **유일한 멈춤 지점** — 배포[11]에서만 사용자 승인 대기 (커밋·PR까지는 자동)
- QA([8]), 코드리뷰([9]) **생략 불가**
- **[4][5][9] Codex 추가 리뷰 생략 불가** — Claude 통과 후 `/codex:review --wait` 1회 실행, High/Critical 지적 반영 필수
- 산출물 보고([10]) 없이 배포([11]) 진행 **금지**
- 회고([12]) **생략 불가** — 배포 완료 후 반드시 수행
- 각 스킬의 상세 규칙은 해당 스킬 파일 참조

→ 워크플로우 상세: [`../harness-workflow.md`](../harness-workflow.md)
→ Codex 리뷰 규칙: [`../harness-codex-review.md`](../harness-codex-review.md)
