# PRD: Codex AGENTS 어댑터

## 변경 이유

현재 하네스는 Claude Code 중심으로 설계되어 `/rp-*` 스킬, `.claude` hook, Claude subagent 리뷰를 전제로 한다. Codex에서 레포를 직접 열면 동일 규칙을 어떻게 해석해야 하는지 명시된 진입점이 없어, 리뷰 단계와 산출물 규칙을 혼동할 수 있다.

목표:
- Codex용 루트 지침 `AGENTS.md` 추가
- Claude-led Mode와 Codex-led Mode 구분
- Codex-led Mode에서 plan / engineering / code review를 세 단계로 분리
- README와 CLAUDE.md 구조 설명에 신규 파일 반영

## 영향 파일

| 파일 | 역할 |
|---|---|
| `AGENTS.md` | Codex용 하네스 어댑터. Claude 전용 절차를 Codex 실행 규칙으로 번역 |
| `README.md` | 프로젝트 구조와 Codex 직접 사용 안내 반영 |
| `CLAUDE.md` | 루트 구조 목록에 `AGENTS.md` 추가 |
| `docs/prd/harness-codex-agents-adapter/*` | PRD와 리뷰 증거 보존 |

## 롤백 전략

문제가 있으면 아래 변경만 되돌린다.
- `AGENTS.md` 삭제
- `README.md`의 `AGENTS.md` 안내 제거
- `CLAUDE.md`의 `AGENTS.md` 구조 항목 제거
- 본 PRD 디렉토리 제거

기존 Claude 워크플로우 파일은 수정하지 않으므로 롤백 범위가 작다.

## 검증

| 항목 | 기준 |
|---|---|
| 문서 구조 | `AGENTS.md`가 200줄 이하이고 한국어 메인 + 보조 영어 톤 유지 |
| 하네스 정합성 | Claude-led Mode와 Codex-led Mode가 기존 Codex review 규칙과 충돌하지 않음 |
| 리뷰 증거 | `review-codex-meta.md` 저장 |
| 민감 정보 | 시크릿, 개인 식별 정보, 내부 인프라 값 없음 |
