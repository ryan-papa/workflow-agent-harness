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
│       ├── rp-workflow.md      # 오케스트레이터
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

| 단계 | 스킬 | 내용 |
|:----:|------|------|
| 1~5 | `rp-init` ~ `rp-eng-review` | 초기화 → 구체화 → PRD → 기획리뷰 → 엔지니어링리뷰 | [`harness-prd.md`](docs/harness-prd.md) |
| 6~7 | `rp-task`, `rp-dev` | 태스크 분해 → 개발 | [`harness-dev.md`](docs/harness-dev.md) |
| 8 | `rp-qa` | QA / 콘텐츠 검수 | [`harness-qa.md`](docs/harness-qa.md) |
| 9 | `rp-code-review` | 코드 리뷰 (7항목, 최저 점수제) | [`harness-code-review.md`](docs/harness-code-review.md) |
| 10 | — | 산출물 보고 → 커밋·PR 자동 진행 | [`harness-ship.md`](docs/harness-ship.md) |
| 11 | `rp-ship` | 커밋 → PR → CI → 머지 → 배포 | [`harness-ship.md`](docs/harness-ship.md) |
| 12 | `rp-retro` | 회고 (절차 준수 + 효율성 + 규칙 개선) | [`skills/rp-retro.md`](docs/skills/rp-retro.md) |

**오케스트레이터:** `rp-workflow`가 전체 플로우 관리, 각 스킬을 순서대로 호출
**자동 전환:** 모든 단계 완료 시 다음 단계 자동 진입. 사용자 확인 없이 즉시 진행. 커밋·PR까지 자동. **배포[11]만 사용자 승인 대기.**
- 구체화 완료 → PRD 작성 자동 진입 (확인 질문 금지)
- PRD 완료 → 기획 리뷰 자동 진입
- 각 단계 완료 시 "다음 단계로 갈까요?" 질문 금지 — 바로 진행
**스킬 위치:** [`docs/skills/`](docs/skills/)

**⛔ 하네스 절대 규칙 (예외 없음):**
- 기능 변경 시 코드 전에 PRD 문서 먼저 업데이트 + 리뷰
- 테스트 코드 없이 커밋/머지 절대 금지
- 테스트·빌드 미통과 시 다음 단계 진행 금지
- QA·코드 리뷰 단계 생략 금지
- 산출물 보고 없이 배포 진행 금지 (커밋·PR은 산출물 보고 후 자동)
- **push 전 README 검증 필수** (5항목 평균 8.0+, 최대 3회 재시도, 미통과 시 push 차단)
- **CI 통과 전 머지 금지** (예외 없음)
- "급해서", "간단해서", "나중에" 등 어떤 이유로도 단계 스킵 불가
- **배포 완료 직후 회고(`/rp-retro`) 자동 시작** — 생략 불가
- 워크플로우 위반 발견 시 즉시 중단하고 빠진 단계부터 재진행


**코드리뷰 상세:** [`harness-code-review.md`](docs/harness-code-review.md)
**디자인 원칙:** [`harness-design.md`](docs/harness-design.md)
**README 규칙:** [`harness-readme.md`](docs/harness-readme.md)
**시크릿 관리:** [`security-guide.md`](docs/security-guide.md) / [`security/secrets-management.md`](docs/security/secrets-management.md)

## Token Efficiency

- 모든 응답에서 불필요한 텍스트 최소화
- 핵심 내용만 간결하게 전달
- 반복·장황한 표현 제거
- `.claudeignore`: 루트 공통 규칙 + 프로젝트별 추가 가능 (합산 적용)
