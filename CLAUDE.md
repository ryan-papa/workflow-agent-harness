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

## Post-Task Suggestions

작업 완료 또는 플랜 제공 후, 추가 개선 제안이 있을 경우:
- 질문 형식과 동일하게 번호형 보기 제공
- 선택지: 2~5개 (추천 점수 포함)
- 사용자가 선택 시 해당 항목 진행

## Document Style

| 규칙 | 내용 |
|------|------|
| 문체 | 구어체 금지, 간결·명료 |
| 구조 | 테이블/리스트 우선, 산문 지양 |
| 분량 | 파일당 200줄 이하 |
| 초과 시 | 파일 분리 또는 내용 압축 |
| 코드 | 코드 직접 작성 금지, 파일 링크 참조로 대체 |
| **자동 정합성** | docs/ 변경 시 서브에이전트가 CLAUDE.md 트리+링크 자동 동기화 (사용자에게 변경 요약만 출력) |

## Project Structure

```
claude-projects/
├── docs/                       # 공통 문서·규칙
│   ├── harness-workflow.md     # 전체 플로우 (9단계)
│   ├── harness-prd.md          # PRD 작성 + 2단계 리뷰
│   ├── harness-dev.md          # 개발 + QA + 코드리뷰
│   ├── harness-code-review.md  # 코드리뷰 상세 기준 (8항목)
│   ├── harness-design.md       # UI 디자인 원칙
│   ├── harness-readme.md       # README 작성 규칙
│   └── prd-template.md         # PRD 템플릿
├── templates/                    # 문서 템플릿
│   ├── readme-opensource.md      # 오픈소스 README 템플릿
│   └── readme-service.md        # 서비스 README 템플릿
├── repositories/               # 프로젝트별 레포 (git 제외)
│   └── [project]/
│       ├── CLAUDE.md
│       ├── README.md
│       └── docs/prd/
├── .gitignore
└── CLAUDE.md
```

**설정 우선순위:** 프로젝트(`repositories/[project]/CLAUDE.md`) > 공통(`docs/`)

## Harness Engineering

→ [`docs/harness-workflow.md`](docs/harness-workflow.md)

| 단계 | 내용 | 상세 |
|------|------|------|
| 1~5 | 초기화 → 구체화(도메인→기술→**외부API인증점검**) → PRD → 기획리뷰 → 엔지니어링리뷰 | [`harness-prd.md`](docs/harness-prd.md) |
| 6~10 | 태스크 분해 → 개발 → QA → 코드리뷰(8항목) → 산출물 | [`harness-dev.md`](docs/harness-dev.md) |

**리뷰 통과 시 사용자 승인 없이 바로 개발 진입**

**⛔ 하네스 절대 규칙 (예외 없음):**
- 기능 변경 시 코드 전에 PRD 문서 먼저 업데이트 + 리뷰
- 테스트 코드 없이 커밋/머지 절대 금지
- 테스트·빌드 미통과 시 다음 단계 진행 금지
- QA·코드 리뷰 단계 생략 금지
- "급해서", "간단해서", "나중에" 등 어떤 이유로도 단계 스킵 불가
- 워크플로우 위반 발견 시 즉시 중단하고 빠진 단계부터 재진행

**코드리뷰 상세:** [`harness-code-review.md`](docs/harness-code-review.md)
**디자인 원칙:** [`harness-design.md`](docs/harness-design.md)
**README 규칙:** [`harness-readme.md`](docs/harness-readme.md)

## Token Efficiency

- 모든 응답에서 불필요한 텍스트 최소화
- 핵심 내용만 간결하게 전달
- 반복·장황한 표현 제거
- `.claudeignore`: 루트 공통 규칙 + 프로젝트별 추가 가능 (합산 적용)
