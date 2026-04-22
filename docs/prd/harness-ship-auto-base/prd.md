# 간소 PRD: rp-ship PR base 자동 결정

## 변경 이유

museum-finder T-23 (어드민 백엔드 가드) 통합 브랜치 머지 후 회고(`repositories/museum-finder/docs/research/retro-T23.md`) 에서 rp-ship 배포 영역 점수 **7.5/10 · 최저 6** 의 근본 원인으로 두 가지가 지목됨:

| # | 회고 이슈 | 근본 원인 |
|:-:|----------|----------|
| I1 | PR #16 초기 base=main 생성 (tasks.md 명시 규칙 = `feat/mvp-v1` 통합 브랜치). 사용자 명시 지시 없었다면 main 직행 가능 | rp-ship 스킬이 PR base 를 `gh pr create` 기본값(레포 default branch = `main`)에 의존. `tasks.md` / `CLAUDE.md` 의 통합 브랜치 선언을 읽지 않음 |
| I2 | 과거 PR #13·#14·#15 등 T-21·T-22가 실제 main 으로 직행 머지 → `feat/mvp-v1` 이 4커밋 뒤처진 stale 상태 방치 | 동일 — base 자동 결정 부재가 운영 누적 괴리로 이어짐 |

회고 개선 제안 #1 단독 반영 결정 (사용자 승인). **#2 통합 브랜치 전략 재정의는 미반영** — 이 PRD 범위 밖.

**목표**: `rp-ship` 스킬이 커밋/PR 생성 전에 **PR 대상 프로젝트의 통합 브랜치 선언을 자동 감지**해 `gh pr create --base` 에 명시 주입. 선언 없으면 현재 동작(레포 default branch) 유지. 실수로 main 직행 PR 생성 차단.

## 영향 파일

| 파일 | 변경 내용 |
|------|----------|
| `docs/skills/rp-ship.md` | (1) "자동 수행" 단계 4 (PR 상태 확인) 직전에 **"0. PR base 결정"** 단계 신설. **감지 규칙 (엄격)**: (a) 해당 프로젝트 `docs/tasks.md` 를 Read 하여 **라인 시작 앵커 `^\\|?\\s*통합 브랜치:\\s*(\\S+)` 로 정확히 1건** 매칭 추출. (b) `tasks.md` 감지 실패 시 프로젝트 `CLAUDE.md` 에서 동일 패턴 정확히 1건 재시도. (c) 둘 다 **없음** → default branch 폴백 + 로그 기록. (d) **2건 이상 매칭 / 값이 공백·`\\n` 포함 / 감지된 브랜치가 원격에 부재 → fail-closed**: ship 중단, 사용자 확인 요구. **느슨한 `feat/*` 추론 금지**. (2) `gh pr create` 호출 예시에 `--base <detected-base>` 명시 추가. (3) 재타깃 케이스: 기존 OPEN PR 이 감지된 base 와 다르면 `gh pr edit <num> --base <detected-base>` 로 보정 + **CI 재실행 대기 + 사용자 재승인 체크포인트 필수** (base 변경은 review diff 범위를 재정의하므로 자동 계속 금지). (4) **엣지·탈출구**: detached HEAD → 중단. 원격 base 브랜치 부재(`git ls-remote` 검증 실패) → 중단. 프로젝트 루트 미확인(`.git` 없음) → 중단. 사용자가 명시적 `--base <X>` 인자를 rp-ship 에 전달한 경우 감지 로직 비활성화(수동 오버라이드 우선) |
| `docs/harness-ship.md` | (1) "커밋 → PR → 배포" 흐름도에 `PR base 결정` 단계 삽입. (2) "CI 규칙" 표에 `PR base 자동 감지` 항목 추가 (tasks.md → CLAUDE.md → default branch 우선순위 명시) |
| `CLAUDE.md` (하네스 메타) | 절대 규칙 목록에 "**`rp-ship` PR base 자동 감지 게이트**: 프로젝트에 통합 브랜치 선언(`tasks.md` 의 `통합 브랜치:` 라인 또는 `CLAUDE.md` 의 `통합 브랜치:` 필드)이 있으면 **해당 브랜치를 PR base 로 고정**. 기본값(main) 폴백은 선언 부재 시에만" 한 줄 추가 |

**비변경**: 태스크별 `tasks.md` 포맷은 건드리지 않음. museum-finder `tasks.md` 의 `통합 브랜치: feat/mvp-v1` 라인이 이미 존재 — 기존 프로젝트 변경 없이 감지 동작.

## 롤백 전략

세 문서 변경만. 실행 코드·스크립트·설정 없음. `git revert <merge-commit>` 또는 PR close 로 즉시 원복. 롤백 후 rp-ship 은 기존 동작(`gh pr create` 기본 base = default branch) 으로 회귀.

## 검증

- [ ] `docs/skills/rp-ship.md` "자동 수행" 단계에 `0. PR base 결정` 서브섹션 존재 — 앵커링된 정규식 `^[\s\-\*|]*통합 브랜치:\s*`?([A-Za-z0-9/_\-]+)`?` 명시 + 정확히 1건 매칭 요구 + fail-closed 항목 (2건+ 매칭 / 공백 포함 / 원격 부재 / detached HEAD / 프로젝트 루트 미확인) 전부 포함
- [ ] `docs/skills/rp-ship.md` "PR 생성/재사용" 단계에 `gh pr create --base <detected-base>` 예시 반영 + 재타깃(`gh pr edit --base`) 시 **CI 재실행 + 사용자 재승인 체크포인트** 명시
- [ ] `docs/skills/rp-ship.md` 에 "수동 오버라이드" 명시 — 사용자가 `rp-ship --base <X>` 로 전달 시 자동 감지 비활성화
- [ ] `docs/harness-ship.md` 흐름도에 `PR base 결정 (fail-closed)` 단계 삽입 + "CI 규칙" 표에 항목 1건 추가 (감지 우선순위 + fail-closed 트리거)
- [ ] `CLAUDE.md` 절대 규칙 목록에 "rp-ship PR base 자동 감지 게이트" 한 줄 추가 — 앵커링 규칙·fail-closed·수동 오버라이드 3요소 간략 요약
- [ ] 기존 museum-finder `docs/tasks.md` 에 선언된 `통합 브랜치: feat/mvp-v1` 라인이 감지 regex 에 정확히 1건 매칭되는지 스킬 본문에 예시로 명시
- [ ] Claude 서브에이전트 meta 리뷰 증거 파일(`review-claude-meta-r{N}.md`) 존재 — 최신 회차 PASS
- [ ] `/codex:review --wait` 1회 실행 + `review-codex-meta.md` 저장
- [ ] Codex High/Critical 지적 모두 반영 (오탐 방지 · fail-closed 경로 · 수동 오버라이드)
- [ ] CLAUDE.md 트리 섹션(프로젝트 구조) 변경 없음 확인 — 본 변경은 절대 규칙 목록 1줄 추가만
