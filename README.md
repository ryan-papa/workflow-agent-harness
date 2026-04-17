# Harness Engineering Framework

> AI 코딩 에이전트의 품질을 높이기 위한 워크플로우 규칙 체계

---

## 왜 이 프로젝트인가?

> **핵심 비전: 사람의 코딩 한 줄 없이 프로젝트를 완성한다.**

AI 코딩 에이전트가 기획 → 개발 → 테스트 → 배포까지 전 과정을 자동으로 수행한다.
하지만 "그냥 만들어줘"라고 하면 결과물의 품질이 들쭉날쭉하다.

**하네스 엔지니어링**은 이 과정에서 품질을 보장하기 위한 규칙 체계다.
PRD 작성부터 코드리뷰까지 10단계 워크플로우를 규칙으로 정의해서,
에이전트가 일관된 품질의 코드를 산출하도록 한다.

### 핵심 특징

- **12단계 전체 플로우** — 프로젝트 초기화부터 배포·회고까지 단계별 가이드
- **2단계 리뷰** — 기획 리뷰 + 엔지니어링 리뷰로 PRD 품질 확보
- **7항목 코드리뷰** — 구조적 코드리뷰 체크리스트로 일관성 유지

---

## 프로젝트 구조

```
claude-projects/
├── docs/                          # 공통 규칙 문서
│   ├── harness-workflow.md        # 12단계 전체 플로우
│   ├── harness-prd.md             # PRD 작성 + 2단계 리뷰
│   ├── harness-dev.md             # 개발 + QA + 코드리뷰
│   ├── harness-code-review.md     # 7항목 코드리뷰
│   ├── harness-design.md          # UI 디자인 원칙
│   ├── harness-readme.md          # README 작성 규칙
│   ├── security-guide.md          # 시크릿 관리 원칙 (sops+age)
│   ├── security/                  # 시크릿 상세 절차
│   │   └── secrets-management.md
│   └── templates/                 # PRD, README, CI, 시크릿 템플릿
│       ├── readme-opensource.md
│       ├── readme-service.md
│       ├── ci-pr.yml
│       ├── sops.yaml.template
│       └── env.example.template
├── .claudeignore                  # 토큰 절약용 공통 ignore
├── CLAUDE.md
└── README.md
```

---

## 워크플로우 개요

```
[1] 프로젝트 초기화
 ↓
[2] 구체화 (도메인 → 기술, 질문·리서치)
 ↓
[3] PRD 작성
 ↓
[4] 기획 리뷰 ← 최대 3회
 ↓
[5] 엔지니어링 리뷰 ← 최대 3회
 ↓
[6] 태스크 분해
 ↓
[7] 개발 (통합 브랜치 → 태스크별 반복)
 ↓
[8] QA (사전 검증 → 시나리오 테스트)
 ↓
[9] 코드 리뷰 (7항목) → 개선 ← 최대 3회
 ↓
[10] 산출물 보고
 ↓
[11] 커밋 → PR → CI → 머지 → 배포
 ↓
[12] 회고
```

전체 흐름은 [`docs/harness-workflow.md`](docs/harness-workflow.md) 참고.

---

## 규칙 문서

| 문서 | 역할 |
|------|------|
| [`harness-workflow.md`](docs/harness-workflow.md) | 12단계 전체 플로우 정의 |
| [`harness-prd.md`](docs/harness-prd.md) | PRD 작성 가이드 + 기획/엔지니어링 리뷰 |
| [`harness-dev.md`](docs/harness-dev.md) | 개발 절차 + QA + 코드리뷰 통합 |
| [`harness-code-review.md`](docs/harness-code-review.md) | 7항목 코드리뷰 체크리스트 |
| [`harness-design.md`](docs/harness-design.md) | UI 디자인 원칙 |
| [`harness-readme.md`](docs/harness-readme.md) | README 작성 규칙 + 체크리스트 |
| [`security-guide.md`](docs/security-guide.md) | 시크릿·자격증명 관리 원칙 (sops+age) |

---

## 빠른 시작

### 전제조건

| 도구 | 용도 | 확인 명령어 |
|------|------|-----------|
| Claude Code | AI 코딩 에이전트 | `claude --version` |
| Node.js | 일부 프로젝트 런타임 | `node --version` |
| Git | 버전 관리 | `git --version` |

### 사용법

1. 이 레포를 클론한다.
2. Claude Code에서 `claude-projects/` 디렉토리를 워킹 디렉토리로 설정한다.
3. `CLAUDE.md`가 자동 로드되어 하네스 규칙이 에이전트에 적용된다.
4. 하위 프로젝트 작업 시 `repositories/{프로젝트명}/`으로 이동한다.

```bash
git clone <repo-url> claude-projects
cd claude-projects
claude  # Claude Code 실행 — CLAUDE.md 자동 적용
```

---

## 기여 가이드

1. Fork
2. `git checkout -b feat/{기능명}`
3. 커밋 (Conventional Commits)
4. Push -> PR 생성

---

## 라이선스

MIT License
