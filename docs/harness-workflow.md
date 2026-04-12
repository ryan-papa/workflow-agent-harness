# Harness Engineering Workflow

## Full Flow

```
사용자 기능 전달
  ↓
▶ [1] 프로젝트 초기화
  ↓
▶ [2] 구체화 (도메인 → 기술, 질문·리서치)
  ↓
▶ [3] PRD 작성 (Doc Agent)
  ↓
▶ [4] 기획 리뷰 (Planning Review Agent) ← 최대 3회
  ↓
▶ [5] 엔지니어링 리뷰 (Engineering Review Agent) ← 최대 3회
  ↓ 점수 만족 시 바로 개발 진입 (사용자 승인 생략)
▶ [6] 태스크 분해
  ↓
▶ [7] 개발 (통합 브랜치 → 태스크별 반복)
  ↓
▶ [8] QA (사전 검증 → 시나리오 테스트)
  ↓
▶ [9] 코드 리뷰 (8항목) → 개선 ← 최대 3회
  ↓
▶ [10] 최종 산출물 전달
```

**상태 메시지:** 진입 `▶ [N] 단계명...`, 완료 `✓ [N] 단계명 완료`

---

→ PRD 상세: [`harness-prd.md`](harness-prd.md)
→ 개발 상세: [`harness-dev.md`](harness-dev.md)
→ 코드리뷰 상세: [`harness-code-review.md`](harness-code-review.md)

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
