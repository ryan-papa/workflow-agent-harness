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

1. **하네스 메타 변경** (`docs/`, `CLAUDE.md`, `AGENTS.md`, 스킬, `scripts/`, `.codex/`, `.claude/settings.json`) → **간소 PRD 경로**
2. **일반 기능 변경** (`repositories/[project]/`) → **Full PRD 경로**

### Full PRD (일반 기능)

1. 구체화 결과 + 리서치 자료를 컨텍스트로 수집
2. PRD 템플릿 기반 문서 작성
3. 파일명: `repositories/[project]/docs/prd/YYYYMMDD_HHMMSS_[feature]_[random].md`
4. 기능 요구사항에 F-XX ID 부여

### 간소 PRD (하네스 메타 변경)

1. 변경 이유·영향 파일·롤백 전략·검증 방법 4섹션 작성
2. 파일명: `docs/prd/[feature]/prd.md`(하네스 루트 기준)
3. 완전 생략 금지 — 4섹션 모두 작성 필수
4. **frontmatter 식별자**: PRD 본문 상단에 `**유형:** 하네스 메타 변경` 명시 (rp-ship 메타 분기 선검사 키)
5. 상세 규격: [`../harness-prd.md`](../harness-prd.md) "간소 PRD" 섹션 참조

## 필수 포함 항목

| 섹션 | 내용 |
|------|------|
| 문제·맥락 · 타깃 사용자 | 배경·원인·왜 지금, 대상 사용자·사용 맥락 |
| 핵심 시나리오 + 실패 모드 | 코드경로 × 시나리오 × 감지 × UX 대응 |
| 대안 탐색 | A/B/C/D + 판단 근거 유형 + 선택 근거 |
| 스코프 & 비-스코프 · 성공 기준 & 실패 기준 | In/Out, 성공 지표·접을 기준 |
| 톤·정체성 | 톤·어투·금칙어·레퍼런스·샘플 카피 |
| 기능 요구사항 | F-01 ~ F-XX, 우선순위 |
| AI 기능 검증 | AI 포함 시 정답 샘플셋·채점 기준·주입 방어·합격선(해당 시만) |
| 비기능 요구사항 | 성능, 보안, 확장성 |
| 기술 스택 · 제약사항 | 언어·프레임워크·인프라, 기술·비즈니스 제약 |
| **공개 전환 시나리오** | **보안·시크릿 관련 기능에 한해 필수.** 레포가 공개로 전환되거나 산출물이 외부에 노출될 때 추가 리스크가 생기는 요소가 있는지 검토. (예: 공개키 하드코딩, 인프라 식별자, 개인 식별 정보) |
| 가정 · 리스크 · 열린 질문 | 가정·요청 번복·리스크·미결 사항 (접두·위치: [`rp-specify.md`](rp-specify.md) "추론 우선 판정") |

섹션 구조 SSOT: [`../prd-template.md`](../prd-template.md). 신규 섹션이 비면 공란으로 두지 말고 "해당 없음" + 근거 명시.

## 완료 조건

- PRD 파일 생성 완료
- 기능 요구사항 F-XX 전체 작성
- 기획 리뷰 진입 가능 상태

## ▶ 자동 전환

완료 즉시 `✓ [3] PRD 작성 완료` 출력 후 **`/rp-plan-review` 자동 진입** (`docs/skills/` 전용 메타 예외 — 변경 범위가 `docs/skills/` + `.codex/skills/` 동기화분으로 한정될 때 (해당 변경의 PRD 산출물 `docs/prd/[feature]/prd.md` 는 판정에서 무시 — 포함돼도 예외 유지): [4]·[5] 스킵 → `/rp-qa` — [`../harness-absolute-rules.md`](../harness-absolute-rules.md) "단축 경로·예외").

→ PRD 상세: [`../harness-prd.md`](../harness-prd.md)
→ 템플릿: [`../prd-template.md`](../prd-template.md)
