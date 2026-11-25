# Antigravity Rules

> 본 파일은 **Antigravity(CLI · 2.0 · IDE) 전용** 하네스 어댑터다.
> 루트 [`AGENTS.md`](./AGENTS.md)가 함께 로드될 때, **Antigravity 런타임은 본 파일의 모드·도구·경계 매핑을 우선 적용**한다.
> 모든 규칙의 원문 SSOT는 [`CLAUDE.md`](./CLAUDE.md)와 [`docs/harness-absolute-rules.md`](./docs/harness-absolute-rules.md)다.

## 역할

이 파일은 Antigravity용 하네스 어댑터다. [`CLAUDE.md`](./CLAUDE.md)를 대체하지 않고, Claude 중심 워크플로우를 Antigravity가 실행 가능한 규칙으로 번역한다.

목표:
- Antigravity 진입 시 `Antigravity-Lead`로 동일 12단계 하네스 수행 (교차 런타임 리뷰 금지 — Claude·Codex 작업의 리뷰어로 타 런타임 호출 불가)
- 문서 우선, QA, 4축 리뷰, 자동 머지 가드 유지 (리뷰 결과는 PRD·코드 본문 흡수, 별도 증거 파일·artifact 없음)
- `/rp-*` Claude 명령이나 Codex `spawn_agent` 등 타 런타임 전용 기능을 Antigravity에서 실행한 것처럼 기록하지 않음

## 기본 운영

작성 모드 SSOT: [`docs/harness-absolute-rules.md`](./docs/harness-absolute-rules.md) "작성 모드 및 리뷰 매트릭스".

| 모드 | 메인 | 서브에이전트 (단계당 재시도 포함) | 외부 추가 리뷰 |
|------|------|------------------------------|-------------|
| Claude-Lead | Claude Code | Claude Agent 툴 ([4]·[5] 3회 / [9] 5회) | **없음** — 타 런타임 호출 금지 |
| Codex-Lead | Codex CLI | Codex `spawn_agent` ([4]·[5] 3회 / [9] 5회) | **없음** — 타 런타임 호출 금지 |
| Antigravity-Lead | Antigravity | Antigravity `invoke_subagent` (`TypeName: "self"`, [4]·[5] 3회 / [9] 5회) | **없음** — 타 런타임 호출 금지 |

핵심:
- 사용자가 진입한 런타임이 메인
- **리뷰 병렬**: `[4] ∥ [5]`, `[9-코드] ∥ [9-인프라]`를 동일 턴에서 `invoke_subagent`로 동시 발사하고, 두 서브에이전트의 완료 알림을 모두 수신한 뒤 판정한다(비동기 fan-in, 컨텍스트 미공유 독립 판정). 동시 발사 불가 환경이면 **순차 fallback 허용**(판정 규칙·통과 조건 동일). 한 축만 기술 실패 시 실패 축만 새 서브에이전트로 재발사(정상 축 보존)
- **[9-인프라]**: SQL·Redis·비동기·직렬화·배포 5영역, **무점수 BLOCK/ASK/WARN** 판정, **정적 분석 전용(실인프라 접근 금지)**. SSOT: [`docs/harness-infra-review.md`](./docs/harness-infra-review.md)
- 메인 셀프 채점 절대 금지 — `[4]`·`[5]`·`[9-코드]`·`[9-인프라]`·`rp-pr-review` 모두 반드시 `invoke_subagent`(`TypeName: "self"`)로 독립 수행
- **런타임 = 리뷰어**: 교차 런타임 추가 리뷰 전면 금지 (`claude`·`codex` 호출 금지)
- 한도 미달 시 자동 중단 + 사용자 결정 요청 (강행/재설계/중단)
- 동일 변경을 나중에 다른 런타임에서 다시 열어도 기존 리뷰 대체·재채점 금지

## Antigravity 스킬 · 훅 · 워크스페이스 경계

프로젝트 로컬 Antigravity 스킬은 `.agents/skills/rp-*/SKILL.md`, 라이프사이클 훅은 `.agents/hooks.json`에 둔다.

관리 규칙:
- 원본은 `docs/skills/rp-*.md`
- 변환본은 `scripts/sync-skills.py`로 생성(`.codex/skills/`·`.agents/skills/` 동시 동기화)
- `.agents/hooks.json`(`PostToolUse` 전용)이 `docs/skills/rp-*.md` 변경 시 `.claude/commands/`·`.codex/skills/`·`.agents/skills/`를 자동 갱신한다 (`PreToolUse` 훅은 권한 정책 우회 및 실행 지연 방지를 위해 미등록)
- 수동 동기화는 `python3 scripts/sync-skills.py`, 검증은 `python3 scripts/sync-skills.py --check`
- 글로벌 스킬 설치는 `python3 scripts/sync-skills.py --target antigravity --install-user` (`~/.gemini/config/skills/` 심링크 설치, `$ANTIGRAVITY_CONFIG_DIR`로 경로 오버라이드 가능)
- **서브레포 경계**: Antigravity는 `.git` 경계까지만 상위 규칙·훅·스킬을 탐색하므로 **하네스 루트(`workflow-agent-harness/`)를 워크스페이스로 여는 것을 권장**한다. `repositories/[project]/` 단독 오픈 시 `--install-user`로 스킬을 전역 노출하고 루트 `GEMINI.md`·`CLAUDE.md`를 직접 Read한다

## 기준 문서

하네스 규칙에 영향이 있는 변경 전 아래 문서를 확인한다.

- [`CLAUDE.md`](./CLAUDE.md)
- [`docs/harness-absolute-rules.md`](./docs/harness-absolute-rules.md)
- [`docs/harness-workflow.md`](./docs/harness-workflow.md)
- [`docs/harness-prd.md`](./docs/harness-prd.md)
- [`docs/harness-dev.md`](./docs/harness-dev.md)
- [`docs/harness-qa.md`](./docs/harness-qa.md)
- [`docs/harness-code-review.md`](./docs/harness-code-review.md)
- [`docs/harness-infra-review.md`](./docs/harness-infra-review.md)
- [`docs/harness-trust-boundary.md`](./docs/harness-trust-boundary.md)
- [`docs/harness-ship.md`](./docs/harness-ship.md)

우선순위:
1. `repositories/[project]/CLAUDE.md`
2. 루트 [`CLAUDE.md`](./CLAUDE.md)
3. 본 파일(`GEMINI.md`)
4. 루트 [`AGENTS.md`](./AGENTS.md) (Codex 전용 — Antigravity에서는 본 파일 매핑 우선)

`repositories/`는 루트 git에서 제외되어 있다. 하네스 메타 변경은 레포 루트에서 수행한다.

## Antigravity 변환 규칙

Claude·Codex 요소는 Antigravity에서 아래처럼 해석한다.

| 하네스 요소 | Antigravity 해석 |
|------------|-----------------|
| `/rp-*` 슬래시 명령 | `.agents/skills/rp-*/SKILL.md` (원본: `docs/skills/rp-*.md`) |
| 리뷰 서브에이전트 | `invoke_subagent` (`TypeName: "self"`, 읽기·분석 전용 프롬프트) |
| 재리뷰 · 조건부 재검증 | 반드시 **새 `invoke_subagent`** 호출 — 부모 → 이전 리뷰어 `send_message` 재호출 금지 |
| 서브에이전트 결과 반환 | 서브에이전트 → 부모 `send_message` 텍스트 회신 필수 허용 (파일·artifact 생성 금지) |
| `[9-인프라]` 접근 제약 | 정적 분석 전용 — DB·Redis·k8s·브로커·MCP DB 도구 접근 전면 금지 |
| `swarm` · `artifact` | 리뷰에 `swarm` 사용 금지; 리뷰 결과·점수표의 artifact 파일 생성 금지(PRD·코드 본문 반영만) |
| `.claude` hooks / push 전 README 검증 | `.claude` 훅은 참고 동작; 스킬 동기화는 `.agents/hooks.json`(`PostToolUse`), push 전 README 검증은 `rp-ship` 절차 2번 수행(`PreToolUse` 미등록) |
| 단계 토큰 출력 | 진입 `python3 scripts/token-usage.py --start N` 단독 호출, 완료 시 `python3 scripts/token-usage.py` 1줄 출력 |

실제로 실행하지 않은 Claude·Codex 전용 명령은 실행했다고 기록하지 않으며, 리뷰 결과는 `Antigravity-Lead` 독립 검토로 기록한다.

## 작성 모드

### Claude-Lead Mode

Claude Code 진입 시 하네스 원문 절차를 따른다. Claude가 작성·구현하고 Claude Agent 툴(`subagent_type=general-purpose`)이 4축 리뷰를 수행한다. 타 런타임 호출 금지.

### Codex-Lead Mode

Codex CLI 진입 시 Codex가 작성·구현하고 Codex `spawn_agent` 서브에이전트가 4축 리뷰를 수행한다. 타 런타임 호출 금지.

### Antigravity-Lead Mode

Antigravity가 주 작성자이고 메인 런타임인 경우:

- **Antigravity 서브에이전트**(`invoke_subagent`, `TypeName: "self"`, 별도 컨텍스트)가 plan / engineering / code / infra review 및 `rp-pr-review` 수행 — 메인 셀프 채점 금지
- 외부 추가 리뷰 없음 · **Claude·Codex 리뷰 호출 금지** (런타임 = 리뷰어)
- 재시도 `[4]`·`[5]` 최대 3회(축별 독립) / `[9]` 최대 5회(코드+인프라 공통, 사이클 단위), 한도 미달 시 사용자 결정 요청
- 네 리뷰 축은 별도 관점·별도 판정으로 처리 — "같은 리뷰 반복"으로 해석 금지

관점 분리:
- plan review: PRD를 기획 관점으로 검토 (engineering review와 병렬)
- engineering review: PRD를 기술 관점으로 검토 (plan review와 병렬)
- code review: 구현 diff를 코드 관점으로 검토 (infra review와 병렬)
- infra review: 구현 diff를 인프라 접점 관점으로 검토 — 무점수 BLOCK/ASK/WARN, 정적 분석 전용

동일 변경을 나중에 Claude·Codex에서 다시 열어도 기존 리뷰 대체·모드 전환·재채점 금지.

## 필수 워크플로우

기능 변경 또는 메타 변경은 아래 순서를 유지한다.

1. 동작·범위·워크플로우 규칙에 영향이 있으면 PRD를 먼저 작성·수정한다.
2. Plan review와 Engineering review를 **병렬로 동시 발사**한다 (양축 통과 시 다음 단계).
3. 변경이 단순하지 않으면 task로 분해한다.
4. 구현한다.
5. 변경 성격에 맞는 테스트와 QA 증거를 남긴다.
6. Code review와 Infra review를 **병렬로 동시 발사**한다 (코드 축 점수 + 인프라 축 BLOCK 0건·미해결 ASK 0건 AND 결합). 인프라 축은 콘텐츠·메타 변경 시 정당한 skip.
7. 산출물 보고 후 `rp-ship`으로 커밋·PR·CI·자동 머지·배포를 진행한다.

하네스 메타 변경은 단축 경로를 허용한다:
- 대상: `docs/`·`CLAUDE.md`·`AGENTS.md`·`GEMINI.md`·스킬·`scripts/`·`.codex/`·`.agents/`·`.claude/settings.json`
- `init`, `specify`, `task`, `dev` 생략 가능 (feat 브랜치 작업 필수, `main` 직접 수정 금지)
- `docs/prd/[feature]/prd.md` 간소 PRD 필수 (frontmatter `**유형:** 하네스 메타 변경` + 4섹션)
- `[4] ∥ [5]` + `[8]` 메타 QA([`docs/harness-qa.md`](./docs/harness-qa.md) "하네스 메타" 행) + `[9-코드]`(인프라 축 skip) + `rp-ship`

리뷰 단계 진입 시 `invoke_subagent` 호출은 단계 자동 실행이다. 별도 사용자 확인 지점을 추가하지 않는다.
Full flow에서는 같은 런타임이라는 이유로 plan review와 engineering review를 합치지 않는다. 단, [`docs/harness-workflow.md`](./docs/harness-workflow.md) Lite 판별을 통과한 핫픽스는 SSOT 예외에 따라 통합 plan/engineering 리뷰 1회를 적용한다.

## 리뷰 산출물

진입 런타임 서브에이전트의 리뷰 결과는 **PRD·코드 본문에 반영**한다. 별도 증거 파일(`review-claude-*.md`, `review-codex-*.md`)이나 artifact 파일을 작성·저장하지 않는다.

- 리뷰 지적은 `send_message` 텍스트로만 메인 에이전트에 전달
- 모든 심각도 지적은 PRD(또는 코드) 본문 갱신으로만 흔적을 남김 (심각도 기준: [`docs/harness-code-review.md`](./docs/harness-code-review.md) "지적 심각도")
- 회차 추적 파일·점수표 보존·원문 저장 모두 폐기

## 리뷰 기준

사용자가 리뷰를 요청하면:
- findings를 먼저 제시하고 심각도순 정렬
- 파일 경로와 근거 포함
- 버그, 워크플로우 회귀, 누락된 게이트, 문서 간 모순을 우선 검토
- 요약은 짧게 유지

Code review는 [`docs/harness-code-review.md`](./docs/harness-code-review.md)를 따른다.
Meta 또는 PRD review는 관련 하네스 문서를 기준으로 교차 정합성을 확인한다.

`Antigravity-Lead` 리뷰 결과에는 독립성을 명시한다:
- 리뷰 단계명을 상단에 기록
- 해당 단계의 관심사만 평가
- 이전 작성 결정을 방어하지 않고 재검토
- 다음 단계 진행을 막아야 하는 finding을 명확히 표시

## 절대 규칙

아래는 예외 없이 지킨다 (하네스 자체 변경도 메타 단축 경로로만 진행 — SSOT [`docs/harness-absolute-rules.md`](./docs/harness-absolute-rules.md)).

- 동작 변경은 문서 우선
- QA·code review·infra review는 생략 불가 (인프라 축 정당한 skip 제외, 테스트 통과를 QA 대체로 기록 금지)
- 모든 심각도 finding은 다음 단계 전 반영 (PRD·코드 본문에 흡수). 단 `[9]` 재시도 한도 소진 회차의 Low는 미처리 후 진행, 산출물 보고에 표로 기록
- 리뷰 결과는 별도 증거 파일·artifact가 아닌 PRD·코드 본문 자체에 반영
- `main` 직접 수정 금지 · 수동 `git`/`gh`로 `rp-ship` 우회 금지
- CI 동기 검증 전 `gh pr merge` 호출 및 `--auto`/`--admin`/`--no-verify` 전면 금지
- 실제 수행하지 않은 CI, PR, deploy, ship 단계를 완료로 기록 금지
- DB `DROP`·`DELETE FROM`·`TRUNCATE` 실행 금지 → [`docs/harness-absolute-rules.md`](./docs/harness-absolute-rules.md) §DB 파괴적 작업 금지
- 인프라 재기동(colima·k3s·노드 reboot 등) 무허가 실행 금지
- auto-memory 시스템 사용 금지
- 민감 정보 기재 및 하네스 문서 내 서브레포 내부 파일 직접 링크 금지

## 응답 언어

한국어 기반으로 답변한다. 기술 용어·코드·고유명사는 원어 유지.

## 질문 절차

[`CLAUDE.md`](./CLAUDE.md) "Interaction"을 따른다 — **추론 우선**(유추 가능 항목은 가정 통지, 유추 불가 결정만 질문, 최소 개수 없음), 1개씩 대화형, 객관식 4개 + 추천 점수(**0.5점 단위**, 임계값·자동 선택·요청 상충 감점·정렬 예외는 [`CLAUDE.md`](./CLAUDE.md) SSOT), 주관식은 마지막 번호.

## 문서 스타일

하네스 문서 수정 시:
- 간결하고 실행 가능한 문장 사용 (표와 짧은 리스트 우선)
- 파일당 500줄 이하 유지, 초과 시 책임 단위로 분리
- 수치·임계값·세부 채점표는 SSOT 링크 참조 유지(중복 하드코딩 금지)
- `GEMINI.md` 내 Antigravity `@` 파일 인클루드 문법 금지(일반 마크다운 상대 링크만 사용)
- 하네스 규칙·스킬 변경 시 `CLAUDE.md`·`AGENTS.md`·`GEMINI.md` 및 3런타임 스킬 동기화 정합성 유지
- 민감 정보, 개인 식별 정보, 실제 시크릿 금지

## 기본 판단

사용자가 "Antigravity도 이 레포를 쓸 수 있나"라고 묻는 경우:
- 메인 런타임 선택 시점에 작성 모드 결정 (Claude Code → Claude-Lead / Codex CLI → Codex-Lead / Antigravity → Antigravity-Lead)
- 세 런타임 모두 동일 12단계 워크플로우·동일 게이트·동일 SSOT 규칙 적용
- 차이는 채점 서브에이전트 도구뿐 — 세 런타임 모두 외부 추가 리뷰 없음

사용자가 Claude·Codex 없이 Antigravity로 진행하라고 하면:
- Antigravity가 변경 작성, `invoke_subagent`(`TypeName: "self"`)가 plan / engineering / code / infra 네 관점으로 분리 채점
- 메인 셀프 채점 절대 금지 — 모든 채점은 독립 서브에이전트가 수행
- 재시도 `[4]`·`[5]` 최대 3회(축별 독립) / `[9]` 최대 5회(코드+인프라 공통, 사이클 단위), 한도 미달 시 사용자 결정 요청
