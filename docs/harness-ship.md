# Harness: 산출물 보고 + 배포

본 문서는 **정책·이유** SSOT. 실행 절차(커밋·PR·CI·머지·README 검증·머지 후 검증)는 [`skills/rp-ship.md`](skills/rp-ship.md) SSOT.

## 산출물 보고 → 자동 ship

QA + 코드리뷰 + 인프라 리뷰(또는 콘텐츠 검수) 통과 후 사용자에게 결과를 보고한다.

**보고 포맷:**
- QA 결과 요약 (통과/실패 항목)
- 코드리뷰 점수 (7항목 또는 빌드 검증)
- 인프라 리뷰 판정 (BLOCK / ASK / WARN 건수, 미실행 시 `N/A` + 사유)
- 리뷰 지적 처리 표 — 심각도 · 위치 · 처리(반영 / 미처리: 한도 소진 회차 Low) ([`harness-code-review.md`](harness-code-review.md) "지적 심각도")
- 변경 파일 목록 + 줄 수 변화
- "산출물 보고 완료, 커밋→PR→자동 머지 절차를 진행합니다" 안내

산출물 보고 후 `rp-ship`이 자동 시작된다. 기본 경로에는 사용자 승인 대기가 없고, 자동 머지는 SSOT 가드 통과 시에만 수행한다.

## 커밋 → PR → 배포 (실행 절차)

→ [`skills/rp-ship.md`](skills/rp-ship.md) "절차" 섹션 SSOT (PR base 결정, 자동 머지 가드 3종 AND, 비상 탈출구 포함)

## CI 정책

| 규칙 | 내용 |
|------|------|
| CI 없을 때 | PR 생성 시점에 "CI가 없습니다. 추가할까요?" 추천 |
| 추가 여부 | 사용자 선택 시에만 추가 |
| **⛔ 컨플릭트 선행 가드** | CI 대기 **이전**에 `mergeable` 선검사 (컨플릭트 시 CI 미실행 → `--watch` 무한 대기 차단). `CONFLICTING` 시 작업자가 `git merge origin/<base>` 자동 해소(안전 충돌만, 불확실 시 중단+보고), 사이클당 1회. 상세: [`skills/rp-ship.md`](skills/rp-ship.md) "컨플릭트 선행 가드" |
| CI 없이 머지 | CI 가드 (a) N/A, base·MERGEABLE 가드 통과 시 자동 머지 |
| **동일 브랜치 재작업** | 기존 PR이 MERGED/CLOSED면 **신규 PR 생성** (OPEN PR만 재사용) |
| **⛔ CI 통과 전 `gh pr merge` 호출 자체 금지** | 가드 (a) 3단계(`--watch` 대기 + exit 0 + pending/queued/in_progress/fail 0건) 모두 통과 전에는 머지 명령 실행 금지. 위반 시 즉시 revert + 배포 취소 + 회고 노트 의무 |
| **⛔ `gh pr merge --auto` 전면 금지** | 단독·옵션 조합 무관. `Free plan` + `private repo` 등 branch protection 인프라 결손 환경에서 즉시 머지 fallback → 가드 무력화. SSOT 가 유일한 가드 |

> ⛔ CI 통과 전 머지 금지 · `--admin`/`--no-verify`/`--auto` 우회 금지 · 자동 머지 가드 3종 AND · PR base 자동 감지(fail-closed) · 위반 시 즉시 revert + 회고 의무 → 본문은 [`harness-absolute-rules.md`](harness-absolute-rules.md) SSOT 참조

## 푸시 전 README 검증 (정책)

모든 push 전 README.md 가 프로젝트 현 상태와 일치해야 한다.

| 항목 | 정책 |
|------|------|
| 검증 5항목 | 프로젝트 개요·디렉토리 구조·설치/실행·기능 목록·기술 스택 |
| 통과 기준 | 평균 ≥ 8.0 |
| 실패 시 | README 수정 → 재검증 (최대 3회) → 3회 실패 시 사용자 판단 위임 |
| 미통과 효과 | **push 차단** |

→ 실행 절차: [`skills/rp-ship.md`](skills/rp-ship.md) "README 검증" SSOT

## PR 생성 시 PRD 요약 본문 포함 (정책)

`gh pr create` 시 본문에 PRD 요약을 처음부터 임베드한다. PRD 디렉토리는 그대로 main 에 머지 (별도 정리 commit 금지 — CI 재실행 비용 차단). Full PRD·간소 PRD 모두 적용.

| 단계 | 내용 |
|------|------|
| 요약 임베드 | Full = `## 문제·맥락` + `## 기능 요구사항` / 간소 = `## 변경 이유` + `## 영향 파일` + `## 검증` → PR 생성 시 본문 `<details>` 블록 |
| 롤백 전략 추출 제외 (의도) | 간소 PRD의 `## 롤백 전략`은 **운영자 내부 자료**로 PR 본문 미포함. PRD 원본(`docs/prd/[feature]/prd.md`)에는 4섹션 모두 보존 — `rp-ship.md` "PR base 자동 감지" 메타 분기 선검사 시 4섹션 검증 |
| 인프라 리뷰 노트 | 인프라 축 실행 시 별도 섹션 추가 — 판정 요약·자문 지적·인프라 선행 작업. **식별 정보 일반화 의무** (SSOT: [`harness-infra-review.md`](harness-infra-review.md)) |
| 추출 누락 | PR 생성 차단 |
| 최초 PR 독립 리뷰 | 신규 PR 생성 시에만 [`skills/rp-pr-review.md`](skills/rp-pr-review.md) 1회 (`연동` 표식 전달) — **출력만**, 게이트·머지 무영향 (재사용 PR 미호출). Medium 이상만 출력·후속 PR 대상, Low 는 건수만 |
| 사후 정리 | 없음 — PRD 디렉토리 main 영구 보존 (추적성 향상) |

→ 실행 절차: [`skills/rp-ship.md`](skills/rp-ship.md) "PR 생성" SSOT
→ 절대 규칙: [`harness-absolute-rules.md`](harness-absolute-rules.md) "PR 생성 시 PRD 요약 본문 포함 필수"

## 머지 후 정책

- 배포 완료 메시지 직후 `/rp-retro` 자동 진입 **금지** ([`harness-absolute-rules.md`](harness-absolute-rules.md): 회고는 사용자 명령 시에만)
- 배포 완료 시 라이브 URL 사용자에게 전달

→ 실행 절차: [`skills/rp-ship.md`](skills/rp-ship.md) "머지 후 검증" SSOT

## 최종 산출물

| 항목 | 기준 |
|------|------|
| 코드 | 실행 가능, 테스트 통과 |
| README | 간결 명료, 링크 참조 방식, **구조 변경 시 동기화 필수** |
| PRD | 열린 질문 업데이트 |

→ 스킬 상세: [`skills/rp-ship.md`](skills/rp-ship.md)
