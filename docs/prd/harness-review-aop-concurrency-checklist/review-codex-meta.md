# Codex Meta Review — harness-review-aop-concurrency-checklist

- 대상: `docs/harness-code-review.md`, `docs/prd/harness-review-aop-concurrency-checklist/prd.md`
- 기준 참조: `docs/prd/harness-meta-retro-followups-r1/review-codex-meta.md`

## Summary

> The rule hardening is materially better and should catch the original T-22 `this.xxx()` and read-decide-write race patterns, but two policy gaps still weaken deterministic review: the `RACE-ACCEPTED` escape hatch is self-certifying, and the non-Spring framing in 1b mixes examples that are not actually the same proxy-bypass failure mode. The PRD checklist is also stale against the current rule text.

## Findings

### P1 — Critical (blocks merge)

없음.

### P2 — Important (should fix before merge)

#### F1. `RACE-ACCEPTED` 예외가 작성자 메모만으로 상한을 해제할 수 있음

File: `docs/harness-code-review.md:25-37`

Reasoning:
1a는 동시성 방어가 없을 때 정확성 7점 상한을 걸어 두었지만, 바로 아래에서 `대상 클래스 JavaDoc 또는 PR 본문`에 `RACE-ACCEPTED` 메모만 남기면 그 상한을 해제할 수 있게 열어 둡니다. 그런데 이 문구에는 승인 주체, 참조해야 할 외부 근거, 보정 메커니즘의 검증 방법이 없습니다. 현재 표현대로면 작성자가 PR 본문에 허용 이유를 직접 적는 것만으로 예외를 자기 승인할 수 있고, 리뷰어도 코드 밖 사실을 확인하지 않은 채 7점 초과를 줄 수 있어 동시성 게이트가 약해집니다.

Suggested fix:
`RACE-ACCEPTED`를 허용하려면 최소한 `승인 근거 링크(이슈/PRD/retro) + 보정 메커니즘 식별자(배치 이름, 스케줄러, 재조회 경로) + 검증 증거`를 필수로 요구하고, 리뷰어가 확인한 위치를 리뷰 본문에 인용하도록 규칙을 좁히십시오.

#### F2. 1b의 타 스택 예시가 실제 self-invocation 프록시 우회와 동일하지 않아 오적용 위험이 있음

File: `docs/harness-code-review.md:39-43`

Reasoning:
1b의 핵심 규칙은 Spring AOP처럼 "프록시/데코레이터를 거쳐야 적용되는 메서드 어드바이스"가 같은 객체 내부 직접 호출로 우회되는 경우를 잡는 것입니다. 그런데 적용 범위 문단은 Python FastAPI `Depends`, Go `context` propagation까지 같은 범주로 묶고 있습니다. 이 둘은 Spring의 `this.xxx()` 우회와 동일한 메서드 디스패치 문제로 보기 어렵기 때문에, 비-Spring 리뷰어가 "모든 dependency/context 전달 문제를 1b FAIL로 본다"거나 반대로 "예시가 안 맞으니 1b 자체를 skip한다"는 혼선을 만들 수 있습니다.

Suggested fix:
1b를 `프록시/데코레이터/인터셉터 기반 메서드 어드바이스`에 한정한다고 먼저 정의하고, 예시도 그 메커니즘에 직접 대응하는 항목으로 교체하십시오. 동치 예시를 유지하려면 "해당 스택에 이런 메서드-경유 어드바이스가 없으면 1b는 N/A"라는 문장을 추가하는 편이 안전합니다.

#### F3. PRD 검증 체크리스트가 현재 규칙 문구와 리뷰 상태를 정확히 반영하지 못함

File: `docs/prd/harness-review-aop-concurrency-checklist/prd.md:28-33`

Reasoning:
검증 항목 2는 `1b. Spring AOP self-invocation 금지`와 `"6점 고정" 규칙`을 요구하지만, 실제 변경 문서는 `프록시 기반 self-invocation 금지 (Spring AOP 예)` 제목과 `전체 FAIL 고정` 규칙으로 작성돼 있습니다 (`docs/harness-code-review.md:39-53`, `docs/harness-code-review.md:129-145`). 또 검증 항목 3은 "Claude ... r1 통과"를 요구하지만, 실제 산출물은 r1 FAIL / r2 PASS입니다. 이 상태면 PRD의 4섹션 계약 중 검증 섹션이 현재 산출물과 어긋나 있어, 완료 판정 기준으로 쓰기 어렵습니다.

Suggested fix:
검증 체크리스트를 현재 문구에 맞게 갱신하십시오. 1b 항목은 실제 제목과 `전체 FAIL` 규칙으로 고치고, Claude 검증은 `r1/r2 review evidence exists and latest round passes`처럼 산출물 기반 문장으로 바꾸는 편이 맞습니다.

### P3 — Minor (nice to have)

#### F4. 1b가 같은 빈 `this.xxx()`만 강조해 다른 대표적 프록시 미적용 패턴은 아직 놓칠 수 있음

File: `docs/harness-code-review.md:43-53`

Reasoning:
현재 1b는 same-bean `this.xxx()` 케이스를 매우 선명하게 잡도록 개선됐고, T-22 재발 방지 목적에는 충분합니다. 다만 Spring 계열에서 리뷰어가 자주 놓치는 인접 패턴인 `private/final 메서드에 붙은 어드바이스`, 초기화 시점 호출(`@PostConstruct` 등), 프록시 생성 전 자기 호출은 표나 경고문에 포함돼 있지 않습니다. 이번 변경의 핵심 목적이 "다음 Claude 리뷰어가 프록시 미적용을 놓치지 않게 하는 것"이라면, 현재 문구만으로는 self-invocation 외 변형 케이스까지 교육되지는 않습니다.

Suggested fix:
1b 말미에 "self-invocation 외에도 private/final/init-time 호출은 프록시 적용 여부를 별도 확인"이라는 경고문을 추가하거나, 안티 패턴 표에 2~3개 대표 행을 보강하십시오.

## Merge Readiness

Not ready.

`docs/harness-code-review.md` 자체는 T-22 재발 방지 관점에서 상당히 강화됐지만, P2 3건이 남아 있으면 예외 적용과 검증 완료 판정이 리뷰어마다 달라질 수 있습니다. 특히 `RACE-ACCEPTED` 검증 방식과 PRD 체크리스트 불일치는 머지 전에 정리하는 편이 맞습니다.
