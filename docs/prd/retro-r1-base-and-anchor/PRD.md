# PRD — 회고 반영 R1: 메타 변경 PR base + CI anchor strip + 자동 머지 + 회고 수동 모드

> 하네스 메타 변경(간소 PRD). 회고 반영 사이클 (Q1~Q4 결정 결과 통합).

## 1. 변경 이유

PR #29 회고 채택(2건) + 사용자 추가 지시(2건). 배경: [retro-r1.md](retro-r1.md).

| # | 문제 | 영향 |
|---|------|------|
| 1 | 메타 변경 단축 경로에서 `rp-ship` PR base 자동 감지가 `docs/tasks.md`의 다른 feature 통합 브랜치(예: `feat/security-guide`)를 잘못 매칭. 매번 수동 오버라이드 `--base main` 필요 | 메타 변경 ship 사이클마다 추가 인지 부담, 실수 시 잘못된 base로 PR 생성 위험 |
| 2 | CI lint-docs `Check for broken internal links` 단계가 마크다운 링크의 fragment(샵 뒤 섹션 anchor) 부분까지 파일 경로로 해석해 오탐 | PR #29 1차 CI 실패. 모든 anchor 포함 내부 링크가 영향받음 |
| 3 | rp-ship 머지 단계가 항상 사용자 승인 대기. 메타 변경·일반 기능 모두 CI·게이트 통과 후에도 인지 부담·대기 시간 발생 | 자동화 흐름 단절. 한 사이클당 추가 round-trip 1회 |
| 4 | rp-ship 완료 시 `/rp-retro` 자동 진입 강제. 단순 메타 변경·소규모 PR에도 회고 강제로 노이즈 | 회고 가치 < 진행 비용 케이스에서 흐름 둔화 |

## 2. 결정 사항

| 항목 | 결정 |
|------|------|
| 메타 변경 PR base | `rp-ship` 절차에 분기 추가: **현재 ship 사이클의 PRD 폴더가 `rp-prd` 간소 PRD(메타 변경)인 경우, PR base 자동 감지를 건너뛰고 `--base main` 적용**. 판정 기준: PRD 폴더 내 `review-claude-meta-r{N}.md` 또는 `review-codex-meta.md` 존재 여부. 일반 기능(`review-claude-{plan,eng,code}-r*.md` 존재) 경로는 기존 자동 감지 유지 |
| 수동 오버라이드 우선순위 | 사용자가 `--base <X>` 명시 전달 시 메타 분기 무시하고 `<X>` 사용 (기존 규칙 유지) |
| CI anchor strip | `.github/workflows/ci.yml` `Check for broken internal links` 단계에서 `target="$dir/$link"`를 `target="$dir/${link%%#*}"`로 변경. 빈 fragment는 path.md만 남음. 외부 URL은 기존 `^http` 필터로 제외 |
| **자동 머지 (Q1=1)** | 모든 워크플로우(메타·일반 기능)에서 PR 생성 + CI 통과 후 **사용자 승인 없이 자동 `gh pr merge --merge`**. 단 아래 "자동 머지 안전 가드" 모두 충족 시에만 |
| **자동 머지 안전 가드 (Q2=2)** | AND 조건: (a) CI 모든 체크 SUCCESS, (b) 리뷰 증거 파일 게이트 통과(기존 사전 체크 게이트), (c) PR base 자동 감지 또는 메타 분기 결과 정상(fail-closed 통과), (d) `gh pr view --json mergeable` 가 `MERGEABLE`. 하나라도 실패 → **자동 머지 중단 + PR 상태 OPEN 유지 + 사용자에게 즉시 보고**. `--admin`·`--no-verify` 우회 금지. 머지 전략은 `--merge` 고정 (squash·rebase 미사용) |
| **비상 탈출구** | 환경변수 `RP_SHIP_MANUAL=1` 설정 시 자동 머지 비활성화하고 기존 사용자 승인 모드로 동작. CI 통과 후 PR URL 보고 → 승인 대기. follow-up `--manual-merge` 플래그 구현 전까지의 대안 |
| **회고 자동 진입 제거 (Q3=2)** | `rp-ship` 완료 시 `/rp-retro` 자동 진입 **삭제**. 회고는 사용자가 명시적으로 `/rp-retro` 입력 시에만 실행. 자동 전환 메시지는 `✓ [11] 배포 완료. 회고가 필요하면 /rp-retro` 로 변경 |
| 적용 범위 | rp-ship.md, rp-retro.md, rp-{plan,eng,code}-review.md(자동 전환 문구), harness-workflow.md, ci.yml, CLAUDE.md 절대 규칙 |
| 수동 오버라이드 (자동 머지) | 사용자가 명시적으로 `--manual-merge` 플래그 전달 시 자동 머지 비활성, 기존 사용자 승인 모드 — **본 사이클에서는 미구현(차후 follow-up)**, 본 변경은 자동 머지 ON이 기본 |

## 3. 영향 파일

| 파일 | 변경 |
|------|------|
| `docs/skills/rp-ship.md` | (a) "PR base 자동 감지" 섹션에 메타 변경 분기 추가, (b) "사용자 승인 대기" 섹션을 "자동 머지 (안전 가드 4종)"로 교체, (c) 자동 전환 메시지를 "배포 완료 + 회고는 수동 명령" 으로 변경, (d) 절대 규칙 갱신 |
| `docs/skills/rp-retro.md` | "트리거"에서 "rp-ship 완료 직후 자동 진행" 삭제. "/rp-retro 명령 수동 실행"만 남김 |
| `docs/skills/rp-plan-review.md` | 자동 전환 문구의 "/rp-eng-review 자동 진입" 표현은 유지 (회고만 수동) |
| `docs/skills/rp-eng-review.md` | 동일 (변경 없음) |
| `docs/skills/rp-code-review.md` | 자동 전환 메시지에서 후속이 ship → ship 후 "회고 수동" 안내 |
| `docs/harness-workflow.md` | 12단계 흐름의 [11]→[12] 자동 전환을 [11]→(선택) [12] 로 변경 |
| `.github/workflows/ci.yml` | `Check for broken internal links` `target` 라인 1줄 수정 |
| `CLAUDE.md` | "배포[11]만 사용자 승인 대기" → "자동 머지(가드 4종)", "배포 완료 직후 회고 자동 시작" → "회고는 사용자 명령 시에만" |
| `.codex/skills/rp-{ship,retro,*-review}/SKILL.md` | sync 자동 동기화 |

## 4. 롤백

| 단계 | 절차 |
|------|------|
| 1 | `git revert <merge-commit>` |
| 2 | `rtk python3 scripts/sync-codex-skills.py --install-user` |
| 3 | 자동 머지로 인한 부작용(예상치 못한 main 변경) 발생 시 `gh pr revert` 또는 hotfix PR 생성 |

자동 머지 활성화 후 첫 1~2 사이클은 안전 가드 작동 여부를 사용자가 모니터링.

## 5. 검증

| 항목 | 방법 |
|------|------|
| CI fragment strip 동작 | 양성: anchor 포함 valid 링크 PASS / 음성: 의도적 broken 링크(`존재하지않는파일.md#x`) FAIL. 본 PR에 시뮬레이션 케이스 1건 포함하지 않음(기존 anchor strip 후 valid 링크가 정상 처리되면 양성 증명) |
| CI 기존 valid 링크 회귀 | 본 PR push 후 lint-docs PASS 확인 |
| 메타 변경 PR base 분기 | rp-ship.md 절차에 PRD 폴더 검사 후 `--base main` 분기 명시 grep |
| 일반 기능 경로 회귀 | 일반 기능 PRD 폴더 시뮬레이션 — meta 파일 부재 → 기존 자동 감지 유지 |
| 자동 머지 안전 가드 | rp-ship.md 자동 머지 절차에 4종 AND 조건(CI·게이트·base·MERGEABLE) 모두 명시 grep |
| 자동 머지 우회 차단 | `--admin`·`--no-verify` 명시 금지 문구 grep |
| 회고 수동 전환 | rp-retro.md 트리거에서 자동 진행 문구 제거 + rp-ship.md 자동 전환 메시지가 회고 수동 안내인지 grep |
| Codex 변환본 sync | `rtk python3 scripts/sync-codex-skills.py --check` 통과 |
| 본 PR 자체가 자동 머지 dogfood | 본 PR 머지 시점에 사용자 승인 단계가 발생하지 않으면 회귀 없음 (본 변경 적용 후 첫 사이클은 기존 사용자 승인 모드 유지) |
