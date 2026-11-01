# PRD: 단계별 토큰 출력 · 질문 자동 선택 · [4]·[5] 변경 중심 · rp-pr-review 이관

**상태:** Approved ([4] 2회차 8.33 · [5] 2회차 8.3 → 재검증 8.4 · [9-코드] 8.36)
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

| # | 문제 | 근거 |
|:-:|------|------|
| 1 | 단계별 토큰 사용량을 알 수 없어 비용 분석 불가 | 사용자 요청 — 전체 사이클 후 재분석 예정. 본 세션 리뷰 1회 5.7만~6.8만 토큰이나 단계 합계 미상 |
| 2 | 답이 사실상 정해진 질문(추천 점수 압도적)도 응답 대기 → 왕복 낭비 | 사용자 요청 |
| 3 | [4]·[5]가 기존 PRD 개정·기능 변경에도 PRD 전체를 채점 → 변경과 무관한 지적·토큰 소모 | 사용자 요청 ([9]는 이미 diff 중심). 선례: PR #72 [5] 회차마다 다른 지적 (`harness-rereview-scope` PRD) |
| 4 | `rp-pr-review` 가 외부 플러그인 레포에만 있어 하네스 [11]과 연동 불가 | 사용자 요청 |

## 결정 사항

| # | 항목 | 결정 | 기각 대안 | 근거 유형 |
|:-:|------|------|-----------|-----------|
| 1 | 토큰 기록 방식 | **단계 완료마다 `✓ [N]` 다음 줄에 1줄 출력만** (파일 저장 없음). 형식 `토큰 [N]: in X · out Y · cache_r Z · cache_w W`. 값은 `scripts/token-usage.py` 출력 그대로 — 추정치 출력 금지, 실패 시 `토큰: 집계 실패 — <사유 코드>` | 레포 원장 JSONL · 로컬 원장 · PRD 표 · PR 본문 | 사용자 결정 |
| 1-1 | 집계 경계 | 단계 진입 시 **`python3 scripts/token-usage.py --start N` 호출 의무** — 그 tool 호출(Claude `tool_use.input.command` / Codex `function_call.arguments.cmd`)의 timestamp 가 경계. 명령 시작·`&&`·`;` 뒤 + 라벨 `[0-9][0-9A-Za-z.-]*` 만 인정(인용 오탐 배제. heredoc·여러 줄 본문의 줄 시작 매치는 미배제 — 저확률 수용), 0건이면 `경계 없음` 실패. 병렬 2축은 경계 1개. **개정 근거(실측)**: assistant text 블록 일부가 transcript 에 미기록 → 텍스트 마커 `▶ [N]` 방식 기각 | 텍스트 마커 `▶ [N]` (실측 누락으로 기각) · 부모 tool_use 연결 | 엔지니어 선호 |
| 1-2 | 집계 대상 (Claude) | 세션 = `$CLAUDE_CODE_SESSION_ID` → `~/.claude/projects/*/<id>.jsonl` + `<id>/subagents/*.jsonl`. 메인·서브에이전트 **모두 `message.id` 단위 1회 집계**(usage 0 행 무시), 경계 timestamp 이후 assistant 행만. 환경변수 부재 시 `세션 식별 불가` 실패 | 최신 수정 파일 선택 | 엔지니어 선호 |
| 1-3 | 집계 대상 (Codex) | `~/.codex/sessions` 에서 `session_meta.cwd` = 현재 cwd 인 최신 rollout. 경계는 `response_item` `function_call` 의 `cmd` 에서 찾고, `token_count.total_token_usage` 의 경계 전후 차분. 동일 cwd 병행 세션은 미지원(가정). **메인만** 집계 → 출력에 `(메인만)` 표기, cache_r = `cached_input_tokens`, cache_w = `n/a` | 자식 rollout(parent_thread_id) 합산 — 사용자 "간단하게" 지시로 기각 | 사용자 결정 |
| 1-4 | 출력 보안·회귀 | 출력은 단계·수치·실패 사유 코드만 (transcript 본문·경로 금지). 스크립트 `--self-test`(내장 픽스처: 중복 id·0 usage·경계 이전 서브에이전트·user 메시지·grep 인용·문자열 내 `&&` 오탐·`&&` 뒤 정상 호출) 로 회귀 검증 | 별도 픽스처 파일·CI 편입 | 엔지니어 선호 |
| 2 | 질문 점수 | **0.5점 단위**. 1위 ≥ 9.5 **+ 단독 1위**면 질문 생략·자동 선택, `Qn 자동 선택(점수): <선택지>` 1줄 통지(응답 대기 없음, 사용자 정정 시 반영). PRD 에 `자동 선택(점수):` 접두 표기 | 공동 1위도 자동 선택 · 통지 생략 | 사용자 결정 (공동 1위 = 엔지니어 선호) |
| 2-1 | 적용 범위·구분 | **전역 Interaction 규칙**(CLAUDE.md) — rp-specify·Lite 질문·기타 모든 객관식 질문. 구분: `가정:` = 질문 미생성(추론), `자동 선택(점수):` = 질문 생성 후 고득점으로 생략 | rp-specify 한정 | 엔지니어 선호 |
| 3 | [4]·[5] 범위 | **변경 중심 최초 리뷰**. 변경분 = 리뷰 스킬(`rp-plan-review`·`rp-eng-review` 프롬프트 (a))이 주입하는 **base 대비 PRD diff**(신규 파일이면 PRD 전체) + **영향 범위 목록**(Full = 변경이 의존하는 기존 PRD 섹션·코드 경로 / 간소 = 영향 파일 표 행). 변경 무관 영역은 "통과 기준을 막는 중대 결함(해당 항목 7 미만)"만 지적, 변경이 건드리지 않은 측면은 기존 상태를 이유로 감점 금지. 표현은 기존 "재리뷰 범위" SSOT 와 통일 | 범위 제한 없이 정보만 제공 | 제품 가설 ([9] diff 중심 대칭) |
| 4 | rp-pr-review 이관 | `docs/skills/rp-pr-review.md` 로 이관(하네스 frontmatter·심링크·`.codex` 동기화), 스킬-단독 운영 6종에 추가. 본문 규칙(독립 서브에이전트 1인·10분·파일/PR 쓰기 금지)은 원본 유지 | 플러그인 유지 + 참조 | 사용자 결정 |
| 4-1 | 호출 시점·처리 | `rp-ship` 이 **신규 PR 생성 직후 1회만** 하네스 사본(`docs/skills/rp-pr-review.md`)을 호출, `gh pr create` 반환 URL 을 인자로 전달(질문 없음). 리뷰어를 백그라운드 발사 후 컨플릭트 가드·CI watch 진행과 병행, **결과는 머지 판정 전 출력** — 머지는 리뷰어 종료를 기다리며 최대 지연 = 원본 10분 타임아웃. 타임아웃·실패는 1줄 기록 후 계속. 재사용 PR·재푸시 미호출. **결과는 출력만** — 반영·머지 중단·게이트 영향 없음, 통과 근거 기록 금지 | Critical·High 반영 · 머지 중단 · 동기 실행 | 사용자 결정 (병행 = 엔지니어 선호) |
| 4-2 | 원본 공존 | extensions 레포 원본 삭제는 타 레포 변경 → 본 PR 후 별도 확인. 공존 기간 혼동 방지로 하네스 사본 description 에 "하네스 [11] 연동판" 명시 | 동시 삭제 | 엔지니어 선호 |

## 우선순위·부분 실패

4건은 상호 독립. 구현 순서 4 → 3 → 2 → 1. 한 건이라도 검증 실패 시 해당 건만 수정 후 재검증, 전체 PR 단위로 ship (부분 ship 없음).

## 영향 파일

| 파일 | 변경 |
|------|------|
| `scripts/token-usage.py` (신규) | 직전 `--start N` tool 호출 이후 토큰 합산·1줄 출력, 라벨 형식 검증 |
| `docs/harness-workflow.md` · `docs/skills/rp-workflow.md` · `rp-amend.md` | "단계 토큰 출력" 규칙(SSOT) + 오케스트레이터 상태 메시지 링크 |
| `CLAUDE.md` | Interaction 점수·자동 선택 규칙, 트리·스킬-단독 목록·[11] 행 |
| `AGENTS.md` | 질문 절차 요약에 0.5 단위·자동 선택 |
| `docs/skills/rp-specify.md` | 질문 형식·가정 기록에 자동 선택 표기 |
| `docs/prd-template.md` | 가정 행 안내에 자동 선택 접두 |
| `docs/harness-absolute-rules.md` | "최초 리뷰 범위 (변경 중심)" SSOT 문단 · 스킬-단독 6종 |
| `docs/harness-prd.md` · `docs/skills/rp-plan-review.md` · `rp-eng-review.md` | 변경 중심 범위 SSOT 링크 |
| `docs/skills/rp-pr-review.md` (신규, + `.claude/commands` 심링크 · `.codex/skills`) | 이관 + 하네스 연동 절 |
| `docs/skills/rp-ship.md` · `docs/harness-ship.md` | 신규 PR 직후 rp-pr-review 1회 |

## 검증

- 로컬 CI 3종(필수 파일·500줄·내부 링크) 통과, `sync-codex-skills.py --check` 통과
- `token-usage.py --self-test` 통과 + 본 세션 transcript 실행 1줄 출력 확인
- **시범 확인**: 본 사이클 [9] 이후 단계부터 토큰 1줄 출력 · 다음 `rp-amend` 1건에서 [4]·[5] 무관 영역 사소 지적 0건 · 자동 선택 발생 시 1줄 통지 + PRD 접두 확인
- 서브에이전트 리뷰 [4]∥[5], [9-코드] (인프라 축 메타 변경 skip)
- **시범 확인**: 본 PR 이 rp-ship 의 첫 rp-pr-review 호출 대상 (머지 판정 전 출력 확인)

## 롤백 전략

PR revert — 문서·독립 스크립트만 변경, 기존 코드 의존 0건. rp-pr-review 는 플러그인 원본이 남아 있어 revert 시 기능 손실 없음.
