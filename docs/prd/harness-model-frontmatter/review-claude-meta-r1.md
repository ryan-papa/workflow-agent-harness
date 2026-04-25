# Claude Meta Review r1 — harness-model-frontmatter

| 항목 | 점수 | 근거 |
|---|:-:|---|
| 변경 이유 | 9 | PR #31 정책의 자동 강제 메커니즘 부재를 명확히 진단. Claude Code 공식 frontmatter `model:` 동작(현 턴만, 다음 턴 복귀)까지 인용. 1점 감점은 "현 턴만" 거동의 공식 출처 한 줄 인용 부재 |
| 영향 파일 | 9 | 13개 skill 매핑 + CLAUDE.md 정책 강도 갱신 + `.claude/commands` 심링크/`.codex/skills` 변환본 비영향 명시. 실제 파일 frontmatter 와 100% 일치 확인 (rp-specify·rp-prd = opus, 그 외 11개 = sonnet) |
| 롤백 | 8 | 단일 commit revert + 1줄 수정 + Claude Code 버그 시 우회 3 시나리오 분기. checksum/감사 트레일 별도 절차는 N/A (skill md 만 변경) |
| 검증 | 9 | 6 절차 — 머지 후 `/rp-prd` Opus 확인, 다음 턴 Sonnet 복귀, `/rp-specify` Opus, lint-docs CI, Codex 메타 리뷰, 4주 회고 정량 측정. 자동 전환 거동 검증을 인간 관찰에 의존하는 한계 있으나 메타 변경 특성상 적절 |
| 일관성 | 9 | CLAUDE.md L100~115 표 + harness-workflow.md L8~41 표 + 13개 skill frontmatter 가 완전 정합. rp-specify·rp-prd = Opus, 그 외 11개 = Sonnet 모두 동일 |
| 후속 영향 | 8 | 4주 후 회고 시점 정량 평가 명시. Opus override 예외(보안/동시성/아키텍처)는 CLAUDE.md L115 에 유지. codex 변환 파이프라인은 model 필드 무관 명시 |

**최저 = 종합: 8.0/10 → 통과**

## High/Critical
없음.

## Medium
- (M1) 검증 #1·#2 의 "응답 모델 확인" 방법이 모호. `/model` 슬래시 출력 또는 응답 메타 헤더 중 어느 쪽인지 운영자 가이드로 한 줄 보강 권장 (블로커 아님)
- (M2) `argument-hint` 와 `model:` 필드 순서가 13개 파일에서 통일되어 있으나 lint 자동 검증은 없음. 후속 PR 에서 `scripts/ops/lint-skill-frontmatter.sh` 추가 고려

## 정합성 체크 결과

| 검증 항목 | 결과 |
|---|:-:|
| 13개 skill 파일에 `model:` 필드 존재 | OK |
| rp-specify, rp-prd 만 `opus` (정확히 2개) | OK |
| 그 외 11개 모두 `sonnet` | OK |
| frontmatter `---` 열기/닫기 사이 위치 | OK |
| CLAUDE.md L100~111 표와 매핑 일치 | OK |
| harness-workflow.md L8~30 표와 매핑 일치 | OK |
| PRD 4섹션(이유·영향·롤백·검증) 충족 | OK |
