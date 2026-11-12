# PRD: 하네스 규칙 전체 정합성 정비 (상충 13건)

**상태:** Approved ([4] 8.17 → 8.33 → 번복 재검증 8.39 · [5] 8.4 → 8.5 → 8.30 · [9-코드] 8.57 → 번복 재검증 8.64, 인프라 축 메타 skip)
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

사용자 요청: "PR #84 후속 4건 처리 + 하네스 규칙 전체 상충 탐색·정합성 정비". 하네스 문서 33개 전수 감사 결과.

| # | 상충 | 근거 | 영향 |
|:-:|------|------|------|
| 1 *(High)* | PR 본문 PRD 추출 섹션 `## 개요·목적` 이 템플릿에 없음 (템플릿은 `## 문제·맥락`) | rp-ship·harness-ship·절대 규칙 vs `prd-template.md` | Full PRD PR 생성 차단 |
| 2 | harness-prd 섹션 표(사용자 스토리 등)·rp-prd 필수 항목명이 템플릿과 불일치 | harness-prd "PRD 작성", rp-prd "필수 포함 항목" | 작성 기준 분기 |
| 3 | 워크트리 제거 경로 `worktrees/[branch]` vs 생성 경로 leaf 대시 치환 | rp-ship vs harness-dev·rp-dev | 정리 실패 |
| 4 | AGENTS.md 잔존 구 규칙 — Codex 독립 리뷰어(교차 리뷰 금지와 충돌), 직접 재검토(셀프 리뷰 금지와 충돌), 하네스 변경 시 우회 허용(예외 없음과 충돌), High/Critical 체계 | AGENTS.md vs 절대 규칙 | Codex-Lead 오동작 |
| 5 | rp-retro "사용자 승인 절차" 평가(자동 머지와 충돌), 개선 반영이 메타 경로 미경유 | rp-retro vs 절대 규칙 | main 직접 수정 유도 |
| 6 | 메타 단축 경로에 [8] QA·[9-인프라] skip 누락, rp-ship 은 메타 QA 이수 확인 제외, 메타 대상 경로 문서별 상이 | 절대 규칙·rp-workflow·rp-prd·harness-prd·rp-ship | 절대 규칙 "QA 생략 금지" 위반 경로 |
| 7 | [4]·[5] 자동 전환 `/rp-task` 가 메타 경로(task 스킵)와 충돌 | rp-plan-review·rp-eng-review | 전환 오류 |
| 8 | PR #84 비-스코프 3건 — Full PRD 결정 표 위치 미정(절대 규칙 ②), rp-prd·harness-prd 기록 위치 안내 부재, `.codex` 상대 링크 깨짐 | PR #84 PRD | 번복 추적 단절·Codex 링크 실패 |
| 9 | 요청 번복 기록 "이전 결정 명시"가 발화 상충(확정 결정 없음) 미포괄 | PR #84 rp-pr-review Low | 기록 공란 |
| 10 | rp-task 브랜치 도식 base `main` 고정 vs develop→main→master 감지 | rp-task vs harness-dev | 도식 오해 |
| 11 | [9] 심각도 High/Mid/Low **기준 정의 부재**, rp-pr-review 4단계·AGENTS High/Critical 과 체계 상이 | harness-code-review·rp-code-review·rp-pr-review·AGENTS | 처리 분기 자의적 |
| Q1 | [9] Low "사용자 선택" vs "명시된 중단 조건 외 확인 질문 금지" — 점수제 판정과 별개 승인 단계 | harness-code-review vs 절대 규칙 | 자동 진행 규칙 모순 |
| Q2 | 워크트리 재진입 "rebase 안내" vs merge 고정·force-push 금지 | rp-dev·harness-dev vs rp-ship·절대 규칙 | push 된 브랜치 force-push 유도 |

**심각도** ([`harness-code-review.md`](../../harness-code-review.md) "지적 심각도"): High — #1 · Medium — #4·#6·#8·#11·Q1·Q2 · Low — #2·#3·#5·#7·#9·#10

## 결정 사항

| # | 항목 | 결정 | 기각 대안 | 근거 유형 |
|:-:|------|------|-----------|-----------|
| 1 | 추출 섹션 | Full = `## 문제·맥락` + `## 기능 요구사항` | 템플릿에 `개요·목적` 신설 — 섹션 중복 | 엔지니어 선호 |
| 2 | PRD 섹션 SSOT | `prd-template.md` 단독, harness-prd 는 링크, rp-prd 항목명은 템플릿 제목 정렬 | harness-prd 표 갱신 유지 — SSOT 이중화 | 엔지니어 선호 |
| 3 | 워크트리 경로 | 제거 경로도 `[branch 슬래시→대시]` | 생성 경로를 슬래시 그대로 — 중첩 디렉터리·기존 워크트리 이전 필요 | 엔지니어 선호 |
| 4 | AGENTS 정비 | 현행 SSOT 문구로 교체, 심각도는 SSOT 링크 | AGENTS 축소(CLAUDE.md 링크만) — Codex 변환 규칙 소실 | 엔지니어 선호 |
| 5 | 회고 반영 | 평가 항목을 CI 동기 검증·가드로, 반영은 메타 단축 경로, 개선안 선택은 자동 선택 미적용 (`CLAUDE.md` 자동 선택 줄에 예외 링크) | 회고 반영 시 메타 경로 면제 — main 직접 수정 금지와 충돌 | 엔지니어 선호 |
| 6 | 메타 QA | `harness-qa.md` "하네스 메타" 행: 로컬 CI 동등 검사(필수 파일·500줄·내부 링크) + `sync-codex-skills.py --check` + 변경 스크립트 `--self-test`. 메타 대상 = `docs/`·`CLAUDE.md`·`AGENTS.md`·스킬·`scripts/`·`.codex/`·`.claude/settings.json`. `docs/skills/` 전용 예외도 [8]·[9] | 메타 QA 면제 명시 — 절대 규칙 "QA 생략 금지"와 충돌 | 엔지니어 선호 |
| 7 | 전환 분기 | [4]·[5] → `/rp-task` (메타: `/rp-qa`), `rp-qa` 트리거·전환에 메타 분기(코드 축 단독) | 메타도 `/rp-task` 진입 후 즉시 스킵 — 불필요 단계 | 엔지니어 선호 |
| 8 | 결정 기록 위치 | 간이·간소 = 결정 사항 표 / Full = 대안 탐색 선택 근거·"가정 · 리스크 · 열린 질문" 표. harness-prd·rp-prd 는 rp-specify 링크 | Full 템플릿에 결정 표 신설 — 구조 변경 과다 | 엔지니어 선호 |
| 8-1 | `.codex` 링크 | `sync-codex-skills.py` 가 `](./` 정규화 후 `](../` → `](../../../docs/`, `](<이름>.md` → `](../../../docs/skills/<이름>.md` 재작성. 어댑터 노트 문구 갱신 | 어댑터 노트로만 안내 — 링크 클릭 실패 지속 | 엔지니어 선호 |
| 8-2 | 링크 회귀 검사 | QA "하네스 메타" 행 수동 전수 해석으로 확인. `--check` 자동 검사는 비-스코프 | `--check` 에 링크 해석 추가 — 스크립트 범위 확대 | 엔지니어 선호 |
| 9 | 번복 기록 | "번복된 이전 결정 또는 상충한 사용자 발화 명시" | 발화 상충은 기록 생략 — 번복 추적 누락 | 엔지니어 선호 |
| 10 | 도식 | `origin/[base]` (자동 감지) | `main` 유지 + 주석 — 도식·본문 이원화 | 엔지니어 선호 |
| 11 | 심각도 SSOT | `harness-code-review.md` "지적 심각도" 4단계 표 (rp-pr-review 기존 정의 승격). 전 심각도 자동 수정(한도 소진 회차 Low 제외). rp-pr-review·rp-code-review·AGENTS·harness-qa 는 링크·용어 정렬 | 3단계 유지 + 기준 신설 — rp-pr-review 와 이원화 | 엔지니어 선호 |
| Q1 | Low 처리 | **Low 도 자동 반영** (사용자 선택 대기 폐지). 단 재시도 카운터 5회를 모두 소비한 회차가 통과한 경우의 Low 는 미처리 후 진행. 처리·미처리는 산출물 보고[10] 표에 기록 (`harness-ship.md` 보고 포맷). 1차 결정 "현행 유지(선택 대기)"는 [9] 실제 발생 시 "점수제인데 왜 별도 선택?" 사용자 재결정으로 번복 | 현행 유지(선택 대기) — 점수제 판정과 이중 게이트 · 보고만(미반영) | 사용자 결정(요청 번복): 1차 "현행 유지" → 자동 반영 |
| Q2 | 재진입 동기화 | **merge 통일** — `git merge origin/[base]` 안내, rebase·force-push 금지 | push 전 rebase 허용 | 사용자 결정 |

**비-스코프:** 서브레포(`repositories/`) 문서, `docs/research/` 과거 기록, 심각도 표의 `rp-pr-review` 플러그인판(하네스 밖) 동기화.

충돌 확인: Q1 1차 결정(Low 사용자 선택 대기) — 사용자 재결정으로 번복, [4]·[5]·[9] 재검증. 그 외 PR #83·#84 결정과 동일 방향

## 영향 파일

| 파일 | 변경 |
|------|------|
| `docs/harness-absolute-rules.md` | 추출 섹션, 워크트리 경로, 메타 경로(대상·QA·인프라 skip), `docs/skills/` 예외 [8]·[9], 결정 기록 위치 |
| `docs/harness-ship.md` · `docs/skills/rp-ship.md` | 추출 섹션, 열린 질문, 산출물 보고 지적 처리 표, 워크트리 제거 경로, 메타 QA 이수 확인 |
| `docs/harness-prd.md` · `docs/skills/rp-prd.md` | 섹션 SSOT 링크, 항목명 정렬, 메타 대상, 기록 위치 링크 |
| `docs/harness-qa.md` | "하네스 메타" 행, 재검증 플로우 심각도 |
| `docs/harness-code-review.md` · `docs/skills/rp-code-review.md` · `docs/skills/rp-pr-review.md` | 심각도 SSOT 표·처리 원칙·링크, Low 자동 반영 |
| `docs/harness-dev.md` · `docs/skills/rp-dev.md` | 재진입 merge 통일 |
| `docs/skills/rp-workflow.md` | 메타 경로 |
| `docs/skills/rp-plan-review.md` · `rp-eng-review.md` · `rp-task.md` · `rp-retro.md` · `rp-specify.md` · `docs/prd-template.md` | 전환 분기, 도식, 회고 규칙, 번복 기록 |
| `AGENTS.md` | 구 규칙 정비, 심각도 링크, 메타 QA |
| `CLAUDE.md` | 자동 선택 `rp-retro` 예외 링크 |
| `docs/skills/rp-qa.md` | 메타 분기 트리거·유형·전환 |
| `scripts/sync-codex-skills.py` (+ `.codex/skills/*` 15종 재생성) | 상대 링크 재작성 |

## 검증

- 메타 QA: 로컬 CI 동등 검사(500줄·내부 링크), `sync-codex-skills.py --check`, `.codex` 링크 전수 해석 0 broken, 잔존 문구 grep(`개요·목적`·`rebase 안내`·`High/Mid`·`보조 구현자`·`사용자 승인 절차`·`Low 지적 선택`) 0건
- 서브에이전트 리뷰 [4]∥[5], [9-코드] (인프라 축 메타 skip)
- 시범 확인: 다음 서비스 Full PRD ship 에서 PR 본문 추출 성공, 다음 [9] 에서 Low 자동 반영·산출물 보고 표 기록 동작을 `rp-retro` 에 기록

## 롤백 전략

PR revert — 문서·변환 스크립트 국소 변경, `.codex` 는 스크립트 재실행으로 재생성.
