# Antigravity Rules

> 본 파일은 **Antigravity(CLI · 2.0 · IDE)** 용 경량 하네스 어댑터다.
> 루트 [`AGENTS.md`](./AGENTS.md)가 함께 로드될 때, **Antigravity 런타임은 본 파일의 모드·도구·경계 매핑을 우선 적용**한다.
> 모든 규칙의 원문 SSOT는 [`CLAUDE.md`](./CLAUDE.md)와 [`docs/harness-absolute-rules.md`](./docs/harness-absolute-rules.md)다.

## 작성 모드 (`Antigravity-Lead`)

- **진입 런타임 = 메인 · 리뷰어**: Antigravity 진입 시 `Antigravity-Lead` 모드로 동일 12단계 워크플로우·4축 리뷰·자동 머지 가드를 수행한다.
- **메인 셀프 채점 절대 금지**: `[4]`·`[5]`·`[9-코드]`·`[9-인프라]`·`rp-pr-review`는 반드시 `invoke_subagent`(`TypeName: "self"`, 별도 컨텍스트)로 독립 수행한다.
- **교차 런타임 리뷰 금지**: `Antigravity-Lead`에서 Claude(`claude`) 또는 Codex(`codex`) 호출 금지. 동일 변경을 타 런타임에서 다시 열어도 기존 리뷰 대체·재채점 금지.
- **리뷰 병렬 실행**: `[4] ∥ [5]`, `[9-코드] ∥ [9-인프라]`를 동일 턴에서 `invoke_subagent`로 동시 발사하고, 두 서브에이전트의 완료 알림을 모두 수신한 뒤 판정한다(비동기 fan-in). 동시 발사 불가 환경이면 순차 fallback 허용(통과 조건 동일). 한 축만 기술 실패 시 실패 축만 새 서브에이전트로 재발사(정상 축 보존).

## 도구 · 계약 매핑

| 하네스 요소 | Antigravity 해석 |
|------------|-----------------|
| `/rp-*` 슬래시 명령 | `.agents/skills/rp-*/SKILL.md` (원본: `docs/skills/rp-*.md`) |
| 리뷰 서브에이전트 | `invoke_subagent` (`TypeName: "self"`, 읽기·분석 전용 프롬프트) |
| 재리뷰 · 조건부 재검증 | 반드시 **새 `invoke_subagent`** 호출 — 부모 → 이전 리뷰어 `send_message` 재호출 금지 |
| 서브에이전트 결과 반환 | 서브에이전트 → 부모 `send_message` 텍스트 회신 필수 허용 (파일·artifact 생성 금지) |
| `[9-인프라]` 접근 제약 | 정적 분석 전용 — DB·Redis·k8s·브로커·MCP DB 도구 접근 전면 금지 |
| `swarm` · `artifact` | 리뷰에 `swarm` 사용 금지; 리뷰 결과·점수표의 artifact 파일 생성 금지(PRD·코드 본문 반영만) |
| push 전 README 검증 | `rp-ship` 절차 2번으로 수행 (`PreToolUse` 훅 미등록) |
| 단계 토큰 출력 | 진입 `python3 scripts/token-usage.py --start N` 단독 호출, 완료 시 `python3 scripts/token-usage.py` 1줄 출력 |

## 스킬 · 훅 · 워크스페이스 경계

- **스킬 동기화**: 원본 `docs/skills/rp-*.md` 수정 시 `.agents/hooks.json`(`PostToolUse`)이 `.claude/commands/`·`.codex/skills/`·`.agents/skills/`를 자동 갱신한다. 수동 동기화는 `python3 scripts/sync-skills.py`, 검증은 `python3 scripts/sync-skills.py --check`.
- **글로벌 스킬 설치**: `python3 scripts/sync-skills.py --target antigravity --install-user` (`~/.gemini/config/skills/` 심링크 설치, `$ANTIGRAVITY_CONFIG_DIR`로 경로 오버라이드 가능).
- **서브레포 경계**: Antigravity는 `.git` 경계까지만 상위 규칙·훅·스킬을 탐색하므로 **하네스 루트(`workflow-agent-harness/`)를 워크스페이스로 여는 것을 권장**한다. `repositories/[project]/` 단독 오픈 시 `--install-user`로 스킬을 전역 노출하고 루트 `GEMINI.md`·`CLAUDE.md`를 직접 Read한다.
- **우선순위**: `repositories/[project]/CLAUDE.md` > 루트 [`CLAUDE.md`](./CLAUDE.md) > 본 파일(`GEMINI.md`).

## 절대 규칙 · 상호작용 요약

- **응답 언어**: 한국어 기반(기술 용어·코드·고유명사 원어 유지).
- **질문 절차**: [`CLAUDE.md`](./CLAUDE.md) "Interaction" 그대로 적용 — 추론 우선(가정 통지), 유추 불가 결정만 1개씩 객관식 4개 + 0.5점 단위 점수 + 자동 선택(임계값·예외는 [`CLAUDE.md`](./CLAUDE.md) SSOT).
- **예외 없는 금지**: 동작 변경 문서 우선 · QA/리뷰 생략 금지 · `main` 직접 수정 금지 · CI 동기 검증 전 `gh pr merge` 및 `--auto`/`--admin`/`--no-verify` 금지 · DB `DROP`/`DELETE FROM`/`TRUNCATE` 금지 · 인프라 재기동 무허가 실행 금지 · auto-memory 사용 금지 · 민감 정보 및 서브레포 직접 링크 금지. 상세 SSOT: [`docs/harness-absolute-rules.md`](./docs/harness-absolute-rules.md).
- **하네스 메타 단축 경로**: `docs/`·`CLAUDE.md`·`AGENTS.md`·`GEMINI.md`·스킬·`scripts/`·`.codex/`·`.agents/`·`.claude/settings.json` 변경 시 간소 PRD + `[4]∥[5]` + `[8]` 메타 QA + `[9-코드]`(인프라 skip) + `rp-ship`.
