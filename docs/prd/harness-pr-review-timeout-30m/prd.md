# PRD: rp-pr-review 타임아웃 10분 → 30분

**상태:** Shipped (PR #89 값 변경 · 본 PR 결정 기록)
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

| # | 문제 | 근거 |
|:-:|------|------|
| 1 | `rp-pr-review` 리뷰어 상한 10분 → 리뷰 미완료 반환 여지 | 사용자 요청 |

## 결정 사항

| # | 항목 | 결정 | 기각 대안 | 근거 유형 |
|:-:|------|------|-----------|-----------|
| 1 | 리뷰어 타임아웃 | **30분(1800s)**. `rp-ship` 머지 전 최대 대기도 30분 | 10분 유지 | 사용자 결정(요청 번복): [`harness-token-question-prreview`](../harness-token-question-prreview/prd.md) 결정 4·4-1 "10분 유지" 번복 |

**트레이드오프:** 신규 PR 머지 최대 지연 10분 → 30분 증가 수용 (리뷰는 CI 대기와 병행).

## 영향 파일

| 파일 | 변경 |
|------|------|
| `docs/skills/rp-pr-review.md` (+ `.codex`) | 10분·600s → 30분·1800s |
| `docs/skills/rp-ship.md` (+ `.codex`) | 단계 5 머지 전 최대 대기 30분 |
| `docs/prd/harness-token-question-prreview/prd.md` | 결정 4·4-1 번복 링크 |

## 롤백 전략

`docs/skills/rp-pr-review.md`·`rp-ship.md` 값 원복 후 `python3 scripts/sync-codex-skills.py`.

## 검증

- 활성 스킬(`docs/skills/`·`.codex/skills/`) `10분`·`600` grep 0건
- `python3 scripts/sync-codex-skills.py --check` 통과
