# 간소 PRD: 코드 리뷰 기준에 AOP self-invocation + 동시성 체크리스트 추가

## 변경 이유

museum-finder T-22 (정보 확인 중 자동 배지) 배포 후 회고(`repositories/museum-finder/docs/research/retro-T22.md`) 에서 Claude r1 리뷰가 놓친 치명 이슈 2건을 Codex 리뷰가 포착:

| # | Codex 지적 | Claude r1 놓침 사유 |
|:-:|-----------|------|
| P1-01 | `InfoCheckBadgeService.evaluateAll()` → `this.evaluate()` self-invocation 으로 `@Transactional` + `@CacheEvict` AOP 프록시 우회 | 프록시 호출 경로를 정적으로 추적하는 체크리스트 항목이 `harness-code-review.md` 에 없음 |
| P1-02 | `read-decide-write` 경로(ip_hash 집계 → ON/OFF 판정)에서 두 트랜잭션이 서로의 insert 를 못 봐 배지 미점등 레이스 | "동시성 처리" 가 9~10점 설명문에만 있고, 감지 패턴·필수 방어책이 명문화되지 않아 리뷰어가 스킵 |

Codex "추가 1회" 리뷰 덕에 머지 전 수정됐지만, 향후 **Codex 가 놓친 유사 패턴**은 배포 후에야 드러남. Claude 리뷰 체크리스트 자체를 강화해 이중 리뷰의 첫 번째 관문 실효성을 끌어올린다.

**목표**: `harness-code-review.md` 정확성 섹션에 (1) 동시성 체크리스트 (2) AOP self-invocation 금지 두 항목을 명문화. 실행 코드 변경 없음.

## 영향 파일

| 파일 | 변경 내용 |
|------|----------|
| `docs/harness-code-review.md` | (1) 정확성 섹션 아래 `1a. 동시성 필수 체크리스트` + `1b. 프록시 기반 self-invocation 금지` 서브섹션 추가. 패턴 표 + 필수 방어책 + 8점 질문 각 1개. 스택 독립 원칙(Python·Node·Go 치환 기준) 명시. 명시적 포기 메모(`RACE-ACCEPTED`) 옵션 포함. (2) 판정 섹션에 "특수 규칙" 표 추가 — 1a=감점형(7점 상한), 1b=FAIL형(전체 FAIL 고정, 우회 불가) 강도 차이 명문화 |

## 롤백 전략

단일 문서 변경. `git revert <merge-commit>` 또는 PR close로 즉시 원복. 실행 코드 영향 0, 다른 스킬·설정 연쇄 변경 없음.

## 검증

- [x] `harness-code-review.md` 정확성 섹션에 `1a. 동시성 필수 체크리스트 (read-decide-write 경로)` 서브섹션 존재 — 스택 독립 원칙·5패턴 표·**"7점 상한" 감점형 규칙**·`RACE-ACCEPTED` 3요소(승인근거·보정메커니즘·검증증거) 포기 메모 옵션·8점 질문 포함
- [x] `harness-code-review.md` 정확성 섹션에 `1b. 프록시 기반 self-invocation 금지 (Spring AOP 예)` 서브섹션 존재 — 프록시/데코레이터/인터셉터 경유 어드바이스 정의·타 스택 예(Celery·Nest·gRPC)·N/A 선언 규칙·**"전체 FAIL 고정" FAIL형 규칙**·피호출자 기준 8점 질문 포함
- [x] `harness-code-review.md` 판정 섹션에 "특수 규칙" 표 추가 (1a 감점형 / 1b FAIL형 강도 차이 명문화)
- [x] Claude 서브에이전트 meta 리뷰 증거 존재 — r1 FAIL (평균 7.67/최저 6) → r2 PASS (평균 8.83/최저 8), 최신 회차 PASS (역할 분리: 서브에이전트 채점, Codex 는 메인)
- [x] `/codex:review --wait` 1회 실행 + `review-codex-meta.md` 저장
- [x] Codex High/Critical(P1) 지적 모두 반영 (P1 0건, P2 3건 전량 반영: `RACE-ACCEPTED` 자가승인 방지 · 1b N/A 규칙 · PRD 검증 갱신)
- [x] CLAUDE.md 트리·스킬 참조 변경 없음 확인 (본 변경은 `harness-code-review.md` 본문 확장만)
