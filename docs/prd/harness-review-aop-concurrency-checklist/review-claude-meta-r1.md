# Claude Meta Review r1 — 간소 PRD 단일 리뷰

- 실행 주체: 서브에이전트 (claude-projects 하네스 메타 변경 리뷰 위임)
- 대상:
  - `docs/prd/harness-review-aop-concurrency-checklist/prd.md`
  - `docs/harness-code-review.md` (정확성 1a·1b 서브섹션 추가)
- 역할 경계: Claude 채점만 수행, `/codex:review` 실행·저장은 메인 에이전트 담당
- 배경: museum-finder T-22 회고 C1·C2 (Codex 가 포착한 AOP self-invocation + read-decide-write 레이스) 대응

## 1. 항목별 점수 (메타 간소 리뷰 6항목, 각 0~10)

| 항목 | 점수 | 근거 |
|------|:---:|------|
| 문서 정합성 | 9 | PRD 4섹션(이유·영향·롤백·검증) 이 `harness-code-review.md` 1a·1b 실제 내용과 1:1 대응. T-22 회고 개선 제안 1·2(★9점) 가 서브섹션 1b·1a 로 문자 수준 반영됨. `review-codex-code-T22.md` P1-01·P1-02 의 예시(evaluateAll→this.evaluate, ip_hash 집계 후 OFF 전환) 가 패턴 표 첫 행으로 재사용돼 역추적 가능 |
| 하네스 연쇄 영향 | 7 | `harness-code-review.md` 본문만 확장·기존 7항목 10점 체계 유지. CLAUDE.md 트리·스킬 참조 경로 불변 확인(문서 위치·ID 변경 없음). 다만 **"최저 ≥7" 통과 조건과 1b "정확성·설계 최대 6점 고정" 간 상호작용**이 본문에 명시되지 않아 리뷰어 주관 여지 (상세는 I1) |
| 규칙의 실효성 | 8 | T-22 역체크: ① self-invocation — 1b 의 8점 질문 "같은 빈의 `this.xxx()` 로 어드바이스 메서드 호출?" 이 `InfoCheckBadgeService.evaluateAll()` → `this.evaluate()` 를 **정적 grep 수준에서 포착 가능** (이진 판정). ② 동시성 — 1a "집계 후 상태 전이" 패턴 표 1행이 ip_hash distinct 집계 → 플래그 ON/OFF 와 정확히 일치, 방어책 "집계 대상 row `FOR UPDATE` 또는 단일 SQL UPDATE 에서 집계+판정" 이 Codex 권고와 일치. 양쪽 모두 T-22 회차 재실행 시 Claude r1 이 놓치지 않을 근거 확보 |
| 오·오버킬 | 6 | **패턴 표와 안티-패턴 표가 Spring/Java 맥락에 강하게 의존** (`@Transactional`·`@Cacheable`·`@CacheEvict`·`@Async`·`SELECT … FOR UPDATE`·`ON CONFLICT`·`advisory lock`). Python(FastAPI·Celery)·Node(Nest·TypeORM)·Go 프로젝트에서 본 체크리스트를 로드 시 "self-invocation" 과 동일 개념(decorator 기반 프록시·`@cache`·`asyncio`)이 있지만 **표 문구 그대로는 불일치** → 오버킬 또는 오탐 위험. PRD/서브섹션 서두에 "Spring/Java 한정" 또는 "프록시 기반 프레임워크 일반화 원칙" 명시 필요 (상세는 I2) |
| 누락 | 7 | ① PR 본문·커밋 메시지에 레이스 방지 방식을 명시하라는 T-22 회고 제안 2의 "PR body 기록" 은 1a 에 반영되지 않음 (체크리스트는 코드 내 방어만). ② 1b FAIL 조건("있으면 무조건 지적") 과 1a "7점 상한" 의 판정 강도 차이 이유 설명 없음. ③ `AopContext.currentProxy()` 권장 안 하는 이유("지양") 근거 링크 없음 — 초심자 리뷰어가 자기근거로 반박 가능 |
| 롤백 안전 | 9 | 단일 문서 변경, 실행 코드 0, 스킬·settings 연쇄 없음. `git revert` 즉시 원복 가능. PRD 롤백 섹션이 이를 정확히 명시. 검증 체크에 "CLAUDE.md 트리·스킬 참조 변경 없음 확인" 항목 포함 — 재차 안전 장치 |

**평균: (9+7+8+6+7+9)/6 = 7.67** / 최저: 6 / **판정: FAIL**

> 기준: 평균 ≥ 8.0 **그리고** 최저 ≥ 7. 평균 7.67 < 8.0 + 최저 6 < 7 → FAIL.
> 참고: `review-claude-meta-r1.md` (선례) 평균 8.29 / 최저 7 과 대비.

## 2. 발견 이슈

| # | 심각도 | 항목 | 내용 |
|:-:|:----:|------|------|
| I1 | High | 하네스 연쇄 영향 | **"최저 ≥7" 통과 조건 vs 1b "정확성·설계 최대 6점 고정" 의 의도 불명확**. 현재 문구대로라면 self-invocation 발견 시 정확성·설계 둘 다 6점 고정 → 최저 ≥7 자동 실패 → 전체 FAIL 고정. 이게 의도라면 `harness-code-review.md` "판정" 섹션에 "1b FAIL 조건 적중 시 전체 FAIL (우회 불가)" 한 줄 명시 필요. 의도가 아니라면(단순 감점) 상한값 조정 필요 |
| I2 | High | 오·오버킬 | **비-Spring 프로젝트(Python·Node·Go) 리뷰 시 1a·1b 적용 기준 부재**. 1a 패턴 표의 `FOR UPDATE`·`ON CONFLICT` 는 PostgreSQL 특화. 1b 는 `@Transactional`·`@Cacheable` 등 Spring 어노테이션 열거. 타 스택 프로젝트 서브에이전트 리뷰어가 "본 체크리스트 적용 제외" 로 오판할지, "프록시·자기호출 일반 원칙으로 확장 적용"할지 판단 기준 미제공 |
| I3 | Med | 누락 | **1a 방어책에 "명시적 포기 메모" 또는 "PR 본문 기록" 옵션 부재**. 회고 제안 2는 "코드 내 방어 OR PR body 레이스 허용 근거 문서화" 였으나 현 1a 는 코드 방어만 7점 초과 허용. 배지·분석 지표처럼 "일시적 불일치 허용 + 스케줄러 보정" 이 명시적 설계인 경우 현재 문구로는 7점 상한 고정 |
| I4 | Med | 규칙의 실효성 | **1b "정확성·설계 최대 6점 고정" 문구의 "고정" 이 8점 질문 "있으면 무조건 지적(FAIL 조건)" 과 표현 불일치**. "6점 고정" = 하락 상한, "FAIL 조건" = 통과 실패 — 의미가 다름. 한쪽으로 통일(예: 둘 다 "발견 시 전체 FAIL") 필요 |
| I5 | Low | 누락 | `AopContext.currentProxy()` "지양" 이유(테스트성·AOP 프록시 노출 결합도) 각주·링크 부재. 리뷰어가 지양 이유를 되묻는 순환 발생 가능 |
| I6 | Low | 문서 정합성 | PRD 검증 체크리스트 `[ ]` 6개 중 "Claude 서브에이전트 meta 리뷰 r1 통과" 가 본 리뷰 자체 — 현재 r1 FAIL 로 미체크 상태 유지. r2 재실행 전제 |
| I7 | Low | 오·오버킬 | 1a 패턴 표 "외부 API 호출 + 상태 저장" 행의 "afterCommit·트랜잭션 outbox" 는 Spring 밖에서도 통용 가능하나, 동일 표 내 다른 행의 `FOR UPDATE` 와 서술 일관성 낮음 — 스택 비의존 표현(락·멱등성 키·이벤트 저장)으로 통일 가능 |

## 3. 수정 권고 (FAIL 원복 차단 요소: R1·R2. 나머지는 동반 권장)

| # | 대응 이슈 | 권고 |
|:-:|:-------:|------|
| R1 | I1, I4 | `harness-code-review.md` "판정" 섹션에 **1b 적중 시 처리 규칙** 명시: "1b FAIL 조건 발견 → 전체 FAIL 고정 (재시도 3회 카운트 소비, 수정 후 r2 진행)". 1a 의 "7점 상한" 과 1b 의 "FAIL" 강도 차이를 표로 정리(예: 1a=감점형, 1b=FAIL형) |
| R2 | I2 | 1a·1b 서두에 **적용 범위 선언** 추가: "(Spring/Java 기본. 타 스택은 동치 패턴 — Python `@cached_property`·Celery task·FastAPI dependency · Node `class-transformer`·TypeORM transaction · Go `sync.Once`·context — 으로 치환 적용. 치환 불가 시 리뷰 노트에 근거 기록 후 해당 서브섹션 skip)". PRD 영향 파일 섹션에도 "언어·프레임워크 일반화 원칙" 추가 |
| R3 | I3 | 1a 에 **"명시적 포기 메모" 옵션** 명문화: "코드 내 방어가 불가능·부적합한 경우, PR 본문 또는 대상 클래스 JavaDoc 에 `// RACE-ACCEPTED: <이유> + <보정 메커니즘>` 근거 기록 시 7점 상한 해제. 보정 메커니즘 없는 포기 불가" |
| R4 | I5 | 1b 에 `AopContext.currentProxy()` 지양 근거 각주 추가 ("테스트 이중성·AOP 컨텍스트 누수·Spring 문서 권장 안 함") |
| R5 | I7 | 1a 패턴 표를 스택 독립 용어(락·멱등성 키·이벤트 저장·outbox)로 재작성 후 Spring 예시는 괄호 부가 (예: "락(`SELECT … FOR UPDATE` / advisory lock / Redis Redlock)") |
| R6 | — | CLAUDE.md `harness-code-review.md` 참조 주위에 1a·1b 신설 사실을 반영할 필요 없음 확인 (링크 경로 불변) — 다만 `## Harness Engineering` 테이블의 9단계 설명에 "AOP·동시성 체크리스트 포함" 1줄 보강은 임의 |

## 4. T-22 역체크 (체크리스트 보강 후 같은 회차 재실행 가정)

| Codex T-22 원본 지적 | 1a·1b 해당 항목 | 재실행 시 Claude r1 포착 가능성 |
|---------------------|----------------|----------------------------------|
| P1-01 `evaluateAll()` → `this.evaluate()` self-invocation (`@Transactional`·`@CacheEvict` 우회) | 1b 8점 질문 | **포착 가능 (High)**. 질문이 이진("같은 빈 내 `this.xxx()` 어드바이스 호출 존재?") — grep 수준 판정. 다만 `evaluateAll()` 에 어드바이스가 없어 리뷰어가 "호출자 쪽은 적용 대상 아님"으로 오판할 여지 → 1b 문구 보강 필요: "호출자 어노테이션 유무와 무관, **피호출자에 어드바이스가 있으면 FAIL**" |
| P1-02 ip_hash 집계 후 ON/OFF 판정 → 두 트랜잭션 동시 `1→2` 읽어 둘 다 OFF 분기 | 1a 패턴 표 1행 "집계 후 상태 전이" | **포착 가능 (High)**. 패턴명·예시·방어("집계 대상 row `FOR UPDATE` 또는 단일 SQL UPDATE 집계+판정") 가 T-22 와 직접 대응. Claude r1 가 이전에 놓친 이유는 "체크리스트 항목 부재" → 1a 추가로 해결 |
| P2-01 `recordSubmission()` 롤백 누수 | 1a 패턴 표 4행 "외부 API 호출 + 상태 저장"의 "afterCommit" | **부분 포착 (Med)**. 패턴명이 "외부 API" 여서 내부 counter 경로는 리뷰어가 "해당 없음" 판단할 여지. 1a 에 "in-memory counter·quota 증가 + DB 트랜잭션" 예시 1줄 추가 시 포착률 상승 |
| P3-01 인덱스 shape 불일치 | 범위 외 | 1a·1b 대상 아님 (성능 섹션 6) — 보강 대상 아님 |

**역체크 결론**: 1a·1b 가 T-22 회차 P1 2건을 **구조적으로 포착 가능한 레벨**로 체크리스트에 명문화됨. 다만 I2 (타 스택), R1 (FAIL 규칙), 표의 Spring 편중을 해소해야 **일반화된 재사용성** 확보. 현 상태는 "T-22 같은 Spring 케이스 포착은 가능하나 문서 완결성 미달" → **FAIL → 수정 후 r2 재실행 권고**.

## 5. 결론

**FAIL** (평균 7.67 / 최저 6).

차단 사유:
1. **I1/I4 (판정 규칙 불명확)** — 1b "최대 6점 고정" 과 통과 조건 "최저 ≥7" 의 상호작용이 문서화 안 됨. r2 에서 R1 반영 필수.
2. **I2 (Spring 편중)** — 타 스택 프로젝트 리뷰 시 적용 기준 부재. R2 반영 필수.

회차 처리:
- 재시도 카운트: r1 소비 (1/3).
- 다음 단계: PRD 또는 `harness-code-review.md` 수정 후 **새 서브에이전트로 r2 재실행** (같은 에이전트 셀프 재채점 금지).
- Codex `/codex:review --wait` 는 r2 PASS 이후 메인 에이전트가 집행.

Low 권고(R3·R4·R5) 는 r2 차단 요소 아님 — 동반 반영 권장.
