# Retro — harness-ship-auto-base (PR #24) 머지 후 회고

- 시점: 2026-04-22
- 트리거: PR #24 main 머지 직후 — 하네스 절대 규칙 "배포/머지 직후 회고 생략 불가"
- 범위: 하네스 메타 변경 단일 리뷰 경로 (`rp-init` · `rp-specify` · `rp-task` · `rp-dev` 스킵, 간소 PRD + meta 리뷰 1회)

## 산출물 요약

| 항목 | 값 |
|------|---|
| PR | #24 (base=main, 수동 오버라이드) |
| 변경 파일 | 3 impl (`rp-ship.md` · `harness-ship.md` · `CLAUDE.md`) + 3 PRD (`prd.md` · `review-claude-meta-r1.md` · `review-codex-meta.md`) |
| Claude meta r1 | PASS 8.57 / 최저 7 |
| Codex meta | HIGH 3건 전량 반영 (오탐 방지 · fail-closed · 문서 원자 반영) |
| CI | lint-docs SUCCESS |
| 머지 커밋 | `cda277a` |

## 강점

| # | 항목 |
|:-:|------|
| S1 | **Codex HIGH 3건이 PRD 강화에 실질 기여**: r1 PRD 초안의 느슨한 감지 규칙(`feat/mvp-*` 폴백)이 Codex 지적으로 앵커링 + 정확히 1건 매칭 + fail-closed 로 격상. 메타 리뷰 이중화 가치 재확인 |
| S2 | **새 규칙이 즉시 tech debt 발견**: 구현 직후 하네스 자체 `docs/tasks.md` 에 stale `feat/security-guide` 선언이 남아있음을 드러냄 (원격 브랜치 부재 → fail-closed 정확 동작). 규칙이 설계대로 작동함을 실전 검증 |
| S3 | **수동 오버라이드 경로 존재**: fail-closed 발동 시 `--base main` 으로 우회 가능해 블로킹 없이 진행. 설계상 탈출구가 살아있음 |

## 이슈

| # | 심각도 | 항목 |
|:-:|:-----:|------|
| I1 | Medium | **하네스 루트 `docs/tasks.md` stale 선언 미정리**: `feat/security-guide` (2026-04-17 초기 과제) 가 완료됐음에도 파일에 남아 새 규칙 첫 실행에서 fail-closed 트리거. 본 PR 범위 밖으로 두었으나 **다음 하네스 메타 PR 직전 정리 필요** |
| I2 | Low | **감지 정규식 문법 명세의 이식성**: 문서에는 `^[\s\-\*\|]*통합 브랜치:...` 표기. grep ERE 는 `[[:space:]]` 요구, sed BRE 는 `\s` 미지원, Node/Python 은 OK. 실행 주체(Claude 에이전트)가 언어 독립 의미로 해석 가능하지만, 외부 CLI 스크립트로 이식 시 명시 변환 필요 |
| I3 | Low | **회고의 자동화 한계**: 본 리플릭션도 메인 에이전트 직접 작성. 메타 변경은 규모가 작아 영역별 서브에이전트 분리의 한계 효용이 낮음 — 현재 운영이 합리적 |

## 교차 분석

I1 (stale tasks.md) 은 본 PR 이 **성공적으로 검출한 결함** — 본 PR 에서 동시에 정리하면 scope creep, 별도 정리 PR 이 깔끔. 이 검출 사실 자체가 규칙 효용의 실증.

## 개선 제안

| # | 유형 | 제안 | 점수 |
|:-:|------|------|:----:|
| 1 | Followup PR | **하네스 루트 `docs/tasks.md` 정리** — 완료된 security-guide 태스크 이력을 `docs/prd/20260417_182747_security-guide_478d1984.md` 로 이동하거나 삭제. 단독 PR 로 최소 변경 | 8/10 ★ 추천 |
| 2 | 규칙 보강 | **감지 문법을 언어 독립 의사 코드로도 명시**: 현재 정규식 표기와 함께 "시작 앵커 + `통합 브랜치:` 리터럴 + 선택적 백틱 + 브랜치 이름 식별자" 문장형 설명 1줄 병기해 이식성 증대 | 6/10 |
| 3 | 반영 안 함 | 본 사이클은 종료, 후속 없이 marinate | 4/10 |

## 사용자 확인

위 1·2·3 중 반영 항목 번호 지정 시 후속 PR 자동 진행. 지정 없으면 본 사이클만 종료.
