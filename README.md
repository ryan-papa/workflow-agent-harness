# Harness Engineering Framework

> AI 코딩 에이전트의 품질을 높이기 위한 워크플로우 규칙 체계

---

## 왜 이 프로젝트인가?

AI 코딩 에이전트에게 "그냥 만들어줘"라고 하면 결과물의 품질이 들쭉날쭉하다.
Harness는 PRD 작성부터 코드리뷰까지 10단계 워크플로우를 규칙으로 정의해서,
에이전트가 일관된 품질의 코드를 산출하도록 한다.

### 핵심 특징

- **10단계 전체 플로우** — 프로젝트 초기화부터 최종 산출물까지 단계별 가이드
- **2단계 리뷰** — 기획 리뷰 + 엔지니어링 리뷰로 PRD 품질 확보
- **8항목 코드리뷰** — 구조적 코드리뷰 체크리스트로 일관성 유지

---

## 프로젝트 구조

```
claude-projects/
├── docs/                          # 공통 규칙 문서
│   ├── harness-workflow.md        # 10단계 전체 플로우
│   ├── harness-prd.md             # PRD 작성 + 2단계 리뷰
│   ├── harness-dev.md             # 개발 + QA + 코드리뷰
│   ├── harness-code-review.md     # 8항목 코드리뷰
│   ├── harness-design.md          # UI 디자인 원칙
│   ├── harness-readme.md          # README 작성 규칙
│   └── templates/                 # PRD, README, CI 템플릿
│       ├── readme-opensource.md
│       ├── readme-service.md
│       └── ci-pr.yml
├── repositories/                  # 프로젝트별 레포
│   ├── naver-cafe-monitor/
│   ├── math-adventure/
│   └── ai-guide/
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
[9] 코드 리뷰 (8항목) → 개선 ← 최대 3회
 ↓
[10] 최종 산출물 전달
```

전체 흐름은 [`docs/harness-workflow.md`](docs/harness-workflow.md) 참고.

---

## 규칙 문서

| 문서 | 역할 |
|------|------|
| [`harness-workflow.md`](docs/harness-workflow.md) | 10단계 전체 플로우 정의 |
| [`harness-prd.md`](docs/harness-prd.md) | PRD 작성 가이드 + 기획/엔지니어링 리뷰 |
| [`harness-dev.md`](docs/harness-dev.md) | 개발 절차 + QA + 코드리뷰 통합 |
| [`harness-code-review.md`](docs/harness-code-review.md) | 8항목 코드리뷰 체크리스트 |
| [`harness-design.md`](docs/harness-design.md) | UI 디자인 원칙 |
| [`harness-readme.md`](docs/harness-readme.md) | README 작성 규칙 + 체크리스트 |

---

## 하위 프로젝트

| 프로젝트 | 설명 | 링크 |
|----------|------|------|
| naver-cafe-monitor | 네이버 카페 모니터링 봇 | private |
| math-adventure | 수학 문제 풀이 웹서비스 | [ryan-papa.github.io/math-adventure](https://ryan-papa.github.io/math-adventure) |
| ai-guide | AI 학습 가이드 사이트 | [ryan-papa.github.io/ai-guide](https://ryan-papa.github.io/ai-guide) |

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
