# rp-prd

PRD(Product Requirements Document) 작성.

## 트리거

- 구체화 완료 후
- `/rp-prd` 명령

## 절차

1. 구체화 결과 + 리서치 자료를 컨텍스트로 수집
2. PRD 템플릿 기반으로 문서 작성
3. 파일명: `docs/prd/YYYYMMDD_HHMMSS_[project]_[random].md`
4. 기능 요구사항은 F-XX ID 부여

## 필수 포함 항목

| 섹션 | 내용 |
|------|------|
| 프로젝트 개요 | 목적, 대상 사용자 |
| 기능 요구사항 | F-01 ~ F-XX, 우선순위 |
| 기술 스택 | 언어, 프레임워크, 인프라 |
| 제약사항 | 성능, 보안, 호환성 |
| Open Issues | 미결 사항 |

## 완료 조건

- PRD 파일 생성 완료
- 기능 요구사항 F-XX 전체 작성
- 기획 리뷰 진입 가능 상태

## ▶ 자동 전환

완료 즉시 `✓ [3] PRD 작성 완료` 출력 후 **`/rp-plan-review` 자동 진입**.

→ PRD 상세: [`../harness-prd.md`](../harness-prd.md)
→ 템플릿: [`../prd-template.md`](../prd-template.md)
