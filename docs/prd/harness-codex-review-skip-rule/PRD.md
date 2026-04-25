# PRD — Codex 추가 리뷰 스킵 규칙

> 하네스 메타 변경(간소 PRD).

## 1. 변경 이유

| 항목 | 내용 |
|------|------|
| 현행 | [4][5][9] 단계 및 메타 단일 리뷰에서 `/codex:review --wait` **생략 불가**. Codex CLI 토큰 한도·rate limit·기능 미지원으로 Codex 실행 자체가 실패해도 워크플로우 차단 |
| 문제 | Codex 측 외부 사유(토큰 소진·rate limit·기능 미지원)로 인한 실행 불가 신호가 발생해도 워크플로우가 멈춰 작업 진행 불가. Claude 리뷰는 통과한 상태에서 Codex 외부 사유 단 한 번으로 전체 정지 |
| 목표 | Codex CLI가 토큰/기능 이슈 신호를 **명시적 패턴**으로 출력한 경우에 한해 1회 스킵 허용. 단계 진행은 계속하되 회피 사실은 영구 기록. **기타 비정상 종료(네트워크·플러그인 미설치·hang)는 기존대로 중단** |

## 2. 결정 사항

| 항목 | 결정 |
|------|------|
| 스킵 판정 | **AND 조건** 모두 충족 시에만 스킵. (a) `/codex:review --wait` 종료 후 exit code ≠ 0 (또는 0이라도 stderr/stdout에 후술 패턴이 명시) **AND** (b) stderr/stdout이 아래 "토큰·기능 신호 패턴 표" 중 1개 이상 매칭. 매칭 0건 → **비-스킵 = 워크플로우 중단** (사용자 보고) |
| 토큰·기능 신호 패턴 표 | 아래 표 참조 (대소문자 무시 정규식). `docs/harness-codex-review.md` `## 토큰·기능 신호 패턴` 섹션을 SSOT로 게시하고 스킬은 그 섹션 앵커를 링크 참조. 중복 정의 금지 |
| 재시도 | **없음**. 첫 신호로 즉시 스킵 확정 (사용자 결정 Q3) |
| Hang 타임아웃 | `/codex:review --wait` 호출 후 별도 wall-clock 타임아웃 **300초** (Codex 평균 리뷰 30~120초, P95 ~240초 가정의 여유 포함, 회고에서 조정 가능). 초과 시 SIGTERM 후 "비-스킵 = 중단" 분기. 타임아웃은 토큰/기능 신호로 간주하지 않음 |
| 증거 파일 | 기존 저장 경로(`<project-root>/docs/prd/[feature]/review-codex-{plan,eng,code,meta}.md`) **동일 파일에 작성**. 첫 줄 `# SKIPPED — codex token/feature signal` 헤더 + (a) UTC ISO 8601 타임스탬프, (b) 실행 cwd, (c) 명령 전체, (d) exit code, (e) stderr/stdout 원문 전체 (단 `(?i)(api[_-]?key\|token\|secret)\s*[:=]\s*\S+` 매칭 값은 `***REDACTED***` 치환), (f) 매칭된 패턴 # + 발견 위치, (g) 판정 사유 한 줄 |
| High/Critical 반영 | 스킵된 단계는 반영 대상 없음 (Codex 결과 자체가 없음). 다음 단계 즉시 진입 |
| 회고 처리 | `/rp-retro` 단계에서 **단순 언급만** (스킵 발생 단계·매칭 패턴명 한 줄). 누적 임계·트렌드 분석 없음 (사용자 결정 Q4) |
| 비-스킵 사유 (기존대로 중단) | 네트워크 오류, `codex login` 미완료, 플러그인 미설치, 패턴 매칭 0건 stderr, 타임아웃, 예측 불가 stderr → **기존대로 중단** + 사용자 보고. "토큰/기능" 신호 패턴이 아닌 모든 비정상 종료 |
| 적용 범위 | 단계 [4][5][9] + 하네스 메타 단일 리뷰. Claude 리뷰 서브에이전트 절차에는 영향 없음 |

## 2-B. 토큰·기능 신호 패턴 표 (SSOT 사본)

| # | 정규식 (case-insensitive) | 매칭 신호 카테고리 | 실제 Codex CLI 출력 예시 |
|---|---------------------------|---------------------|---------------------------|
| 1 | `rate.?limit` | rate limit | `Error: rate limit exceeded` |
| 2 | `usage.?limit` | usage cap (ChatGPT Pro 등) | `ERROR: You've hit your usage limit. Upgrade to Pro ...` |
| 3 | `token.*(limit\|exceed\|exhaust)` | 토큰 한도 | `token limit exceeded for this request` |
| 4 | `context.{0,3}(length\|window).*(exceed\|limit)` | 컨텍스트 한도 | `context length exceeded` |
| 5 | `quota` | quota 소진 | `monthly quota exhausted` |
| 6 | `(purchase\|upgrade).*(credit\|plan\|pro)` | 결제 안내 동반 한도 | `visit ... to purchase more credits` |
| 7 | `not (yet )?supported` | 기능 미지원 | `model not yet supported` |
| 8 | `unsupported (model\|feature)` | 기능 미지원 | `unsupported feature: --base on detached HEAD` |
| 9 | `model.*not.*available` | 모델 미가용 | `model gpt-5.5 not available in this region` |

신규 패턴 추가 시 본 표를 갱신하고 `docs/harness-codex-review.md` 동일 섹션을 동기화. 정규식 변경은 동작 시뮬레이션 양방향(검증 §5) 통과 후 머지.

## 2-A. 대안 탐색

| 대안 | 장점 | 단점 | 채택 |
|------|------|------|------|
| A. 항상 차단 유지(현행) | 안전성 최대, 외부 의존 명시 | 외부 사유 1건으로 전체 워크플로우 정지, 가용성 최악 | 미채택 |
| B. 1회 재시도 후 스킵 | rate limit 일시 완화 케이스 자동 회복 | 토큰 한도·기능 미지원은 재시도해도 동일, 응답 시간 2배 증가 | 미채택 |
| C. 사용자 수동 승인 후 스킵 | 인간 판단 보강 | 자동화 워크플로우 정지, 운영자 부담 | 미채택 |
| **D. 패턴 매칭 즉시 스킵 (채택)** | 외부 사유 즉시 회피, 회피 사실 영구 기록, AND 조건으로 오용 방지 | 패턴 미스매치 시 안전망 부족 | **채택** — 사용자 Q3 결정 일치. 패턴 미스매치 리스크는 "비-스킵=중단" 안전망으로 커버 |

## 3. 영향 파일

| 파일 | 변경 내용 |
|------|----------|
| `docs/harness-codex-review.md` | 절대 규칙 갱신: "생략 불가" → "토큰/기능 패턴 매칭 시 1회 스킵 허용". **토큰·기능 신호 패턴 표 SSOT 게시**, AND 판정 로직, 300초 타임아웃, 증거 파일 7개 항목 명시 |
| `docs/skills/rp-plan-review.md` | Codex 실행 절차에 스킵 분기 추가 (패턴 표는 위 SSOT 참조 링크) |
| `docs/skills/rp-eng-review.md` | 동일 |
| `docs/skills/rp-code-review.md` | 동일 |
| `docs/skills/rp-retro.md` | Codex 스킵 발생 시 회고 단순 언급 항목 1줄 추가 |
| `CLAUDE.md` | "[4][5][9] Codex 추가 리뷰 필수" 절대 규칙에 스킵 예외 1줄 + 패턴 표 출처 링크 추가 |
| `.codex/skills/rp-{plan,eng,code,retro}-review/SKILL.md` | Codex 변환본 동기화 (`scripts/sync-codex-skills.py --install-user`) |

## 4. 롤백

| 단계 | 절차 |
|------|------|
| 1 | `git revert <merge-commit>` (PR 단일 머지 커밋 되돌리기) |
| 2 | Codex 스킬 변환본 재동기화: `rtk python3 scripts/sync-codex-skills.py --install-user` |
| 3 | 기존 절대 규칙(생략 불가) 복원 확인: `grep "생략 불가" docs/harness-codex-review.md` |

영향 범위가 문서·스킬 정의에 한정되어 코드/DB 마이그레이션 없음. 롤백 위험 낮음.

## 5. 검증

| 항목 | 방법 |
|------|------|
| 문서 정합성 | `harness-codex-review.md` ↔ `rp-{plan,eng,code,retro}-review.md` ↔ `CLAUDE.md` 절대 규칙 표현 일치 (수동 grep) |
| 스킬 동기화 | `rtk python3 scripts/sync-codex-skills.py --check` 통과 |
| 정적 시뮬레이션 | 스킵 헤더 형식대로 `review-codex-meta.md` 더미 1건 작성해 7개 항목(헤더·타임스탬프·cwd·명령·exit code·stderr·매칭 패턴·사유) 모두 표현되는지 확인 |
| **동작 시뮬레이션 (양방향)** | (1) 가짜 stderr `rate limit exceeded for tokens` 주입 → 스킵 헤더 자동 생성 + 다음 단계 진입 확인. (2) 가짜 stderr `network unreachable` 주입 → 패턴 매칭 0건 → 워크플로우 중단 + 사용자 보고 확인. 두 케이스 모두 PASS여야 검증 통과 |
| 회고 반영 | `rp-retro` 스킬 항목에 "Codex 스킵 발생 단계·패턴명 한 줄" 항목 존재 확인 |
| 비-스킵 보호 | "패턴 매칭 0건·타임아웃·기타 비정상 종료는 기존대로 중단" 문구가 `harness-codex-review.md` + 3개 리뷰 스킬 + `CLAUDE.md`에 모두 명시 |
| 패턴 SSOT | 토큰·기능 신호 패턴 표가 `harness-codex-review.md` `## 토큰·기능 신호 패턴` 섹션에만 게시되고 다른 파일은 해당 앵커로 링크 참조하는지 확인 (중복 정의 금지) |
| 마스킹 검증 | 가짜 stderr `api_key=sk-abc123` 주입 → 증거 파일에 `***REDACTED***` 치환 확인 (CLAUDE.md 민감 정보 금지 규칙 준수) |
