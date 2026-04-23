# Harness Codex Review

Claude 리뷰 이후 Codex 플러그인(`openai/codex-plugin-cc`)으로 **추가 리뷰 1회**를 포그라운드에서 순차 실행한다.

## 적용 단계

| 단계 | Claude 리뷰 | Codex 명령 | 저장 경로 |
|:---:|-------------|-----------|---------|
| 4 | 기획 리뷰 | `/codex:review --wait` | `<project-root>/docs/prd/[feature]/review-codex-plan.md` |
| 5 | 엔지니어링 리뷰 | `/codex:review --wait` | `<project-root>/docs/prd/[feature]/review-codex-eng.md` |
| 9 | 코드 리뷰 | `/codex:review --wait --base main` | `<project-root>/docs/prd/[feature]/review-codex-code.md` |
| meta | 하네스 메타 변경(간소 PRD 단일 리뷰) | `/codex:review --wait` | `claude-projects/docs/prd/[feature]/review-codex-meta.md` |

`<project-root>` 정의:
- 일반 기능 변경 → `repositories/[project]/`
- 하네스 메타 변경(본 규칙·docs/·CLAUDE.md 등) → `claude-projects/` 루트

## 실행 규칙

| 항목 | 규칙 |
|------|------|
| 실행 순서 | Claude 리뷰 **완료 후** Codex 실행 (직렬) |
| 모드 | `--wait` 포그라운드, 완료까지 동기 대기 |
| 회차 | **1회만** 실행 (재시도 없음) |
| 점수화 | **없음** — Codex는 점수 산출·통과 판정 안 함 |
| 반영 규칙 | 지적 심각도 **High / Critical**만 수동 반영. Medium 이하는 참고용 |
| 결과 저장 | Codex stdout 전체를 경로에 그대로 기록 |
| cwd | **해당 기능의 PRD가 있는 프로젝트 루트**에서 실행. 하위 feature는 `repositories/[project]/`에서, 하네스 메타 변경은 `claude-projects/` 루트에서 실행. cwd 오인 시 Codex가 상위 레포를 리뷰해 결과 무효 |
| 실행 전 체크 | `pwd` 출력이 PRD 프로젝트 루트와 일치하는지 검증. 불일치 시 `cd` 후 재확인. 체크 생략 금지 |

## 직렬 실행 패턴

```
[단계 N 진입]
  ↓
Claude 리뷰 서브에이전트 실행 (기존 점수제 판정)
  ↓
Claude 통과 확인
  ↓
Codex 포그라운드 실행 (1회)
  ↓
Codex stdout 저장 (review-codex-*.md)
  ↓
High / Critical 지적 확인
  ├─ 있음 → 반영 → 다음 단계
  └─ 없음 → 다음 단계
```

## High / Critical 반영 절차

1. Codex 결과에서 `[high]` / `[critical]` 표기 라인만 추출
2. 각 지적을 PRD(단계 4·5) 또는 코드(단계 9)에 반영
3. 반영 결과를 해당 `review-codex-*.md` 하단에 `## 반영` 섹션으로 기록
4. Claude 리뷰는 재실행하지 않음 (Codex 1회 원칙 유지, 반영만 수행)

## 플러그인 선언

`.claude/settings.json` 루트에 선언:

```json
{
  "extraKnownMarketplaces": {
    "openai-codex": {
      "source": { "source": "github", "repo": "openai/codex-plugin-cc" }
    }
  },
  "enabledPlugins": { "codex@openai-codex": true }
}
```

- 요구사항: Node.js 18.18+, ChatGPT 구독 또는 OpenAI API 키, `codex login` 완료
- clone 후 폴더 trust 시 플러그인 설치 프롬프트 자동 노출
- 최초 1회 `/codex:setup` + `!codex login` 필요

## ⛔ 절대 규칙

- 단계 4 · 5 · 9 및 **메타 변경 단일 리뷰**에서 Codex 리뷰 **생략 불가**
- Codex 결과 **저장 필수** (감사용)
- High / Critical 지적은 반영 **필수**. 미반영 시 다음 단계 진입 금지
- Codex는 점수화·재시도 **하지 않음** (1회 원칙)
- 플러그인 미설치 시 워크플로우 중단, 설치 안내

→ 워크플로우: [`harness-workflow.md`](harness-workflow.md)
→ 기획 리뷰: [`skills/rp-plan-review.md`](skills/rp-plan-review.md)
→ 엔지 리뷰: [`skills/rp-eng-review.md`](skills/rp-eng-review.md)
→ 코드 리뷰: [`harness-code-review.md`](harness-code-review.md)
