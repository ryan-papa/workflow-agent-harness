---
description: '[4] 기획 리뷰. Claude 9항목 점수제 + Codex /codex:review 1회. AND 진행'
argument-hint: '[대상 PRD 경로]'
---

# rp-plan-review

기획 리뷰. PRD의 기능 완전성과 사용자 관점 적합성 검증.

## 트리거

- PRD 작성 완료 후
- `/rp-plan-review` 명령

## 절차

1. **⛔ Claude 기획 리뷰는 반드시 Agent 툴의 서브에이전트로 실행** (`subagent_type=general-purpose`). 메인 에이전트의 셀프 채점 **금지**. 서브에이전트 프롬프트: (a) PRD 파일 경로 전체, (b) 9항목 채점 기준, (c) 독립 판정 지시, (d) **역할 경계: Claude 채점만 수행. Codex 실행·저장 금지**
2. 메인 에이전트가 서브에이전트 응답(점수·근거·개선)을 수신
3. 메인 에이전트: **결과를 `<project-root>/docs/prd/[feature]/review-claude-plan-r{N}.md`로 저장** (N=회차, 덮어쓰기 금지) 후 판정
   - **하네스 메타 변경(간소 PRD)**: 파일명은 `review-claude-meta-r{N}.md` 단일 리뷰로 대체 (plan/eng/code 구분 없이 meta 하나). Codex 저장도 `review-codex-meta.md`
4. 평균 >= 8.0 + 각 항목 >= 7 → Claude 통과. 미달 시 PRD 수정 후 **새 서브에이전트로 재검토** (최대 3회, 매 회차 새 에이전트)
5. **기술 실패 Fallback**: Agent 툴 오류·토큰 초과·형식 오류 시 최대 2회 재호출. 지속 실패 시 사용자에게 즉시 보고 + 중단. 메인 셀프 채점 우회 금지
6. **Claude 통과 후 Codex 추가 리뷰 (1회)**:
   - **Codex 실행 전 `pwd` 확인 필수**: 출력이 해당 PRD 프로젝트 루트와 다르면 `cd`로 이동 후 재확인. 일반 기능 `repositories/[project]/`, 하네스 메타 변경 `claude-projects/`
   - `/codex:review --wait` 실행 (wall-clock 300초 타임아웃)
   - **종료 분기**:
     - 정상 종료 → stdout을 `<project-root>/docs/prd/[feature]/review-codex-plan.md`에 저장 (하네스 메타 변경은 `review-codex-meta.md`). High/Critical 반영 후 동일 파일 `## 반영` 섹션 기록
     - **토큰/기능 신호 매칭 (AND 조건 충족)** → SKIPPED 헤더 + 7항목으로 동일 경로 저장. 반영 대상 없음. 패턴 표·판정 규칙은 [`../harness-codex-review.md`](../harness-codex-review.md) "토큰/기능 이슈 스킵" 섹션 SSOT 참조
     - 그 외 비정상 종료 (네트워크·login·플러그인·hang·매칭 0건) → 워크플로우 중단 + 사용자 보고. 자동 재시도 금지
7. 반영 완료(또는 SKIPPED 저장) 후 다음 단계 진입

## 평가 항목

| 항목 | 설명 |
|------|------|
| 문제 정의 | 해결하려는 문제가 명확하고 관찰 가능한 근거가 있는가 |
| 사용자 가치 | 대상 사용자에게 실질적 가치가 있는가 |
| 기능 완전성 | 누락된 기능이 없는가 |
| 우선순위 | 기능 간 우선순위가 합리적인가 |
| 실현 가능성 | 주어진 조건으로 구현 가능한가 |
| 경계 명확성 | 스코프/비-스코프가 분명하고 포함·비포함 판단이 가능한가 |
| 분기 충분성 | 예외·에러·빈 상태·대안 흐름이 고려되어 있는가 |
| 사용자 검증 게이트 | 실사용자 반응 검증 방법이 있는가 (프로토타입 / 인터뷰 / A·B 테스트 / 내부 시범 사용 중 명시) |
| 대안 탐색 | 대안 A/B/C/D 중 선택 근거 + 판단 근거 유형(창업자 직감 / 엔지니어 선호 / 제품 가설)이 명시되어 있는가 |

## 판정

- 평균 >= 8.0 + 각 항목 >= 7 → 통과
- 평균 미달 또는 항목별 최저 < 7 → Doc Agent 재작성 (최대 3회)
- 3회 실패 → 사용자에게 보고

## ▶ 자동 전환

Claude 통과 + (Codex High/Critical 반영 완료 OR Codex 토큰/기능 SKIPPED) 시 `✓ [4] 기획 리뷰 통과 (Claude+Codex)` (스킵 시 `(Claude+Codex SKIPPED)`) 출력 후 **`/rp-eng-review` 자동 진입**.

→ PRD 상세: [`../harness-prd.md`](../harness-prd.md)
→ Codex 리뷰 규칙: [`../harness-codex-review.md`](../harness-codex-review.md)
