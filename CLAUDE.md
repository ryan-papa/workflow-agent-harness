# Claude Rules

## Interaction

업무/지시 수신 또는 기능 추가/변경 요청 시 질문 절차:
- 질문 수: 최소 2개, 최대 15개
- **질문은 1개씩 대화형으로 진행** (한번에 모아서 제시 금지)
- 각 질문마다 객관식 4개 제공
- 각 선택지에 추천 점수 표기 (10점 만점)
- 최고 점수 항목에 "★ 추천" 표시
- 주관식 답변 항목 별도 제공
- 답변 수신 후 다음 질문 진행
- **재귀적 구체화:** 질문 과정에서 새 기능이 추가되면, 그 기능도 동일한 질문 절차로 구체화 (모든 기능이 구체화될 때까지 반복)

**질문 형식 예시:**
> Q1. [질문 내용]
> 1. 선택지 1 — 7/10
> 2. 선택지 2 — 9/10 ★ 추천
> 3. 선택지 3 — 5/10
> 4. 선택지 4 — 6/10
> 5. 직접 입력: ___

## Document Style

| 규칙 | 내용 |
|------|------|
| 문체 | 구어체 금지, 간결·명료 |
| 구조 | 테이블/리스트 우선, 산문 지양 |
| 분량 | 파일당 200줄 이하 |
| 초과 시 | **역할/책임 단위로 파일 분리** (텍스트 압축이 아닌 영역 분리) |
| 코드 | 코드 직접 작성 금지, 파일 링크 참조로 대체 |
| **자동 정합성** | docs/ 변경 시 서브에이전트가 CLAUDE.md 트리+링크 자동 동기화 (사용자에게 변경 요약만 출력) |
| **하네스 동기화** | 하네스 문서(원본) 변경 시 관련 스킬(`docs/skills/`) + CLAUDE.md를 즉시 갱신 |
| **⛔ 민감 정보 금지** | 다음 정보는 **어떠한 문서·커밋 메시지에도 작성 금지**: (1) 인프라 — 호스트·계정명·포트·인증서 경로·내부 IP, (2) 개인 식별 정보 — 실명·개인 이메일·개인 연락처·SNS ID, (3) 시크릿 — 비밀번호·API 키·토큰·개인키. 환경변수 참조(`$DB_HOST`)로 대체하고 실제 값은 "관리자에게 별도 문의"로 안내. 공개키는 안전하지만 프로파일링 방지 위해 로컬 파일(`.gitignore`)에 분리 |

## Project Structure

```
claude-projects/
├── docs/                       # 공통 문서·규칙
│   ├── harness-workflow.md     # 전체 플로우 (12단계)
│   ├── harness-prd.md          # PRD 작성 + 2단계 리뷰
│   ├── harness-dev.md          # 개발 (브랜치·태스크·테스트)
│   ├── harness-qa.md           # QA + 콘텐츠 검수
│   ├── harness-code-review.md  # 코드리뷰 상세 기준 (7항목)
│   ├── harness-codex-review.md # Codex 추가 리뷰 규칙 (4·5·9, 1회, High/Critical 반영)
│   ├── harness-ship.md         # 산출물 보고 + 배포
│   ├── harness-design.md       # UI 디자인 원칙
│   ├── harness-readme.md       # README 작성 규칙
│   ├── security-guide.md       # 시크릿·자격증명 원칙 (sops+age)
│   ├── security/
│   │   ├── secrets-management.md       # sops+age 세팅·운영·rotation
│   │   └── recipients.local.md         # (git 제외) 공개키 레지스트리
│   ├── prd-template.md         # PRD 템플릿
│   ├── templates/              # 문서·CI·시크릿 템플릿
│   │   ├── readme-opensource.md
│   │   ├── readme-service.md
│   │   ├── ci-pr.yml
│   │   ├── sops.yaml.template          # .sops.yaml 초안 (플레이스홀더)
│   │   └── env.example.template        # .env.example 초안
│   └── skills/                 # 하네스 스킬 (rp-*)
│       ├── rp-workflow.md      # 오케스트레이터 (신규 프로젝트·기능)
│       ├── rp-amend.md         # 오케스트레이터 (기존 프로젝트 수정·추가, init 스킵)
│       ├── rp-init.md          # [1] 프로젝트 초기화
│       ├── rp-specify.md       # [2] 구체화
│       ├── rp-prd.md           # [3] PRD 작성
│       ├── rp-plan-review.md   # [4] 기획 리뷰
│       ├── rp-eng-review.md    # [5] 엔지니어링 리뷰
│       ├── rp-task.md          # [6] 태스크 분해
│       ├── rp-dev.md           # [7] 개발
│       ├── rp-qa.md            # [8] QA / 콘텐츠 검수
│       ├── rp-code-review.md   # [9] 코드 리뷰
│       ├── rp-ship.md          # [11] 커밋→PR→배포
│       └── rp-retro.md         # [12] 회고
├── repositories/               # 프로젝트별 레포 (git 제외)
│   └── [project]/
│       ├── CLAUDE.md
│       ├── README.md
│       └── docs/prd/
├── .gitignore
├── .codex/skills/             # Codex용 프로젝트 로컬 rp-* 스킬
├── AGENTS.md                  # Codex용 하네스 어댑터
└── CLAUDE.md
```

**설정 우선순위:** 프로젝트(`repositories/[project]/CLAUDE.md`) > 공통(`docs/`)

**서브 레포 CLAUDE.md 참조 규칙:**
- 서브 레포 CLAUDE.md 최상단에 상위 공통 규칙(`../../CLAUDE.md`) 참조 문구 필수
- **⛔ 서브 레포 진입 시 `../../CLAUDE.md`를 반드시 Read로 읽을 것 (참조 문구만으로는 자동 적용되지 않음)**
- 프로젝트 로컬 규칙 1순위, 공통 규칙 2순위 (충돌 시 프로젝트 우선)
- 신규 레포 생성 시 `rp-init`이 자동 삽입

## Harness Engineering

→ [`docs/harness-workflow.md`](docs/harness-workflow.md)

| 단계 | 스킬 | 권장 모델 | 내용 |
|:----:|------|:--:|------|
| 1 | `rp-init` | Sonnet | 초기화 |
| 2 | `rp-specify` | **Opus** | 구체화 (신규 도메인 추론) |
| 3 | `rp-prd` | **Opus** | PRD 작성 (종합 사고) |
| 4 | `rp-plan-review` | Sonnet | 기획 리뷰 (**Codex 추가 1회**) |
| 5 | `rp-eng-review` | Sonnet | 엔지니어링 리뷰 (**Codex 추가 1회**) |
| 6 | `rp-task` | Sonnet | 태스크 분해 |
| 7 | `rp-dev` | Sonnet | 개발 |
| 8 | `rp-qa` | Sonnet | QA / 콘텐츠 검수 |
| 9 | `rp-code-review` | Sonnet | 코드 리뷰 (7항목, **Codex 추가 1회**) |
| 10 | — | Sonnet | 산출물 보고 → 커밋·PR 자동 진행 |
| 11 | `rp-ship` | Sonnet | 커밋 → PR → CI → 머지 → 배포 |
| 12 | `rp-retro` | Sonnet | 회고 |

**모델 선택 정책:** `rp-specify`·`rp-prd` 만 **Opus**, 그 외 모든 단계는 **Sonnet** 권장. 비용·속도 절감 + Opus 의 추론 우위는 신규 도메인 구체화·PRD 초안에 집중. 사용자가 `/model sonnet` 또는 `/model opus` 슬래시 커맨드로 단계 전환 시 즉시 전환. 본 정책은 **권장**이며 강제 전환 자동화는 별도 후속.

**상세 표·근거:** [`docs/harness-workflow.md`](docs/harness-workflow.md)

**오케스트레이터:**
- `rp-workflow` — 신규 프로젝트·기능 (init부터 전 단계)
- `rp-amend` — 기존 프로젝트 기능 수정·추가 (init 스킵, specify부터 전 단계 Full PRD)
**자동 전환:** 모든 단계 완료 시 다음 단계 자동 진입. 사용자 확인 없이 즉시 진행. 커밋·PR·**머지(자동 머지 가드 4종 AND 충족 시)까지 자동**. 배포[11] 완료 후 회고[12]는 **사용자 명령 시에만 실행** (자동 진입 없음).
- 구체화 완료 → PRD 작성 자동 진입 (확인 질문 금지)
- PRD 완료 → 기획 리뷰 자동 진입
- 각 단계 완료 시 "다음 단계로 갈까요?" 질문 금지 — 바로 진행

**스킬 위치:** [`docs/skills/`](docs/skills/)

**Codex 스킬 동기화:** `docs/skills/rp-*.md`가 원본이다. 변경 후 `.claude/commands/` 심링크와 `.codex/skills/rp-*/SKILL.md` 변환본을 함께 갱신한다. 수동 확인은 `rtk python3 scripts/sync-codex-skills.py --check`, 로컬 설치는 `rtk python3 scripts/sync-codex-skills.py --install-user`.

**⛔ 하네스 절대 규칙 (예외 없음):**
- **[리뷰 단계 서브에이전트 필수]** `/rp-plan-review` · `/rp-eng-review` · `/rp-code-review` 의 Claude 리뷰는 **반드시 Agent 툴로 분리된 서브에이전트(`subagent_type=general-purpose`)가 실행**한다. 메인 에이전트가 본인이 작성한 PRD·코드를 자체 채점하는 행위 **전면 금지**. 이해충돌·관성 편향 방지. 서브에이전트는 메인 대화 컨텍스트 없이 대상 파일만 읽고 독립 판정. **역할 분리**: 서브에이전트는 Claude 채점만, `/codex:review` 실행·결과 저장은 메인 에이전트. **Fallback**: 서브에이전트 호출 기술적 실패(Agent 툴 오류·토큰 초과·형식 오류) 최대 2회 재호출 → 실패 지속 시 사용자에게 즉시 보고, **메인 셀프 채점 우회 금지**. 채점 결과 "미달"은 PRD 재작성 후 새 서브에이전트 재실행 (평가 미달과 기술 실패 구분). **증거 저장**: 매 회차 결과를 `<project-root>/docs/prd/[feature]/review-claude-{plan,eng,code,meta}-r{N}.md` 로 저장 (N=1,2,3 회차). `{meta}`는 간소 PRD(하네스 메타 변경) 단일 리뷰 전용. 파일 덮어쓰기 금지, 매 회차 새 파일로 보존 (감사·회고용).
- 기능 변경 시 코드 전에 PRD 문서 먼저 업데이트 + 리뷰
- 테스트 코드 없이 커밋/머지 절대 금지
- 테스트·빌드 미통과 시 다음 단계 진행 금지
- **QA·코드 리뷰 단계 생략 금지 (게이트 강화)**: 두 단계 모두 완료 여부를 배포 전 체크하고, 하나라도 미수행이면 배포 차단. "단위 테스트 통과 = QA 대체 불가"
- **[4][5][9] Codex 추가 리뷰 필수**: Claude 리뷰 통과 후 `/codex:review --wait` 1회 포그라운드 실행 (wall-clock 300초 타임아웃). cwd는 **해당 PRD 프로젝트 루트** (일반 기능 `repositories/[project]/`, 하네스 메타 변경 `claude-projects/`). 점수화 없음. High/Critical 지적은 반영 후 다음 단계 진입. 결과는 `<project-root>/docs/prd/[feature]/review-codex-{plan,eng,code,meta}.md`에 저장. **단, Codex CLI가 토큰/기능 신호 패턴**([`docs/harness-codex-review.md`](docs/harness-codex-review.md) "토큰·기능 신호 패턴" 섹션 SSOT)을 명시적으로 출력하면 1회 스킵 후 다음 단계 진입(SKIPPED 헤더 + 7항목 증거 저장 필수). 그 외 비정상 종료(네트워크·login·플러그인·hang·매칭 0건)는 **기존대로 중단 + 사용자 보고**, 자동 재시도 금지
- 산출물 보고 없이 배포 진행 금지 (커밋·PR은 산출물 보고 후 자동)
- **push 전 README 검증 필수** (5항목 평균 8.0+, 최대 3회 재시도, 미통과 시 push 차단)
- **CI 통과 전 머지 금지** (예외 없음)
- **feat 브랜치 직행 배포 금지**: 모든 배포는 `rp-ship` 경유 (PR → CI → main 머지 → 배포). feat/통합 브랜치 상태로 프로덕션 프로세스 기동·노출 금지. 단, 로컬 개발 서버(`uvicorn --reload`) 는 예외.
- **프런트엔드 변경 시 Playwright E2E + axe(접근성) 검사 필수**: `rp-qa` 단계에서 둘 다 실행, 실패 시 진행 차단. E2E 테스트가 없는 UI 태스크는 완료 불가.
- **백엔드 변경 시 4-게이트 의무**: [`harness-backend-test-policy.md`](docs/harness-backend-test-policy.md) — (1) 단위 항상 (2) 읽기 endpoint API 응답 테스트 (3) SQL/JPA/마이그레이션 변경 시 `@SpringBootTest+@Transactional` ROLLBACK 통합 테스트 (4) 컨트롤러·DI·Flyway 변경 시 로컬 `bootRun` + 헬스 + Flyway 로그 + OAuth 인증 endpoint 응답 캡처. 미준수 머지 차단.
- "급해서", "간단해서", "나중에" 등 어떤 이유로도 단계 스킵 불가
- **회고(`/rp-retro`)는 사용자 명시 명령 시에만 실행** — 자동 진입 없음. 필요 시 사용자가 직접 `/rp-retro` 호출
- **`rp-ship` 자동 머지 가드 4종 AND**: (a) CI 모든 체크 SUCCESS (b) 리뷰 증거 게이트 통과 (c) PR base 정상 감지 (d) `gh pr view --json mergeable` = `MERGEABLE`. 모두 충족 시에만 자동 머지. 하나라도 실패 → 중단 + OPEN 유지 + 사용자 보고. `--admin`·`--no-verify` 우회 금지. 비상 탈출구 `RP_SHIP_MANUAL=1` 환경변수만 자동 머지 비활성 허용
- 워크플로우 위반 발견 시 즉시 중단하고 빠진 단계부터 재진행
- **하네스 메타 변경 단축 경로**: `rp-init`·`rp-specify`·`rp-task`·`rp-dev` 스킵 + feat 브랜치 + `rp-prd` 간소(변경 이유·영향 파일·롤백·검증 4섹션) + 리뷰 + `rp-ship`. 완전 생략은 금지
- **`main` 직접 수정 금지**: `main` 브랜치에서 docs·CLAUDE.md·스킬·settings 수정 감지 시 즉시 중단 + feat 브랜치 전환 요구
- **`rp-ship` 스킬 호출 필수**: 커밋·PR·머지·배포는 수동 `git`/`gh` 우회 없이 `rp-ship` 스킬 경유. 단, `rp-ship` 스킬 내부 절차로 명시된 명령은 예외
- **`rp-ship` PR base 자동 감지 게이트**: 메타 변경 분기(선검사 — PRD 폴더에 `review-claude-meta-r*.md` 또는 `review-codex-meta.md` 존재 시 자동 `--base main`) → 프로젝트 `docs/tasks.md` → 프로젝트 `CLAUDE.md` 의 `^[\s\-\*|]*통합 브랜치:\s*`?([A-Za-z0-9/_\-]+)`?` 앵커를 순차 감지해 정확히 1건 매칭되는 값을 `--base` 로 주입. 전부 0건이면 레포 default branch. **Fail-closed**: 2건+ 매칭·공백 포함·원격 부재·detached HEAD·프로젝트 루트 미확인 시 중단. 느슨한 `feat/*` 추론 금지. 수동 오버라이드 `--base <X>`·메타 분기만 감지 우회 허용. base 리타깃 시 CI 재실행 후 자동 머지 가드 재확인

**코드리뷰 상세:** [`harness-code-review.md`](docs/harness-code-review.md)
**Codex 추가 리뷰:** [`harness-codex-review.md`](docs/harness-codex-review.md) — 플러그인 `openai/codex-plugin-cc` (루트에 1회 설치, settings.json 선언)
**디자인 원칙:** [`harness-design.md`](docs/harness-design.md)
**README 규칙:** [`harness-readme.md`](docs/harness-readme.md)
**시크릿 관리:** [`security-guide.md`](docs/security-guide.md) / [`security/secrets-management.md`](docs/security/secrets-management.md)
**DB 스타일:** [`harness-db.md`](docs/harness-db.md) — 테이블/컬럼/인덱스/ENUM COMMENT 규칙
**백엔드 테스트 정책:** [`harness-backend-test-policy.md`](docs/harness-backend-test-policy.md) — 4-게이트 (단위·GET API·DB 통합·bootRun)

## Token Efficiency

- 모든 응답에서 불필요한 텍스트 최소화
- 핵심 내용만 간결하게 전달
- 반복·장황한 표현 제거
- `.claudeignore`: 루트 공통 규칙 + 프로젝트별 추가 가능 (합산 적용)
