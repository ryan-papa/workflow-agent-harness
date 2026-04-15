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
▶ [4] 기획 리뷰 ← 최대 3회         → /rp-plan-review
  ↓
▶ [5] 엔지니어링 리뷰 ← 최대 3회   → /rp-eng-review
  ↓ 점수 만족 시 바로 개발 진입 (사용자 승인 생략)
▶ [6] 태스크 분해                   → /rp-task
  ↓
▶ [7] 개발 (태스크별 반복)           → /rp-dev
  ↓
▶ [8] QA / 콘텐츠 검수              → /rp-qa
  ↓
▶ [9] 코드 리뷰 (7항목)             → /rp-code-review
  ↓
▶ [10] 산출물 보고 → 사용자 승인
  ↓
▶ [11] 커밋 → PR → CI → 머지 → 배포 → /rp-ship
  ↓
▶ [12] 회고                          → /rp-retro
```

**상태 메시지:** 진입 `▶ [N] 단계명...`, 완료 `✓ [N] 단계명 완료`

**오케스트레이터:** `/rp-workflow`가 전체 플로우를 관리하고 각 스킬을 순서대로 호출

---

→ PRD 상세: [`harness-prd.md`](harness-prd.md)
→ 개발 상세: [`harness-dev.md`](harness-dev.md)
→ QA + 콘텐츠 검수: [`harness-qa.md`](harness-qa.md)
→ 코드리뷰 상세: [`harness-code-review.md`](harness-code-review.md)
→ 산출물 + 배포: [`harness-ship.md`](harness-ship.md)
→ 스킬 목록: [`skills/`](skills/)

## 자동 진행 규칙

| 구간 | 자동 진행 조건 | 중단 조건 |
|------|--------------|----------|
| [4]→[5] 리뷰 | 점수 통과 시 자동 | 3회 실패 시 사용자 보고 |
| [7]→[8] 개발→QA | 전체 태스크 완료+빌드 통과 시 자동 | 빌드/테스트 실패 |
| [8]→[9] QA→코드리뷰 | QA 통과 시 자동 | QA 3회 실패 |
| [9]→[10] 코드리뷰→산출물 | 코드리뷰 통과 시 자동 | 3회 실패 |
| [10]→[11] 산출물→배포 | **사용자 승인 필수** | 사용자 거부 |
| [11]→[12] 배포→회고 | 배포 완료 시 자동 | — |

**⛔ 절대 규칙:**
- [8] QA, [9] 코드리뷰 **생략 불가** — 어떤 이유로도 스킵 금지
- [10] 산출물 보고 없이 [11] 배포 진행 **금지**
- [12] 회고 **생략 불가** — 배포 완료 후 반드시 수행
- 사용자에게 "작업 완료"라고 전달하는 시점은 [10] 이후, [11] 이전

## 프로젝트 유형별 QA 분기

| 유형 | 판별 기준 | QA 방식 | 코드리뷰 |
|------|----------|---------|---------|
| 코드 프로젝트 | src/ 또는 실행 코드 존재 | 기능 QA + E2E + 디자인 QA | 7항목 전체 |
| 콘텐츠/문서 프로젝트 | MDX/MD 콘텐츠 중심 | 빌드+렌더링+내용 품질 검수 | 빌드 검증만 |

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
| 작성 규칙 | 200줄 이하, 테이블/리스트 우선 |

**리서치 결과 저장:**
- 경로: `repositories/[project]/docs/research/YYYYMMDD_[topic].md`
- Doc Agent 호출 시 경로를 컨텍스트로 전달

**문서 정합성:**
- docs/ 파일 변경 시 CLAUDE.md 트리·링크 자동 동기화

**스펙 변경 시 문서 우선 원칙:**
- 기능 추가/변경/삭제 시 코드 작업 전에 반드시 PRD 문서 먼저 업데이트
- 변경 부분에 대해 기획 리뷰 + 엔지니어링 리뷰 수행
- 리뷰 통과 후 코드 작업 진행
- 코드보다 문서가 먼저. 문서 없이 코드 수정 금지

**UI 프로젝트 시 디자인 원칙:**
- UI가 포함된 프로젝트는 [`harness-design.md`](harness-design.md)의 디자인 원칙을 준수
