# 간소 PRD: 하네스 메타 Retro r1 High 4건 반영

## 변경 이유

PR #21(서브에이전트 리뷰 의무화) 배포 직후 회고(`docs/prd/harness-review-subagent-mandate/retro-r1.md`)에서 High 4건 확인:

| # | 회고 지적 | 영향 |
|:-:|-----------|------|
| H1 | `review-codex-meta.md` 파일 부재 — 메타 변경용 Codex 저장 규약 없음 | [3·4] 절차에서 Codex 누락 감지 불가 |
| H2 | `rp-ship` 진입 전 리뷰·산출물 파일 존재 검증 게이트 없음 | 증거 없는 배포 통과 |
| H3 | `node_modules/.astro/.claude/*.lock` 머지 커밋 포함 — `.gitignore` 미비 | 레포 위생·빌드 재현성 저하 |
| H4 | `meta-r{N}` 경로 규약이 CLAUDE.md L116 단일 선언 — rp-prd 간소 분기·rp-*-review 스킬은 미인지 | 스킬 자동 라우팅 불가 |

**목표**: 4건을 하네스 문서·스킬·`.gitignore`에 문자열 수준으로 반영. 실행 코드 변경 없음.

## 영향 파일

| 파일 | 변경 내용 |
|------|----------|
| `.gitignore` (루트) | `node_modules/`, `.astro/`, `.claude/*.lock` 추가 + `git rm --cached` 로 기 추적 제거 |
| `docs/harness-codex-review.md` | "적용 단계" 표에 메타 변경 행(meta → `review-codex-meta.md`) 추가. "⛔ 절대 규칙"에 메타도 Codex 1회 필수 명시 |
| `docs/skills/rp-plan-review.md` | 절차 3·6에 "하네스 메타 변경(간소 PRD)일 경우 `review-claude-meta-r{N}.md` + `review-codex-meta.md` 단일 리뷰로 대체" 분기 문구 추가 |
| `docs/skills/rp-eng-review.md` | 동일 분기 문구 추가 |
| `docs/skills/rp-code-review.md` | 동일 분기 문구 추가 (메타 변경이 코드 리뷰 단계까지 내려올 경우 대비) |
| `docs/skills/rp-prd.md` | "간소 PRD" 완료 조건에 "리뷰 파일명은 `-meta-r{N}` / `-codex-meta` 규약 사용" 1줄 추가 |
| `docs/skills/rp-ship.md` | "절차 1번 직전" 사전 체크 게이트 추가: `review-claude-*-r*.md` + `review-codex-*.md` + `retro-r*.md`(직전 회고가 반영 사이클일 때) 존재 검증. 누락 시 ship 중단 |
| `docs/harness-ship.md` | 동일 게이트 규칙 추가 기술 |

## 롤백 전략

단순 문서·`.gitignore` 변경. `git revert <merge-commit>` 또는 PR close로 즉시 원복. 실행 코드 영향 없음. `git rm --cached`는 원격 기록에만 영향 → revert 시 파일이 다시 추적되므로 후속 정리 필요하지만 데이터 손실 없음.

## 검증

- [ ] `.gitignore`에 3항목(`node_modules/`, `.astro/`, `.claude/*.lock`) 포함 + `git ls-files | grep -E "(node_modules|\.astro|\.claude/.*\.lock)"` 결과 0건
- [ ] `harness-codex-review.md` 적용 단계 표에 meta 행 존재 + 저장 경로 `review-codex-meta.md` 명시
- [ ] `rp-plan-review.md` · `rp-eng-review.md` · `rp-code-review.md` 각각에 "메타 변경 분기" 문자열 포함
- [ ] `rp-prd.md` 간소 PRD 섹션에 meta 리뷰 파일명 규약 1줄 포함
- [ ] `rp-ship.md` 사전 체크 게이트 절차 명시 + `harness-ship.md` 동기화
- [ ] Claude 서브에이전트 meta 리뷰 r1 통과 (역할 분리: 서브에이전트 채점만, Codex는 메인)
- [ ] `/codex:review --wait` 1회 실행 + `review-codex-meta.md` 저장
- [ ] High/Critical 지적 모두 반영 (있을 시)
