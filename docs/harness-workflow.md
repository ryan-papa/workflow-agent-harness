# Harness Engineering Workflow

## Full Flow

```
사용자 기능 전달
  ↓
▶ [1] 프로젝트 초기화              → /rp-init
  ↓
▶ [2] 구체화 (도메인 → 기술, 질문)  → /rp-specify
  ↓
▶ [3] PRD 작성                     → /rp-prd
  ↓
▶ [4] 기획 리뷰 ∥ [5] 엔지니어링 리뷰  → /rp-plan-review ∥ /rp-eng-review
     (병렬 동시 발사, 축별 최대 3회)
  ↓ 양축 통과 시 바로 개발 진입 (사용자 승인 생략)
▶ [6] 태스크 분해                   → /rp-task
  ↓
▶ [7] 개발 (태스크별 반복)           → /rp-dev
  ↓
▶ [8] QA / 콘텐츠 검수              → /rp-qa
  ↓
▶ [9-코드] 코드 리뷰(7항목) ∥ [9-인프라] 인프라 리뷰(BLOCK/ASK/WARN)
     (병렬 동시 발사, 공통 최대 5회)  → /rp-code-review ∥ /rp-infra-review
  ↓
▶ [10] 산출물 보고 (자동 진행)
  ↓
▶ [11] 커밋 → PR → CI → **자동 머지(가드 3종 AND)** → 배포 → /rp-ship
  ↓
(선택) [12] 회고 — 사용자 명시 명령 시에만 실행 → /rp-retro
```

**작성 모드 분기:** 메인 런타임이 Claude면 Claude-Lead, Codex면 Codex-Lead. **런타임 = 리뷰어** — 진입 런타임의 서브에이전트만 채점하며 교차 런타임 추가 리뷰는 전면 금지. 메인 셀프 채점 절대 금지. SSOT [`harness-absolute-rules.md`](harness-absolute-rules.md) "작성 모드 및 리뷰 매트릭스".

**상태 메시지:** 진입 `▶ [N] 단계명...`, 완료 `✓ [N] 단계명 완료`

**스킬 인덱스:**

| # | 단계 | 스킬 파일 |
|:-:|------|----------|
| 1 | 프로젝트 초기화 | [`skills/rp-init.md`](skills/rp-init.md) |
| 2 | 구체화 | [`skills/rp-specify.md`](skills/rp-specify.md) |
| 3 | PRD 작성 | [`skills/rp-prd.md`](skills/rp-prd.md) |
| 4 | 기획 리뷰 (∥ 5) | [`skills/rp-plan-review.md`](skills/rp-plan-review.md) |
| 5 | 엔지니어링 리뷰 (∥ 4) | [`skills/rp-eng-review.md`](skills/rp-eng-review.md) |
| 6 | 태스크 분해 | [`skills/rp-task.md`](skills/rp-task.md) |
| 7 | 개발 | [`skills/rp-dev.md`](skills/rp-dev.md) |
| 8 | QA / 콘텐츠 검수 | [`skills/rp-qa.md`](skills/rp-qa.md) |
| 9 | 코드 리뷰 (∥ 인프라) | [`skills/rp-code-review.md`](skills/rp-code-review.md) |
| 9 | 인프라 리뷰 (∥ 코드) | [`skills/rp-infra-review.md`](skills/rp-infra-review.md) |
| 10 | 산출물 보고 | — (스킬 없음, 자동 진행) |
| 11 | 커밋·PR·머지·배포 | [`skills/rp-ship.md`](skills/rp-ship.md) |
| 12 | 회고 | [`skills/rp-retro.md`](skills/rp-retro.md) |

**오케스트레이터:**
- [`skills/rp-workflow.md`](skills/rp-workflow.md) — 신규 프로젝트·기능 (init부터 전 단계)
- [`skills/rp-amend.md`](skills/rp-amend.md) — 기존 프로젝트에 기능 수정·추가 (init 스킵, Lite 판별 후 Full amend 또는 핫픽스 경량 트랙)

---

→ PRD 상세: [`harness-prd.md`](harness-prd.md)
→ 개발 상세: [`harness-dev.md`](harness-dev.md)
→ QA + 콘텐츠 검수: [`harness-qa.md`](harness-qa.md)
→ 코드리뷰 상세: [`harness-code-review.md`](harness-code-review.md)
→ 인프라 리뷰 상세: [`harness-infra-review.md`](harness-infra-review.md)
→ 산출물 + 배포: [`harness-ship.md`](harness-ship.md)
→ 스킬 목록: [`skills/`](skills/)

## 자동 진입 규칙

| 구간 | 자동 진입 조건 | 중단 조건 |
|------|--------------|----------|
| [4]∥[5] 리뷰→[6] | **양축** 점수 통과 시 자동 | 축별 3회 미달 시 자동 중단 + **사용자 결정 요청** (강행/재설계/중단) |
| [7]→[8] 개발→QA | 전체 태스크 완료+빌드 통과 시 자동 | 빌드/테스트 실패 |
| [8]→[9] QA→코드리뷰 | QA 통과 시 자동 | QA 3회 실패 |
| [9]→[10] 코드∥인프라 리뷰→산출물 | **양축** 통과(코드 점수 + 인프라 BLOCK·미해결 ASK 0건) 시 자동 | 공통 **5회** 미달 시 자동 중단 + 사용자 결정 요청. 인프라 **ASK 발생 시 중단 + 사용자 결정** |
| [10]→[11] 산출물→커밋·PR | 산출물 보고 후 자동 ("산출물 보고 완료, 커밋·PR 자동 진행합니다" 출력) | — |
| [11] 커밋·PR→자동 머지 | **CI + 게이트 + base 정상 + MERGEABLE AND 충족 시 자동 머지** | 가드 1개 이상 실패 → 중단 + OPEN 유지 + 사용자 보고 |
| [11]→[12] 배포→회고 | **자동 진입 없음**. 사용자 `/rp-retro` 명령 시에만 실행 | — |

**⛔ 절대 규칙 SSOT:** [`harness-absolute-rules.md`](harness-absolute-rules.md) — QA/코드리뷰 생략 불가, 자동 머지 가드 3종 AND, 메타 단축 경로, rp-ship 필수 호출, main 직접 수정 금지 등 본문은 SSOT 참조

**워크플로우 보조 규칙 (단계 흐름 한정):**
- 사용자에게 "작업 완료"라고 전달하는 시점은 [10] 이후, [11] 이전

## 핫픽스 경량 트랙 (Lite)

**적용 대상:** 기존 동작을 수정하는 단일 버그 픽스 (UI z-index, 오타, 색상, 접근성 경고 등). 신규 기능·스펙 변경·API 변경은 제외.
**진입:** 기존 프로젝트 핫픽스 요청은 `rp-amend`가 Lite 판별 후 본 트랙으로 라우팅한다.

**판별 기준 (모두 충족):**
- 변경 파일 3개 이하(테스트·설정 제외), 총 diff 50 LOC 이하 예상
- 사용자가 "버그/핫픽스/수정" 표현으로 지시
- 공개 API·DB 스키마·기존 Full PRD 스펙 변경 없음

| 단계 | Lite 처리 |
|------|----------|
| 질문 | **2~3개** (범위·동작·테스트 방식만) |
| PRD | **간이 1쪽** (배경·목표·In/Out·테스트만, 리뷰 항목 생략) |
| 기획·엔지니어링 리뷰 | **통합 1회**, 평균 점수만 기록 |
| 태스크 분해 | 생략 (단일 태스크) |
| QA | **필수 유지** — E2E + axe 규칙 그대로 적용 |
| 코드 리뷰 | **필수 유지** — 7항목 최저점수제 그대로 |
| 인프라 리뷰 | **필수 유지** — 코드 축과 병렬. 5영역 무해당 시 N/A 1줄 |
| 산출물 보고·ship | 필수 유지 |
| 회고 | 사용자 명시 명령 시에만 실행 (자동 진입 없음) |

**⛔ Lite 트랙 금지 조건:**
- QA·코드리뷰 축소 금지
- 테스트 없이 커밋 금지
- Lite 판별 실패 시 즉시 Full 트랙 전환

**리뷰 예외:** 통합 plan/engineering 리뷰는 Full flow 분리 리뷰 규칙의 Lite 전용 예외다. 메인 셀프 채점은 여전히 금지하며 작성 모드별 서브에이전트가 자동 수행한다.

## 프로젝트 유형별 QA 분기

→ SSOT: [`harness-qa.md`](harness-qa.md) "프로젝트 유형별 분기" 표

## 공통 규칙

**프로젝트 초기화 (자동 생성):**

| 항목 | 경로 | 비고 |
|------|------|------|
| 프로젝트 설정 | `repositories/[project]/CLAUDE.md` | |
| 리드미 | `repositories/[project]/README.md` | 유형별 템플릿 적용 |
| PRD 디렉토리 | `repositories/[project]/docs/prd/` | |
| 리서치 디렉토리 | `repositories/[project]/docs/research/` | |

**README 템플릿:** 프로젝트 유형에 따라 선택 적용
- 오픈소스/라이브러리 → [`templates/readme-opensource.md`](templates/readme-opensource.md)
- 사내 서비스/API → [`templates/readme-service.md`](templates/readme-service.md)
- 작성 규칙: [`harness-readme.md`](harness-readme.md)

**에이전트 컨텍스트 표준 (필수 전달 항목):**

| 항목 | 내용 |
|------|------|
| 역할 정의 | 에이전트 역할 명시 |
| 파일 경로 | 읽기·쓰기 대상 경로 |
| 요구사항 요약 | 수집된 내용 |
| 작성 규칙 | 500줄 이하, 테이블/리스트 우선 |

**리서치 결과 저장:**
- 경로: `repositories/[project]/docs/research/YYYYMMDD_[topic].md`
- Doc Agent 호출 시 경로를 컨텍스트로 전달

**문서 정합성:**
- docs/ 파일 변경 시 CLAUDE.md 트리·링크 자동 동기화
- `docs/skills/rp-*.md` 신규 생성 시 `.claude/commands/rp-*.md` 심링크 `PostToolUse` 훅이 자동 생성 (`.claude/hooks/sync-rp-commands.sh`)
- `docs/skills/rp-*.md` 변경 시 `.codex/skills/rp-*/SKILL.md`도 `scripts/sync-codex-skills.py`로 동기화

**스펙 변경 시 문서 우선 원칙:**
- 기능 추가/변경/삭제 시 코드 작업 전에 반드시 PRD 문서 먼저 업데이트
- 변경 부분에 대해 기획 리뷰 + 엔지니어링 리뷰 수행
- 리뷰 통과 후 코드 작업 진행
- 코드보다 문서가 먼저. 문서 없이 코드 수정 금지

**UI 프로젝트 시 디자인 원칙:**
- UI가 포함된 프로젝트는 [`harness-design.md`](harness-design.md)의 디자인 원칙을 준수
