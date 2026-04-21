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

- [ ] 수정 후 `rp-plan-review`, `rp-eng-review`, `rp-code-review` 스킬 문서에 "Agent 툴 필수" 문구 포함 확인
- [ ] `CLAUDE.md` "⛔ 하네스 절대 규칙" 블록에 신규 항목 포함
- [ ] Codex 리뷰 1회 통과 (High/Critical 없음)
- [ ] 최소 1건의 실제 하네스 워크플로 실행 시 리뷰가 서브에이전트로 수행되는지 육안 확인 (museum-finder 엔지 리뷰 재시도에서 확인 가능)
