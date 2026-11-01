# PRD: token-usage 집계 보강 (PR #79 rp-pr-review 지적 반영)

**상태:** Approved ([4] 8.17 · [5] 8.3 · [9-코드] 8.43)
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

| # | 문제 | 근거 |
|:-:|------|------|
| 1 | 하네스 루트가 아닌 cwd(서브레포·worktree)에서 상대 경로 `scripts/token-usage.py` 호출 불가. Codex 는 `session_meta.cwd` 정확 일치라 하위 디렉터리 실행 시 `세션 식별 불가` | PR #79 rp-pr-review 지적 (Medium) |
| 2 | Codex `spawn_agent` 자식 rollout 도 같은 cwd → 메인 대신 선택되어 오집계·`경계 없음` | PR #79 rp-pr-review 지적 (Medium). 실측: 자식 rollout `session_meta.payload.source = {"subagent": ...}` |
| 3 | `message.id` 없는 assistant 행이 같은 키로 덮여 과소 집계 | PR #79 rp-pr-review 지적 (Low) |
| 4 | rp-pr-review 호출 프롬프트에 스킬 원문에 없는 문구 추가 | PR #79 rp-pr-review 지적 (Low) — 원인은 메인 호출 방식. #2 반영으로 Codex 자식 rollout 이 집계 제외되어 문구 불필요 → **문서 변경 없음**, 이후 원문 그대로 호출 |

## 결정 사항

| # | 항목 | 결정 | 기각 대안 | 근거 유형 |
|:-:|------|------|-----------|-----------|
| 1 | 호출 경로 | cwd 가 하네스 루트가 아니면 **하네스 루트 절대 경로**로 호출 (경계 정규식은 이미 경로 접두 허용). 문서 표기는 플레이스홀더 `<하네스 루트>/scripts/token-usage.py` — 실제 경로(계정명 포함) 기재 금지. 하네스 루트 = 세션 진입 디렉터리 (서브레포는 별도 git 이라 `git rev-parse` 불가) | 스크립트 PATH 설치 · 환경변수 | 엔지니어 선호 |
| 1-1 | Codex cwd 매칭 | `realpath` 정규화 후 현재 cwd 가 `session_meta.cwd` 와 같거나 **그 하위**(`Path.is_relative_to`, 경로 경계 기준 — `/w` ≠ `/wx`)면 일치. 복수 일치 시 **mtime 최신 우선, 동률은 `session_meta.cwd` 가 긴 후보** ([9] 지적: 깊이 1순위는 과거 서브레포 세션 오선택 → 기록 중인 메인 세션이 최신) | 정확 일치 유지 · 하네스 루트 정규화 | 엔지니어 선호 |
| 2 | 자식 rollout 제외 | `session_meta.payload.source` 가 dict 이고 `subagent` 키 보유 시 후보 제외 (메인만 집계 원칙 유지) | parent_thread_id 로 합산 — 기존 "메인만" 결정 유지 | 사용자 결정 (기존 "간단하게") |
| 3 | id 부재 행 | 키 = `message.id` → 없으면 행 `uuid` → 없으면 파일:행 번호 (`read_jsonl` 에 `enumerate`) | 무시 | 엔지니어 선호 |
| 4 | 프롬프트 문구 | 문서 변경 없음 — 스킬 원문 그대로 호출. 추가됐던 문구 = 리뷰어의 `--start` 실행 금지(경계 오염 방지 목적). Claude 는 서브에이전트 tool 호출이 경계 검색 대상(메인 jsonl) 밖이고, Codex 는 #2 로 자식 rollout 이 후보에서 빠져 오염 경로 없음 | 스킬에 금지 문구 추가 | 엔지니어 선호 |

## 영향 파일

| 파일 | 변경 |
|------|------|
| `scripts/token-usage.py` | 결정 1-1·2·3 + self-test 픽스처(자식 rollout mtime 최신 고정 `os.utime`·하위 cwd·경계 위반 `/wx` 음성·최신 우선·id·uuid 부재) |
| `docs/harness-workflow.md` | "단계 토큰 출력" 에 비루트 cwd 시 `<하네스 루트>/scripts/token-usage.py` 호출 1구 (플레이스홀더) |

## 검증

- `token-usage.py --self-test` 통과, 로컬 CI 3종, `sync-codex-skills.py --check`
- 실데이터: Claude 세션 1줄 출력 확인 + `--runtime codex` 로 로컬 rollout 선택 경로 실행 확인 (본 세션은 Claude 라 Codex 경계 존재 수치는 **픽스처 한정 검증**)
- 서브에이전트 리뷰 [4]∥[5] (변경 중심 최초 리뷰 첫 적용), [9-코드] (인프라 축 메타 skip)

## 롤백 전략

PR revert — 독립 스크립트·문서 1구 변경, 다른 코드 의존 0건.
