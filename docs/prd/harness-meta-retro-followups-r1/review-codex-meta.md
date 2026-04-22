# Codex Meta Review — harness-meta-retro-followups-r1

- 실행: `codex review --uncommitted --title "harness-meta-retro-followups-r1"`
- cwd: `/Users/hose.kim/Claude/claude-projects` ✅
- 모델: gpt-5.4 / sandbox: read-only
- session: 019db283-d75f-7b42-a083-f846fb4e143d

## 총평

> The patch introduces contradictory artifact names for meta Codex reviews and a ship-gate check that does not actually detect partially missing review evidence. Those issues break the workflow this change is trying to enforce.

## 지적 (P2 × 4 — 하네스 규칙상 High/Critical 미해당이나, 본 PRD 게이트 자체를 무효화하는 실효성 이슈로 판단하여 전건 반영)

| # | 경로 | 내용 |
|:-:|------|------|
| F1 | `docs/skills/rp-plan-review.md:23-26` | step 3은 meta 변경 시 `review-codex-meta.md` 저장 지시, step 6은 여전히 `review-codex-plan.md` 지시 — 자체 모순 |
| F2 | `docs/skills/rp-eng-review.md:23-26` | 동일 모순 (`review-codex-eng.md` vs `review-codex-meta.md`) |
| F3 | `docs/skills/rp-code-review.md:77-83` | 동일 모순 (`review-codex-code.md` vs `review-codex-meta.md`) |
| F4 | `docs/skills/rp-ship.md:27-32` | 사전 체크 `ls review-claude-*-r*.md review-codex-*.md`는 한 종류라도 있으면 통과 — 부분 누락 감지 불가, 게이트 실효성 없음 |

## 반영

| # | 반영 내용 |
|:-:|----------|
| F1 | rp-plan-review.md L25 Codex stdout 저장 경로 뒤에 "(하네스 메타 변경일 경우 `review-codex-meta.md`)" 삽입 |
| F2 | rp-eng-review.md L25 동일 삽입 |
| F3 | rp-code-review.md L82 동일 삽입 |
| F4 | rp-ship.md 사전 체크 게이트를 PRD 유형별 개별 파일 존재 검증 스크립트로 교체 (일반 기능: Codex 3종 + Claude 회차 3단계 / 메타: meta 2종). 부분 존재 시 exit 1 |

## 참고 정보 (미반영)

없음. 4건 모두 반영.
