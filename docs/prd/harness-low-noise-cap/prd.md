# PRD: Low 지적 후속 PR 연쇄 차단

**상태:** Approved ([4] 8.06 · [5] 8.2 · [9-코드] 8.14, 인프라 축 메타 skip)
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

| # | 문제 | 근거 |
|:-:|------|------|
| 1 *(핵심)* | 후속 PR 마다 새 독립 리뷰어가 새 Low 를 생산 → Low 후속 PR 연쇄(#83→#84→#85→#86) | 사용자: "언제까지 low 가 나오냐", "한번에 처리해" |
| 2 | PR #86 rp-pr-review Low: `docs/skills/` 전용 예외 조건이 간소 PRD 파일(`docs/prd/`)을 포함해 사실상 발동 불가 | PR #86 리뷰 |

## 결정 사항

| # | 항목 | 결정 | 기각 대안 | 근거 유형 |
|:-:|------|------|-----------|-----------|
| 1 | [9] Low | 같은 PR 안에서 자동 반영, **반영 후 재리뷰·재검증 없음**, Low 만으로 후속 PR 생성 금지. 동작·분기 변경이 필요한 반영은 Medium 재분류 → 반영 검증 | Low 반영마다 재검증 — 연쇄 원인 | 창업자 직감 (사용자 지시) |
| 2 | rp-pr-review 출력 | 하네스 연동 호출은 **Medium 이상만 출력**, Low 는 `Low n건 (생략)` 1줄. 후속 PR 제안은 Medium 이상만. 수동 호출은 전체 출력 | Low 미검출 지시 — 리뷰어 기준 주입 금지 위반 | 창업자 직감 (사용자 지시) |
| 3 | 예외 조건 | `docs/skills/` 전용 예외 판정에서 PRD 산출물 `docs/prd/` 는 무시 — 포함돼도 예외 유지 (절대 규칙 SSOT + rp-prd·rp-workflow) | 예외 폐지 — 범위 변경 | 엔지니어 선호 |

충돌 확인: 절대 규칙 "리뷰 지적 반영 검증" ③ — Low 예외를 SSOT ③ 에 명시해 해소 ([5] 지적). PR #85 Q1 "Low 자동 반영" 유지

## 영향 파일

| 파일 | 변경 |
|------|------|
| `docs/harness-code-review.md` · `docs/skills/rp-code-review.md` (+ `.codex`) | 처리 원칙·이슈 처리 표: Low 재검증 없음·후속 PR 금지·동작 변경 시 Medium 재분류 |
| `docs/harness-absolute-rules.md` | "리뷰 지적 반영 검증" ③ Low 예외 명시 |
| `docs/skills/rp-pr-review.md` (+ `.codex`) | 연동 호출 Medium 이상 출력, Low 건수만 |
| `docs/harness-ship.md` | 최초 PR 독립 리뷰 행 |
| `docs/harness-absolute-rules.md` · `docs/skills/rp-prd.md` · `docs/skills/rp-workflow.md` (+ `.codex`) | 예외 조건 `docs/prd/` 제외 |

## 검증

- 메타 QA: 500줄·내부 링크·`.codex` 링크, `sync-codex-skills.py --check`
- 서브에이전트 리뷰 [4]∥[5], [9-코드] (인프라 축 메타 skip)
- 즉시 확인: 본 PR 의 rp-pr-review 출력이 Low 를 건수 1줄로만 표기

## 롤백 전략

PR revert — 문서 국소 변경, 코드 의존 0건.
