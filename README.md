# Harness Engineering Framework

> AI 코딩 에이전트의 품질을 일정하게 유지하는 워크플로우 규칙 체계

---

## 이 프로젝트는 무엇을 하나?

AI 코딩 도구(Claude Code, Codex CLI 등)에게 "앱 하나 만들어줘"라고 시켰을 때, 같은 요청이어도 결과 품질이 매번 들쭉날쭉합니다. 이 프로젝트는 AI가 따라야 할 **일하는 순서(workflow)**와 **단계별 검토 규칙(review gates)**을 정리해서, 사람이 코드를 한 줄도 쓰지 않아도 일정한 품질의 결과물이 나오도록 보장합니다.

> **비전: 사람의 코딩 한 줄 없이 프로젝트를 완성한다.**

### 핵심 특징

- **12단계 워크플로우 (기획 → 회고)** — 새 프로젝트·기능 하나를 만들 때 AI가 어떤 순서로 무엇을 해야 하는지 단계별 명문화. 각 단계 완료 시 다음 단계로 **자동 진입**(사용자 승인 없이 진행). 단, 마지막 회고[12]는 사용자 명시 명령(`/rp-retro`) 시에만 실행.
- **4축 리뷰 게이트** — 기획(PRD 작성 후), 엔지니어링(설계 검토), 코드(구현 검토), 인프라 접점 검토를 **메인 AI가 아닌 별도 서브에이전트**가 독립 판정. 메인이 자기 작업을 셀프 채점하면 편향이 생기므로 강제 분리.
- **런타임 = 리뷰어** — 진입한 AI 도구의 서브에이전트가 채점합니다. Claude Code로 들어오면 Claude가, Codex CLI로 들어오면 Codex가 리뷰. **교차 호출은 하지 않습니다** — 외부 도구 구독·인증이 리뷰 게이트의 전제조건이 되지 않도록.
- **자동 머지 가드 3종 AND** — PR(변경 묶음)의 자동 머지는 (a) CI(자동 검사) 통과 · (b) base 브랜치 정상 · (c) 충돌 없음(MERGEABLE) **3개 모두 충족** 시에만 진행. 하나라도 실패 시 PR을 OPEN 유지 + 사용자 즉시 보고.

---

## 프로젝트 구조

```
workflow-agent-harness/
├── docs/                              # 공통 규칙 문서
│   ├── harness-absolute-rules.md      # 절대 규칙 SSOT (예외 없음)
│   ├── harness-workflow.md            # 12단계 전체 플로우
│   ├── harness-prd.md                 # PRD 작성 + 2단계 리뷰
│   ├── harness-dev.md                 # 개발·태스크·테스트
│   ├── harness-qa.md                  # QA + 콘텐츠 검수
│   ├── harness-code-review.md         # 7항목 코드리뷰
│   ├── harness-ship.md                # 산출물 보고 + 배포
│   ├── harness-design.md              # UI 디자인 원칙
│   ├── harness-readme.md              # README 작성 규칙
│   ├── harness-writing.md             # 글쓰기 원칙 (원칙 10 + 기술 용어 보존)
│   ├── harness-db.md                  # DB 스타일 (테이블·컬럼·인덱스·ENUM)
│   ├── harness-backend-test-policy.md # 백엔드 4-게이트 테스트 정책
│   ├── security-guide.md              # 시크릿 관리 원칙 (sops+age)
│   ├── security/                      # 시크릿 운영 상세
│   ├── research/                      # 하네스 메타 변경 근거 발췌 (서비스 회고에서 추출)
│   ├── templates/                     # PRD·README·CI·시크릿 템플릿
│   └── skills/                        # 하네스 스킬 (rp-*)
├── .claude/commands/                  # Claude Code 슬래시 명령 (rp-* 심링크)
├── .codex/skills/                     # Codex CLI 로컬 스킬 변환본
├── scripts/sync-codex-skills.py       # 스킬 변환·동기화
├── scripts/token-usage.py             # 단계별 토큰 1줄 출력
├── AGENTS.md                          # Codex용 하네스 어댑터
├── CLAUDE.md                          # Claude Code 진입점
└── README.md
```

---

## 12단계 워크플로우

| # | 단계 | 핵심 |
|:-:|------|------|
| 1 | 초기화 | 새 프로젝트 골격 생성 |
| 2 | 구체화 | "무엇을 만들지" 질문·리서치로 결정 잠금 |
| 3 | PRD 작성 | 요구사항을 문서(PRD = Product Requirements Doc)로 정리 |
| 4 | 기획 리뷰 | PRD의 사용자 가치·경계 채점 (**[5]와 병렬**, 축별 최대 3회) |
| 5 | 엔지니어링 리뷰 | 기술·확장성·운영성 채점 (**[4]와 병렬**, 축별 최대 3회) |
| 6 | 태스크 분해 | 작업을 작은 단위로 쪼개기 |
| 7 | 개발 | 태스크별 코딩·테스트·커밋 |
| 8 | QA | 시나리오 테스트 + 콘텐츠 검수 |
| 9 | 코드 리뷰 ∥ 인프라 리뷰 | 코드 축 7항목 채점 + **인프라 축 병렬**(SQL·Redis·비동기·직렬화·배포, BLOCK/ASK/WARN 무점수). 공통 최대 5회 |
| 10 | 산출물 보고 | 결과 정리 + 자동 진입 |
| 11 | 배포 (`rp-ship`) | PR 생성(신규 시 `rp-pr-review` 독립 리뷰 1회, 출력만) → CI → 자동 머지 가드 3종 → 머지 → 배포 |
| 12 | 회고 | 절차 준수·효율·규칙 개선 평가 (**사용자 명령 시에만**) |

각 단계 완료 시 다음 단계 자동 진입. 기본 경로는 배포[11] 자동 머지 가드 실패 시 중단·보고하고, 회고[12]는 자동 진입하지 않는다.

**진입 스킬:**
- `/rp-workflow` — 신규 프로젝트·기능 (init부터 전 단계)
- `/rp-amend` — 기존 프로젝트 기능 수정·추가 (init 스킵, Lite 판별 후 Full amend 또는 핫픽스 경량 트랙)

---

## 규칙 문서

| 문서 | 역할 |
|------|------|
| [`harness-absolute-rules.md`](docs/harness-absolute-rules.md) | 절대 규칙 SSOT(Single Source of Truth = 유일한 정답 문서) |
| [`harness-workflow.md`](docs/harness-workflow.md) | 12단계 전체 플로우 |
| [`harness-prd.md`](docs/harness-prd.md) | PRD 작성 + 기획·엔지니어링 2단계 리뷰 |
| [`harness-dev.md`](docs/harness-dev.md) | 개발·태스크·테스트 |
| [`harness-qa.md`](docs/harness-qa.md) | QA + 콘텐츠 검수 |
| [`harness-code-review.md`](docs/harness-code-review.md) | 7항목 코드리뷰 |
| [`harness-infra-review.md`](docs/harness-infra-review.md) | 인프라 리뷰 (SQL·Redis·비동기·직렬화·배포, [9] 병렬 축) |
| [`harness-ship.md`](docs/harness-ship.md) | 산출물 보고 + 배포 |
| [`harness-writing.md`](docs/harness-writing.md) | 글쓰기 원칙 (한국어 산출물 공통, 기술 용어 보존) |
| [`security-guide.md`](docs/security-guide.md) | 시크릿·자격증명 (sops+age) |

---

## 빠른 시작

### 전제조건

| 도구 | 용도 | 확인 |
|------|------|-----|
| [Claude Code](https://claude.com/claude-code) | AI 코딩 에이전트 (메인) | `claude --version` |
| Git | 버전 관리 | `git --version` |
| Python 3 | 스킬 변환·동기화 스크립트 | `python3 --version` |

### 사용법

```bash
git clone https://github.com/ryan-papa/workflow-agent-harness.git
cd workflow-agent-harness
claude  # Claude Code 실행 — CLAUDE.md 자동 로드
```

1. Claude Code가 `CLAUDE.md`를 자동 로드해 하네스 규칙을 에이전트에 적용
2. 신규 프로젝트는 `/rp-workflow [기능 설명]`, 기존 프로젝트 수정은 `/rp-amend [변경 설명]`
3. 서비스 레포는 `repositories/{프로젝트명}/`에 위치 — **하네스 문서에서 서브레포 내부 파일을 직접 링크 참조 금지** (필요 시 발췌본을 `docs/research/`에 작성)

**Codex CLI에서 직접 진입할 경우** 루트 [`AGENTS.md`](AGENTS.md)가 Claude 중심 규칙을 Codex 실행 규칙으로 번역합니다. 로컬 Codex 스킬 설치는 `python3 scripts/sync-codex-skills.py --install-user`.

---

## 작성 모드 (Claude-Lead vs Codex-Lead)

`-Lead` = "~가 주도하는". 진입한 런타임이 메인 작성자이자 채점 주체입니다 (SSOT: [`harness-absolute-rules.md`](docs/harness-absolute-rules.md) "작성 모드 및 리뷰 매트릭스"):

| 모드 | 메인 런타임 | 서브에이전트 채점 | 외부 추가 리뷰 |
|------|-----------|---------------|-------------|
| Claude-Lead | Claude Code | Claude Agent 툴 | **없음** — Codex 호출 금지 |
| Codex-Lead | Codex CLI | Codex `spawn_agent` | **없음** — Claude 호출 금지 |

**⛔ 교차 런타임 추가 리뷰 전면 금지.** 통과 판정은 동일 런타임 서브에이전트의 판정 단일 기준(코드 축 평균 ≥8.0 + 각 항목 ≥7, 인프라 축 BLOCK 0건 + 미해결 ASK 0건)입니다. 다른 도구로 별도 검토하는 것은 자유지만, 그 결과를 단계 통과 근거로 기록하지 않습니다.

---

## 기여 가이드

1. Fork
2. `git checkout -b feat/{기능명}`
3. 커밋 (Conventional Commits)
4. Push → PR 생성

하네스 규칙·문서·스킬 변경은 **메타 변경 단축 경로** 적용: `rp-init`·`rp-specify`·`rp-task`·`rp-dev` 스킵 + `rp-prd` 간소(변경 이유·영향 파일·롤백 전략·검증 4섹션) + 리뷰[4·5·9] + `rp-ship`. 상세: [`harness-absolute-rules.md`](docs/harness-absolute-rules.md) "단축 경로·예외".

---

## 라이선스

MIT License
