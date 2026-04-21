# 간소 PRD: 리뷰 단계 서브에이전트 강제

## 변경 이유

현재 `rp-plan-review`, `rp-eng-review` 스킬에 **"Claude 서브에이전트가 검토"**라고 서술돼 있으나, 실제 운영에서 메인 Claude가 **자신이 작성한 PRD를 자체 채점**하는 사례가 발생. 이해충돌·관성 편향으로 리뷰 신뢰도 저하. Codex 리뷰는 외부 독립이나, Claude 1차 리뷰는 여전히 본인 셀프 체크.

**목표**: 평가 단계는 **반드시 Agent 툴로 분리된 서브에이전트**가 실행하도록 절차·규칙 강제. 메인 에이전트의 자체 채점 금지.

## 영향 파일

| 파일 | 변경 내용 |
|------|----------|
| `CLAUDE.md` | 최상위 하네스 절대 규칙에 "평가 단계 서브에이전트 필수" 항목 추가 |
| `docs/skills/rp-plan-review.md` | 절차 1번 "서브에이전트 호출(Agent 툴, subagent_type=general-purpose)" 명시. 메인 에이전트 셀프 채점 금지 |
| `docs/skills/rp-eng-review.md` | 동일 |
| `docs/skills/rp-code-review.md` | 동일 (9단계도 서브에이전트 필수) |
| `docs/harness-prd.md` | "PRD 리뷰 2단계 순차 실행" 블록에 서브에이전트 원칙 추가 |
| `docs/harness-code-review.md` | 코드 리뷰 실행 주체 서브에이전트 명시 |

## 롤백 전략

단순 문서 변경이므로 `git revert <commit>` 또는 PR close로 즉시 원복 가능. 실 코드 영향 없음.

## 검증

- [ ] 수정 후 `rp-plan-review`, `rp-eng-review`, `rp-code-review` 스킬 문서에 "Agent 툴 필수 + 역할 경계 + Fallback" 3요소 모두 포함 확인
- [ ] `CLAUDE.md` "⛔ 하네스 절대 규칙" 블록에 신규 항목(역할 분리 + Fallback + 증거 저장) 포함
- [ ] Codex 리뷰 1회 통과 (High/Critical 없음)
- [ ] 다음 실제 하네스 워크플로에서 `review-claude-{plan,eng,code}.md` 파일이 **실제 생성**되는지 확인 (증거 기반 검증, 육안 아님)
- [ ] 다음 `rp-retro` 회고에 "셀프 채점 재발 여부" 점검 항목 포함 확인

## 리스크·Tradeoff (부작용)

| 리스크 | 대응 |
|--------|------|
| 서브에이전트 반복 호출로 토큰 비용 증가 (재시도 3회 × 3단계 = 최대 9회) | 정당화: 이해충돌 방지 가치 > 비용. retro에서 실 비용 관측 후 재조정 |
| 서브에이전트 자체 장애 시 워크플로 중단 | Fallback 절차 2회 재호출 + 사용자 보고. 메인 우회 **금지** |
| 매 회차 PRD·CLAUDE.md 재로드 | 향후 공통 프롬프트 템플릿 `docs/templates/review-subagent-prompt.md` 분리로 감축 검토 |
