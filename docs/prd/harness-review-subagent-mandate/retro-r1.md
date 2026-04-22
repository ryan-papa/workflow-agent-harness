# Retro r1 — 하네스 메타 변경 PR #21 회고

- 시점: 2026-04-22 (PR #21 머지 익일)
- 트리거: rp-retro 누적 2건 중 (a) 하네스 메타 변경 배포 직후 회고

## 영역별 점수

| 영역 | 평균 | 핵심 지적 |
|------|:---:|----------|
| 리뷰 | 7.2 | `review-codex-meta.md` 미존재, "Codex 1회 통과" 증거 부재 |
| 배포 | 8.0 | node_modules/.astro/.lock 머지 커밋 포함, .gitignore 누락 |
| 규칙 품질 | 7.0 | meta 경로 규약이 CLAUDE.md에만 존재, rp-*-review 스킬에 없음 |
| **종합** | **7.4** | |

## 단계별 평가

| 단계 | 점수 | 준수 | 비고 |
|------|:---:|:---:|------|
| [3] 간소 PRD | 9/10 | ✅ | 4섹션 준수 |
| meta-r1 (Claude 서브에이전트) | 8/10 | ✅ | 미달 판정 → 재작성 |
| meta-r2 | 9/10 | ✅ | 회차 보존 정상 |
| Codex meta 리뷰 | 3/10 | ❌ | 산출물 파일 부재 (High) |
| [11] rp-ship | 8/10 | ⚠️ | feat·CI·PR 규약 ✅ / 산출물 보고·README 검증 증거 ❌ |
| 레포 위생 | 5/10 | ❌ | node_modules/.astro/.lock 추적 (High) |

## 교차 분석 — 근본 원인

| # | 원인 |
|---|------|
| C1 | dogfooding 공백: 메타 변경은 "규칙"을 고치지만 그 규칙(Codex 저장·README 검증·산출물 보고)을 이번 배포에서 본인이 미준수 |
| C2 | meta 분기 규약 부재: CLAUDE.md만 meta 키워드 인지, rp-prd·rp-*-review·rp-ship은 모름 → 스킬 자동 라우팅 불가 |
| C3 | 증거 자동 수집 메커니즘 없음: 서브에이전트·Codex 실행 여부가 "자기 선언", CI·훅에서 파일 존재 검증 부재 |

## 사용자 승인 개선 (11번 = High 4건)

| # | 제안 | 심각도 |
|:-:|------|:----:|
| 1 | `harness-codex-review.md`에 meta 분기 명시 + `review-codex-meta.md` 파일명 공식화 | High |
| 2 | `rp-ship` 진입 전 파일 존재 체크(`review-claude-*-r*.md` + `review-codex-*.md` + `ship-checklist.md`) | High |
| 3 | `.gitignore` 강화 + `git rm --cached` (node_modules/.astro/.claude/*.lock) | High |
| 4 | meta 경로(`review-claude-meta-r{N}.md`)를 rp-plan/eng/code-review + rp-prd 간소 분기에 명시 | High |

## 미반영 (기각 · TODO)

| # | 제안 | 상태 |
|:-:|------|:---:|
| 5 | 기술 실패 판정 기준 표 | 보류 |
| 6 | rp-workflow·rp-amend 서브에이전트 강제 링크 | 보류 |
| 7 | CLAUDE.md L116 테이블 분해 | 보류 |
| 8 | 서브에이전트 호출 메타 자동 기록 | 보류 |
| 9 | Codex High 반영 후 재검증 루프 명문화 | 보류 |

## 반영 경로

- 브랜치: `feat/harness-meta-retro-followups-r1`
- 간소 PRD: `docs/prd/harness-meta-retro-followups-r1/prd.md`
- 리뷰: `review-claude-meta-r1.md` + `review-codex-meta.md`
- 배포: `rp-ship`
