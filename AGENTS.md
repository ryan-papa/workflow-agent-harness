# Codex Rules

## 역할

이 파일은 Codex용 하네스 어댑터다. [`CLAUDE.md`](./CLAUDE.md)를 대체하지 않고, Claude 중심 워크플로우를 Codex가 실행 가능한 규칙으로 번역한다.

목표:
- Claude 중심 하네스에서 Codex를 보조 구현자·독립 리뷰어로 사용
- 문서 우선, QA, 코드리뷰 게이트 유지 (리뷰 결과는 PRD 본문 흡수, 별도 증거 파일 없음)
- `/rp-*`, `.claude` hook 등 Claude 전용 기능을 Codex에서 실행한 것처럼 기록하지 않음

## 기본 운영

작성 모드 SSOT: [`docs/harness-absolute-rules.md`](./docs/harness-absolute-rules.md) "작성 모드 및 리뷰 매트릭스".

| 모드 | 메인 | 서브에이전트 (단계당 재시도 포함) | 외부 추가 리뷰 |
|------|------|------------------------------|-------------|
| Claude-Lead | Claude Code | Claude 서브에이전트 ([4]·[5] 3회 / [9] 5회) | **없음** — Codex 호출 금지 |
| Codex-Lead | Codex CLI | Codex `spawn_agent` 서브에이전트 ([4]·[5] 3회 / [9] 5회) | **없음** — Claude 리뷰 금지 |

핵심:
- 사용자가 진입한 런타임이 메인
- **리뷰 병렬**: `[4] ∥ [5]`, `[9-코드] ∥ [9-인프라]` 동시 발사 (컨텍스트 미공유 독립 판정). Codex-Lead 는 `spawn_agent` 동시 발사 불가 시 **순차 fallback 허용** — 판정 규칙·통과 조건 동일, 병렬 여부는 통과 조건 아님
- **[9-인프라]**: SQL·Redis·비동기·직렬화·배포 5영역, **무점수 BLOCK/ASK/WARN** 판정, **정적 분석 전용(실인프라 접근 금지)**. SSOT: [`docs/harness-infra-review.md`](./docs/harness-infra-review.md)
- 메인 셀프 채점 절대 금지 — 모든 채점은 해당 런타임의 서브에이전트가 수행
- **런타임 = 리뷰어**: 교차 런타임 추가 리뷰 전면 금지 (Claude-Lead 에서 Codex 호출 금지, Codex-Lead 에서 Claude 호출 금지)
- 한도 미달 시 자동 중단 + 사용자 결정 요청 (강행/재설계/중단)
- 동일 변경을 나중에 다른 런타임에서 다시 열어도 기존 리뷰 대체 금지 — 추가 독립 검토로만 기록

## Codex 스킬

프로젝트 로컬 Codex 스킬은 `.codex/skills/rp-*/SKILL.md`에 둔다.

관리 규칙:
- 원본은 `docs/skills/rp-*.md`
- 변환본은 `scripts/sync-codex-skills.py`로 생성
- Claude hook은 `docs/skills/rp-*.md` 변경 시 `.claude/commands/`와 `.codex/skills/`를 함께 갱신
- Codex에서 직접 수정했다면 `python3 scripts/sync-codex-skills.py --check`로 동기화 확인
- 로컬 Codex discovery가 필요하면 `python3 scripts/sync-codex-skills.py --install-user`로 `$CODEX_HOME/skills`에 심링크 설치

## 기준 문서

하네스 규칙에 영향이 있는 변경 전 아래 문서를 확인한다.

- [`CLAUDE.md`](./CLAUDE.md)
- [`docs/harness-workflow.md`](./docs/harness-workflow.md)
- [`docs/harness-prd.md`](./docs/harness-prd.md)
- [`docs/harness-dev.md`](./docs/harness-dev.md)
- [`docs/harness-code-review.md`](./docs/harness-code-review.md)
- [`docs/harness-infra-review.md`](./docs/harness-infra-review.md)
- [`docs/harness-trust-boundary.md`](./docs/harness-trust-boundary.md)
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

실제로 실행하지 않은 Claude 전용 명령은 실행했다고 기록하지 않는다.

Codex도 `spawn_agent` 기반 서브에이전트 실행은 가능하다. 단, Claude Agent tool과 동일한 hook·slash command 런타임은 아니므로 결과는 Codex-Lead 독립 검토로 기록한다.

## 작성 모드

### Claude-Lead Mode

하네스 원문 절차를 그대로 따른다.

- Claude가 작성·구현
- **Claude 서브에이전트**(Agent 툴, `subagent_type=general-purpose`)가 plan / engineering / code / infra review 수행 — 메인 셀프 채점 금지
- 외부 추가 리뷰 없음 — `codex` 명령·`/codex:*` 호출 금지
- 재시도 [4]·[5] 최대 3회(축별 독립) / [9] 최대 5회(코드+인프라 공통, 사이클 단위), 한도 미달 시 사용자 결정 요청

### Codex-Lead Mode

Codex가 주 작성자이고 메인 런타임이 Codex CLI인 경우:

- **Codex 서브에이전트**(`spawn_agent` 별도 컨텍스트)가 plan / engineering / code / infra review 수행 — 메인 셀프 채점 금지
- 외부 추가 리뷰 없음 · **Claude 리뷰 호출 금지** (런타임 = 리뷰어)
- 재시도 [4]·[5] 최대 3회(축별 독립) / [9] 최대 5회(코드+인프라 공통, 사이클 단위), 한도 미달 시 사용자 결정 요청
- 네 리뷰 축은 별도 관점·별도 판정으로 처리 — "같은 리뷰 반복"으로 해석 금지

관점 분리:
- plan review: PRD를 기획 관점으로 검토 (engineering review와 병렬)
- engineering review: PRD를 기술 관점으로 검토 (plan review와 병렬)
- code review: 구현 diff를 코드 관점으로 검토 (infra review와 병렬)
- infra review: 구현 diff를 인프라 접점 관점으로 검토 — 무점수 BLOCK/ASK/WARN, 정적 분석 전용

동일 변경을 나중에 Claude에서 다시 열면 Claude 리뷰는 기존 증거 대체가 아니라 추가 독립 검토로 기록한다 — 모드 전환·재채점 금지.

## 필수 워크플로우

기능 변경 또는 메타 변경은 아래 순서를 유지한다.

1. 동작·범위·워크플로우 규칙에 영향이 있으면 PRD를 먼저 작성·수정한다.
2. Plan review와 Engineering review를 **병렬로 동시 발사**한다 (양축 통과 시 다음 단계).
3. 변경이 단순하지 않으면 task로 분해한다.
4. 구현한다.
5. 변경 성격에 맞는 테스트와 QA 증거를 남긴다.
6. Code review와 Infra review를 **병렬로 동시 발사**한다 (코드 축 점수 + 인프라 축 BLOCK 0건·미해결 ASK 0건 AND 결합). 인프라 축은 콘텐츠·메타 변경 시 정당한 skip.
7. Ship 관련 작업 전에 결과를 보고한다.

하네스 메타 변경은 단축 경로를 허용한다.
- `init`, `specify`, `task`, `dev` 생략 가능
- `docs/prd/[feature]/prd.md` 간소 PRD 필수 (frontmatter `**유형:** 하네스 메타 변경` + 4섹션)
- 리뷰 결과는 PRD 본문에 반영, 별도 증거 파일 생성 금지

Codex-Lead Mode에서도 단계 구조를 유지한다.
- PRD update
- plan review ∥ engineering review (병렬)
- implementation
- QA / verification
- code review ∥ infra review (병렬)

리뷰 단계 진입 시 `spawn_agent` 서브에이전트 호출은 단계 자동 실행이다. 별도 사용자 확인 지점을 추가하지 않는다.

Full flow에서는 같은 모델만 사용 가능하다는 이유로 plan review와 engineering review를 합치지 않는다. 단, [`docs/harness-workflow.md`](./docs/harness-workflow.md) Lite 판별을 통과한 핫픽스는 SSOT 예외에 따라 통합 plan/engineering 리뷰 1회를 적용한다.

## 리뷰 산출물

진입 런타임 서브에이전트의 리뷰 결과는 **PRD 본문에 반영**한다. 별도 증거 파일(`review-claude-*.md`, `review-codex-*.md`)을 작성·저장하지 않는다.

- 리뷰 지적은 응답 텍스트로만 메인 에이전트에 전달
- High/Critical 지적은 PRD(또는 코드) 본문 갱신으로만 흔적을 남김
- 회차 추적·점수표 보존·Codex 원문 저장 모두 폐기

Codex-Lead Full flow에서도 plan/eng/code/infra 네 리뷰 축은 서로 다른 관점의 판정임을 유지하되, 산출물은 PRD 또는 코드 본문 갱신 자체로 흡수된다. Lite는 SSOT 통합 plan/engineering 리뷰 예외를 따른다.

## 리뷰 기준

사용자가 리뷰를 요청하면:
- findings를 먼저 제시하고 심각도순 정렬
- 파일 경로와 근거 포함
- 버그, 워크플로우 회귀, 누락된 게이트, 문서 간 모순을 우선 검토
- 요약은 짧게 유지

Code review는 [`docs/harness-code-review.md`](./docs/harness-code-review.md)를 따른다.
Meta 또는 PRD review는 관련 하네스 문서를 기준으로 교차 정합성을 확인한다.

Codex-Lead Mode의 리뷰 결과에는 독립성을 명시한다.
- 리뷰 단계명을 상단에 기록
- 해당 단계의 관심사만 평가
- 이전 작성 결정을 방어하지 않고 재검토
- 다음 단계 진행을 막아야 하는 finding을 명확히 표시

## 절대 규칙

사용자가 하네스 자체 변경을 명시적으로 요청하지 않는 한 아래를 우회하지 않는다.

- 동작 변경은 문서 우선
- QA와 code review는 생략 불가
- High/Critical finding은 다음 단계 전 반영 (PRD/코드 본문에 흡수)
- 리뷰 결과는 별도 증거 파일이 아닌 PRD 본문 자체에 반영
- 테스트 통과를 QA 대체로 기록하지 않음
- 실제 수행하지 않은 CI, PR, deploy, ship 단계를 완료로 기록하지 않음
- "리뷰 3"을 같은 관점의 반복 채점으로 재정의하지 않음

## 문서 스타일

하네스 문서 수정 시:
- 간결하고 실행 가능한 문장 사용
- 표와 짧은 리스트 우선
- 파일당 500줄 이하 유지
- 책임 단위로 분리
- 민감 정보, 개인 식별 정보, 실제 시크릿 금지

## 기본 판단

사용자가 "Codex도 이 레포를 쓸 수 있나"라고 묻는 경우:
- 메인 런타임 선택 시점에 작성 모드 결정 (Claude Code → Claude-Lead / Codex CLI → Codex-Lead)
- 양쪽 모두 동일 12단계 워크플로우·동일 게이트·동일 SSOT 규칙 적용
- 차이는 채점 서브에이전트 종류뿐 — 양쪽 모두 외부 추가 리뷰 없음

사용자가 Claude 없이 Codex로 진행하라고 하면:
- Codex가 변경 작성, Codex 서브에이전트가 plan / engineering / code / infra 네 관점으로 분리 채점
- 메인 셀프 채점 절대 금지 — 모든 채점은 `spawn_agent` 서브에이전트가 수행
- 재시도 [4]·[5] 최대 3회(축별 독립) / [9] 최대 5회(코드+인프라 공통, 사이클 단위), 한도 미달 시 사용자 결정 요청
- 추후 Claude 리뷰는 동일 변경의 재채점이 아닌 추가 독립 검토로만 기록
