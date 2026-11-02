# PRD: token-usage Codex 세션 후보 범위 제한 (PR #80 rp-pr-review 지적 반영)

**상태:** Approved ([4] 8.11 · [5] 8.3 · [9-코드] 8.64)
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

| # | 문제 | 근거 |
|:-:|------|------|
| 1 | cwd 하위 일치 도입 후 상위 디렉터리(`~`·`/`) Codex 메인 세션도 모든 cwd 의 후보 → 동시 기록 중이면 mtime 최신으로 선택되어 `경계 없음`·타 세션 오집계. 후보가 있는 상태의 "불일치" 음성 테스트도 사라짐 | PR #80 rp-pr-review 지적 (Medium) |
| 2 | 매 호출 모든 rollout 첫 줄(지침 원문 포함, 큼) 파싱 — 세션 수천 개 시 지연 | PR #80 rp-pr-review 지적 (Low) |
| 3 | 비루트 cwd 절대 경로 안내가 `--start` 괄호 안에만 있어 보고 호출에 미적용 | PR #80 rp-pr-review 지적 (Low) |
| 4 | `--start N` 과 보고 호출을 **같은 응답의 동시 tool 호출**로 실행하면 보고 시점에 같은 응답의 tool_use 행이 transcript 미기록 → 이전 단계 라벨로 오집계 | 본 세션 실측: [3] 보고가 `[11]` 로 출력, 해당 행은 응답 종료 후 일괄 기록 |

## 결정 사항

| # | 항목 | 결정 | 기각 대안 | 근거 유형 |
|:-:|------|------|-----------|-----------|
| 1 | 후보 범위 | 후보 `session_meta.cwd` 는 **하네스 루트 이하**여야 함 + 현재 cwd 가 그 하위(기존). 하네스 루트 = `Path(__file__).resolve().parents[1]` 를 `main` 에서 `codex_session(root, cwd, harness_root)` 로 주입(self-test 는 픽스처 루트 주입). 비-스코프: 하네스 밖 Codex 세션·하네스 `worktrees/` 사본 스크립트 호출 → `세션 식별 불가` (메인 루트 스크립트로 호출). 잔여 위험: 하네스 루트 안 동시 Codex 세션 2개는 mtime 으로만 구분 | `--start` 경계 보유 후보만 — 후보마다 전체 파싱 필요 | 엔지니어 선호 |
| 2 | 탐색 비용 | mtime 내림차순 순회, 첫 일치의 mtime 보다 오래된 파일에서 조기 종료 (동률만 cwd 깊이 비교) | 전수 파싱 유지 · 캐시 파일 (파일 저장 없음 원칙 위배) | 엔지니어 선호 |
| 3 | 문서 | "두 호출 모두 cwd 가 하네스 루트가 아니면 `<하네스 루트>/scripts/token-usage.py`" 로 괄호 밖 이동 | — (문구 위치 이동) | 엔지니어 선호 |
| 4 | 호출 분리 | "`--start` 와 보고 호출을 **같은 assistant 메시지의 병렬 tool 호출로 묶지 않는다** (순차 호출은 허용). 보고 호출이 포함된 응답 자체의 사용량은 미포함" 을 SSOT + `rp-workflow.md` 상태 메시지에 명시. 운영 체크: 보고 라벨이 현재 단계와 다르면 수치 대신 `토큰: 집계 누락` 출력 | 스크립트에서 감지 — transcript 지연 기록이라 감지 불가 | 엔지니어 선호 |

## 영향 파일

| 파일 | 변경 |
|------|------|
| `scripts/token-usage.py` | `codex_session` 에 `harness_root` 범위·조기 종료. self-test: 기존 `/elsewhere` 단언 → 음성(Fail), "newest wins" 단언 → 루트 이하 후보(`/w`·`/w/sub`)로 재구성, 상위(`/`) 세션 배제, 오래된 비일치 파일 존재 시 첫 일치 반환 |
| `docs/harness-workflow.md` | "단계 토큰 출력" 문구 위치 이동 + 호출 분리·라벨 대조 규칙 |
| `docs/skills/rp-workflow.md` (+ `.codex`) | 상태 메시지 토큰 줄에 호출 분리 1구 |

## 검증

- `token-usage.py --self-test` 통과, 로컬 CI 3종, `sync-codex-skills.py --check`
- 실데이터: Claude 1줄 출력, `--runtime codex` 하네스 루트·서브레포 cwd 세션 선택 (수치는 픽스처 한정)
- 서브에이전트 리뷰 [4]∥[5], [9-코드] (인프라 축 메타 skip)

## 롤백 전략

PR revert — 독립 스크립트·문서 1구 변경, 다른 코드 의존 0건.
