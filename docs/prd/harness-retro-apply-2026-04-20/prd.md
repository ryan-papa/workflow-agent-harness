# PRD: 하네스 회고 반영 (2026-04-20)

**상태:** In Review
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

PR #16 머지 회고에서 도출된 4개 개선사항 반영:
1. 메타 변경도 feat 브랜치 + PRD + 리뷰 필수화
2. 메타 변경용 간소 PRD 섹션 정의 (완전 생략 금지)
3. Codex `/codex:review` 실행 전 cwd 자동 체크
4. `rp-ship` 스킬 필수 호출 (수동 git/gh 우회 금지)

## 영향 파일

| 파일 | 변경 |
|------|------|
| `CLAUDE.md` | 절대 규칙 3개 추가 (메타 변경도 feat+PRD, main 직수정 금지, rp-ship 필수) |
| `docs/harness-prd.md` | 메타 변경용 간소 PRD 섹션 정의 추가 |
| `docs/skills/rp-plan-review.md` | Codex 실행 전 `pwd` 확인 절차 |
| `docs/skills/rp-eng-review.md` | 동일 |
| `docs/skills/rp-code-review.md` | 동일 |
| `docs/harness-codex-review.md` | cwd 체크 절차 강화 |
| `docs/skills/rp-workflow.md` | rp-ship 필수 호출 명시 |
| `docs/harness-workflow.md` | 반영 |

## 롤백 전략

문서만 변경이므로 `git revert <merge-sha>` 또는 main 직접 revert PR 생성으로 즉시 롤백 가능. 워크플로우 오작동 시 PR #16 직후 상태로 복원.

## 검증

- lint-docs CI 통과
- Claude 자체 점검 + Codex 1회 리뷰 후 High/Critical 반영
- 각 파일 200줄 한도 유지
