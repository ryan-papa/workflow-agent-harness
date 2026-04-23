# 간소 PRD: 하네스 규칙 문서 전반 다듬기

## 변경 이유

하네스 규칙 문서(`CLAUDE.md`, `docs/harness-*.md`, `docs/skills/rp-*.md`)가 누적 업데이트로 다음 문제가 생김:

| # | 관찰 | 원인 |
|:-:|------|------|
| O1 | 동일 규칙을 여러 파일에서 약간씩 다른 표현으로 반복 설명 (중복·표현 편차) | 단계별 회고·핫픽스가 개별 문서에 국소 삽입됨 |
| O2 | 섹션 제목 레벨(`##`/`###`) 혼재, 파일별 목차성 편차 | 작성자·시기별 스타일 차이 |
| O3 | 긴 산문 문장·구어체 잔존 | CLAUDE.md 문체 규칙(구어체 금지·테이블/리스트 우선) 미적용 구간 |
| O4 | 한글·영어 혼용 표기 불일치 | 표준(한글 우선·필요 시 영어 병기) 미정의 |

**목표**: 규칙 의도·문구 원문은 보존하면서, 주변 설명문·섹션 제목 레벨·리스트/표 구조만 정리해 가독성·일관성을 높인다. 규칙 텍스트(앵커·정규식·명령어·브랜치명·파일 경로) 변경 금지.

## 영향 파일

### 범위 (총 24개)

| 파일 군 | 개수 | 파일 |
|---------|:---:|------|
| 루트 | 1 | `CLAUDE.md` |
| 공통 문서 | 10 | `docs/harness-workflow.md`, `docs/harness-prd.md`, `docs/harness-dev.md`, `docs/harness-qa.md`, `docs/harness-code-review.md`, `docs/harness-codex-review.md`, `docs/harness-ship.md`, `docs/harness-design.md`, `docs/harness-readme.md`, `docs/harness-db.md` |
| 스킬 | 13 | `docs/skills/rp-workflow.md`, `docs/skills/rp-amend.md`, `docs/skills/rp-init.md`, `docs/skills/rp-specify.md`, `docs/skills/rp-prd.md`, `docs/skills/rp-plan-review.md`, `docs/skills/rp-eng-review.md`, `docs/skills/rp-task.md`, `docs/skills/rp-dev.md`, `docs/skills/rp-qa.md`, `docs/skills/rp-code-review.md`, `docs/skills/rp-ship.md`, `docs/skills/rp-retro.md` |

### 변경 성격 (공통)

| 유형 | 허용 | 금지 |
|------|------|------|
| 문장 간결화 | 장황한 문장 → 단문/리스트 분리 | 규칙 텍스트 수정 |
| 중복 표현 제거 | 바로 인접한 중복 문장 제거 | 규칙 문구 자체 병합·삭제 |
| 섹션 제목 레벨 통일 | `##` → `###` 등 레벨 재정렬 | 섹션 삭제·신설 |
| 리스트/표 정리 | 테이블 헤더 통일, 불릿 기호 통일, 중첩 깊이 ≤3 | 표 항목 의미 변경 |
| 표기 통일 | 한글 우선, 필요 시 괄호로 영어 병기 | 명령어·변수명·경로의 영문 변경 |

### 비변경 (불변 대상)

- **규칙 텍스트 원문**: `⛔`·`**` 강조 블록 안의 실제 규칙 문구 (예: "코드 전에 PRD 문서 먼저 업데이트 + 리뷰", `rp-ship PR base 자동 감지 게이트` 내부 정규식 `^[\s\-\*|]*통합 브랜치:\s*`?([A-Za-z0-9/_\-]+)`?`, `/codex:review --wait` 등)
- **파일 경로·링크 상대 경로** (`../../CLAUDE.md`, `docs/skills/`, `docs/prd/[feature]/review-*.md` 등)
- **스킬 frontmatter** (`description`, `name` 등 YAML)
- **파일 신설·삭제·분리·이동** 없음
- **200줄 초과 파일**도 현행 유지 (분리 작업은 본 스코프 제외)

### 표기 규칙 (한글 우선·영어 병기 상세)

| 대상 | 처리 |
|------|------|
| 일반 설명문·섹션 제목 | 한글 |
| 도메인 전문 용어 첫 등장 | 한글(영문) 병기 — 예: "포그라운드(foreground)", "게이트(gate)" |
| 약어(CI, PR, QA, PRD, MCP 등) | 영문 그대로 |
| 명령어·플래그·변수명·파일 경로·브랜치명·URL | 영문 그대로 (백틱 유지) |
| 고유명사(Claude, Codex, GitHub, Playwright 등) | 영문 그대로 |
| 이미 한글 표기로 정착된 용어(커밋·브랜치·태스크·머지) | 한글만 |

### 리스크 및 완화책

| # | 리스크 | 완화책 |
|:-:|--------|--------|
| R1 | 규칙 텍스트 의도치 않은 변경으로 의미 훼손 | 검증 체크리스트의 "규칙 원문 앵커 diff" 전수 점검 + Codex meta 리뷰 |
| R2 | 상대 경로 링크 깨짐 | 검증의 "상대 경로 링크 유효성" 전수 점검 |
| R3 | 섹션 삭제·병합으로 인한 외부 앵커 링크 파손 | 섹션 삭제·신설 금지 원칙 명시 (비변경 섹션) |
| R4 | 강조 블록(`⛔`, `**`) 유실로 규칙 가중치 저하 | 규칙 문구 원문 보존 조항에 강조 기호 포함 |
| R5 | 대규모 diff 로 리뷰 품질 저하 | 파일군(루트·공통·스킬) 단위로 분할 커밋 가능 (선택) |
| R6 | 한글·영어 병기 규칙 해석 편차 | 위 표기 규칙 표를 단일 진리 원천(SSOT)으로 사용 |

## 롤백 전략

문서 변경만. 실행 코드·스크립트·설정 없음. `git revert <merge-commit>` 또는 PR close 로 즉시 원복. 롤백 후 규칙 의미·동작 동일.

## 검증

- [ ] 규칙 텍스트 원문 diff 검증 절차 (순서대로 실행):
  1. `git diff --word-diff=porcelain main -- CLAUDE.md docs/harness-*.md docs/skills/rp-*.md` 실행해 단어 단위 변경 전수 확인
  2. `git diff main -- CLAUDE.md docs/harness-*.md docs/skills/rp-*.md | grep -E '^[+-]' | grep -v '^[+-]{3}' | grep -iE '⛔|필수|금지|무시|즉시 중단|fail-closed|앵커|정규식|^\+.*`[^`]+`'` 로 규칙성 문구 포함 라인 추출 후 규칙 의미 불변 검토
  3. 아래 앵커/문구가 문자 단위로 동일하게 보존됨을 개별 확인
  - `^[\s\-\*|]*통합 브랜치:\s*`?([A-Za-z0-9/_\-]+)`?` (CLAUDE.md · rp-ship.md · harness-ship.md)
  - `/codex:review --wait`
  - `review-claude-{plan,eng,code,meta}-r{N}.md` · `review-codex-{plan,eng,code}.md`
  - `subagent_type=general-purpose`
  - 절대 규칙 목록 각 항목의 핵심 키워드(예: "main 직접 수정 금지", "CI 통과 전 머지 금지", "feat 브랜치 직행 배포 금지")
- [ ] 상대 경로 링크 유효성: Markdown 링크 문법 전수 점검, 깨진 링크 0건
- [ ] 섹션 제목 레벨 일관성: 각 파일 최상단 `#` 1개 + 이후 `##`·`###` 레벨 스킵 없음
- [ ] 표기 일관성: 주 본문 한글, 전문 용어는 필요 시 괄호 영어 병기 (예: "포그라운드(foreground)")
- [ ] 파일 신설·삭제·이동 0건 (`git status` 로 `renamed`/`deleted`/신규 파일 없음 확인, PRD 디렉터리·리뷰 증거 제외)
- [ ] `git diff --stat` 상 대상 24개 파일(루트 1 + 공통 10 + 스킬 13) 중 **22~24개** 변경, 미변경 파일은 "이미 정돈됨" 판정 근거를 `polish-report-*.md` 에 기록. 대상 외 파일 변경 0건 (PRD/리뷰 증거 파일 제외)
- [ ] 강조 기호(`⛔`, `**강조**`) 사용 횟수가 변경 전후 동일 (규칙 가중치 보존)
- [ ] Claude 서브에이전트 meta 리뷰 증거 파일(`review-claude-meta-r{N}.md`) 존재 — 최신 회차 PASS
- [ ] `/codex:review --wait` 1회 실행 + `review-codex-meta.md` 저장
- [ ] Codex High/Critical 지적 모두 반영
