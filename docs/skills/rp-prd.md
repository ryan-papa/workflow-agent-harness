---
description: '[3] PRD 작성. 일반 기능은 Full PRD, 하네스 메타 변경은 간소 PRD 자동 분기'
argument-hint: '[기능·변경 컨텍스트]'
---

# rp-prd

PRD(Product Requirements Document) 작성.

## 트리거

- 구체화 완료 후
- `/rp-prd` 명령

## 절차

### 분기 — 변경 유형 판별

1. **하네스 메타 변경** (`docs/`, `CLAUDE.md`, 스킬, `.claude/settings.json`) → **간소 PRD 경로**
2. **일반 기능 변경** (`repositories/[project]/`) → **Full PRD 경로**

### Full PRD (일반 기능)

1. 구체화 결과 + 리서치 자료를 컨텍스트로 수집
2. PRD 템플릿 기반으로 문서 작성
3. 파일명: `repositories/[project]/docs/prd/YYYYMMDD_HHMMSS_[feature]_[random].md`
4. 기능 요구사항은 F-XX ID 부여

### 간소 PRD (하네스 메타 변경)

1. 변경 이유·영향 파일·롤백 전략·검증 방법 4섹션 작성
2. 파일명: `docs/prd/[feature]/prd.md` (하네스 루트 기준)
3. 완전 생략 금지 — 4섹션 모두 작성 필수
4. 상세 규격: [`../harness-prd.md`](../harness-prd.md) "간소 PRD" 섹션 참조

## 필수 포함 항목

| 섹션 | 내용 |
|------|------|
| 프로젝트 개요 | 목적, 대상 사용자 |
| 핵심 시나리오 + 실패 모드 | 코드경로 × 시나리오 × 감지 × UX 대응 |
| 대안 탐색 | A/B/C/D + 판단 근거 유형 + 선택 근거 |
| 톤·정체성 | 톤·어투·금칙어·레퍼런스·샘플 카피 |
| 기능 요구사항 | F-01 ~ F-XX, 우선순위 |
| AI 기능 검증 | AI 포함 시 정답 샘플셋·채점 기준·주입 방어·합격선 (해당 시만) |
| 기술 스택 | 언어, 프레임워크, 인프라 |
| 제약사항 | 성능, 보안, 호환성 |
| **공개 전환 시나리오** | **보안·시크릿 관련 기능에 한해 필수.** 레포가 공개로 전환되거나 산출물이 외부에 노출될 때 추가 리스크가 생기는 요소가 있는지 검토. (예: 공개키 하드코딩, 인프라 식별자, 개인 식별 정보) |
| Open Issues | 미결 사항 |

신규 섹션이 비면 공란으로 두지 말고 "해당 없음" + 근거 명시.

## 완료 조건

- PRD 파일 생성 완료
- 기능 요구사항 F-XX 전체 작성
- 기획 리뷰 진입 가능 상태

## ▶ 자동 전환

완료 즉시 `✓ [3] PRD 작성 완료` 출력 후 **`/rp-plan-review` 자동 진입**.

→ PRD 상세: [`../harness-prd.md`](../harness-prd.md)
→ 템플릿: [`../prd-template.md`](../prd-template.md)
