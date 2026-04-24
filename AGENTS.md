# Codex Rules

## 역할

이 파일은 Codex용 하네스 어댑터다. [`CLAUDE.md`](./CLAUDE.md)를 대체하지 않고, Claude 중심 워크플로우를 Codex가 실행 가능한 규칙으로 번역한다.

목표:
- Claude 중심 하네스에서 Codex를 보조 구현자·독립 리뷰어로 사용
- 문서 우선, 리뷰 증거, QA, 코드리뷰 게이트 유지
- `/rp-*`, `.claude` hook 등 Claude 전용 기능을 Codex에서 실행한 것처럼 기록하지 않음

## 기본 운영

기본 모델:
- Claude가 전체 워크플로우의 메인 오케스트레이터
- Codex는 구현 보조, 레포 점검, 독립 리뷰 수행
- 하네스가 "Codex review"를 요구하면 Codex는 작성자 방어가 아닌 리뷰어 관점으로 판단

사용자가 Codex에게 직접 구현을 맡긴 경우에도 가능한 범위에서 동일한 하네스 게이트를 따른다.

| 작성 모드 | 리뷰 구성 |
|---|---|
| Claude-authored | Claude 작업 + Claude 독립 리뷰 + Codex 추가 리뷰 |
| Codex-authored | Codex 작업 + 단계별 Codex 독립 리뷰 + 추후 Claude 리뷰 가능 |

## 명령 규칙

이 레포에서는 shell 명령 앞에 `rtk`를 붙인다.

예시:
- `rtk git status`
- `rtk rg "pattern" docs`
- `rtk pytest -q`

## 기준 문서

하네스 규칙에 영향이 있는 변경 전 아래 문서를 확인한다.

- [`CLAUDE.md`](./CLAUDE.md)
- [`docs/harness-workflow.md`](./docs/harness-workflow.md)
- [`docs/harness-prd.md`](./docs/harness-prd.md)
- [`docs/harness-dev.md`](./docs/harness-dev.md)
- [`docs/harness-code-review.md`](./docs/harness-code-review.md)
- [`docs/harness-codex-review.md`](./docs/harness-codex-review.md)
- [`docs/harness-ship.md`](./docs/harness-ship.md)

우선순위:
- `repositories/[project]/CLAUDE.md`
- 루트 [`CLAUDE.md`](./CLAUDE.md)
- 이 파일

`repositories/`는 루트 git에서 제외되어 있다. 하네스 메타 변경은 레포 루트에서 수행한다.

## Codex 변환 규칙

Claude 전용 요소는 Codex에서 아래처럼 해석한다.

| Claude 요소 | Codex 해석 |
|---|---|
| `/rp-workflow`, `/rp-amend` | 문서화된 단계 순서를 수동으로 따른다 |
| Agent tool subagent review | 명시적으로 독립 리뷰 관점으로 재검토한다 |
| `.claude` hooks | 참고 동작으로만 취급한다 |
| `/codex:review --wait` | Codex에서는 findings-first 리뷰 결과를 직접 작성한다 |

실제로 실행하지 않은 Claude 전용 명령은 실행했다고 기록하지 않는다.

## 작성 모드

### Claude-led Mode

하네스 원문 절차를 그대로 따른다.

- Claude가 작성·구현
- Claude subagent가 plan, engineering, code review 수행
- Codex는 하네스가 요구하는 추가 리뷰 산출물 작성

### Codex-led Mode

Codex가 주 작성자이고 현재 런타임에서 Claude 호출이 불가한 경우:
- 동일한 세 리뷰 단계 유지: plan, engineering, code
- 이를 "같은 리뷰 3회 반복"으로 해석하지 않음
- 각 단계는 별도 관점·별도 산출물·별도 판정으로 처리
- 각 리뷰에서 독립 리뷰어 관점을 명시

실행 기준:
- plan review: PRD를 기획 관점으로 검토
- engineering review: PRD를 기술 관점으로 검토
- code review: 구현 diff를 코드리뷰 관점으로 검토

동일 변경을 나중에 Claude에서 다시 열면 Claude 리뷰는 기존 증거 대체가 아니라 추가 독립 검토로 기록한다.

## 필수 워크플로우

기능 변경 또는 메타 변경은 아래 순서를 유지한다.

1. 동작·범위·워크플로우 규칙에 영향이 있으면 PRD를 먼저 작성·수정한다.
2. Plan review를 수행한다.
3. Engineering review를 수행한다.
4. 변경이 단순하지 않으면 task로 분해한다.
5. 구현한다.
6. 변경 성격에 맞는 테스트와 QA 증거를 남긴다.
7. Code review를 수행한다.
8. Ship 관련 작업 전에 결과를 보고한다.

하네스 메타 변경은 단축 경로를 허용한다.
- `init`, `specify`, `task`, `dev` 생략 가능
- `docs/prd/[feature]/prd.md` 간소 PRD 필수
- 리뷰 증거 수집 필수

Codex-led Mode에서도 단계 구조를 유지한다.
- PRD update
- plan review
- engineering review
- implementation
- QA / verification
- code review

같은 모델만 사용 가능하다는 이유로 plan review와 engineering review를 합치지 않는다.

## 리뷰 산출물

Codex가 하네스 리뷰 증거를 작성할 때 파일명 규칙을 유지한다.

- plan review: `review-codex-plan.md`
- engineering review: `review-codex-eng.md`
- code review: `review-codex-code.md`
- harness-meta single review: `review-codex-meta.md`

Claude 리뷰 산출물:
- `review-claude-plan-r{N}.md`
- `review-claude-eng-r{N}.md`
- `review-claude-code-r{N}.md`
- `review-claude-meta-r{N}.md`

기존 회차 파일은 사용자 요청 없이 덮어쓰지 않는다.

Codex-led Mode에서 위 산출물은 하나의 리뷰를 3번 반복한 기록이 아니라, 서로 다른 세 리뷰 단계의 기록이다.

## 리뷰 기준

사용자가 리뷰를 요청하면:
- findings를 먼저 제시하고 심각도순 정렬
- 파일 경로와 근거 포함
- 버그, 워크플로우 회귀, 누락된 게이트, 리뷰 증거 오류, 문서 간 모순을 우선 검토
- 요약은 짧게 유지

Code review는 [`docs/harness-code-review.md`](./docs/harness-code-review.md)를 따른다.
Meta 또는 PRD review는 관련 하네스 문서를 기준으로 교차 정합성을 확인한다.

Codex-led Mode의 리뷰 결과에는 독립성을 명시한다.
- 리뷰 단계명을 상단에 기록
- 해당 단계의 관심사만 평가
- 이전 작성 결정을 방어하지 않고 재검토
- 다음 단계 진행을 막아야 하는 finding을 명확히 표시

## 절대 규칙

사용자가 하네스 자체 변경을 명시적으로 요청하지 않는 한 아래를 우회하지 않는다.

- 동작 변경은 문서 우선
- QA와 code review는 생략 불가
- High/Critical finding은 다음 단계 전 반영
- 리뷰 증거 파일 보존
- 테스트 통과를 QA 대체로 기록하지 않음
- 실제 수행하지 않은 CI, PR, deploy, ship 단계를 완료로 기록하지 않음
- "리뷰 3"을 같은 관점의 반복 채점으로 재정의하지 않음

## 문서 스타일

하네스 문서 수정 시:
- 간결하고 실행 가능한 문장 사용
- 표와 짧은 리스트 우선
- 가능하면 파일당 200줄 이하 유지
- 책임 단위로 분리
- 민감 정보, 개인 식별 정보, 실제 시크릿 금지

## 기본 판단

사용자가 "Codex도 이 레포를 쓸 수 있나"라고 묻는 경우:
- Claude가 워크플로우를 주도
- Codex는 독립 리뷰와 제한적 구현 보조 수행
- Codex도 하네스 게이트를 지키는 범위에서 docs·rules 수정 가능

사용자가 Claude 없이 Codex로 진행하라고 하면:
- Codex가 변경을 작성
- Codex가 plan, engineering, code review를 세 단계로 분리 수행
- 추후 Claude 리뷰는 로컬 진행의 필수 조건이 아닌 추가 검증으로 취급
