# PRD: Codex Skill Sync

## 변경 이유

현재 하네스 스킬은 `docs/skills/rp-*.md`와 `.claude/commands/` 기준으로 Claude에서 바로 쓰도록 구성되어 있다. Codex는 `SKILL.md` 기반 스킬 폴더를 읽으므로 같은 절차를 프로젝트 안에서 바로 쓰려면 Codex용 변환본과 동기화 규칙이 필요하다.

목표:
- Claude `rp-*` 스킬 전체를 Codex `SKILL.md` 형식으로 변환
- Claude 스킬 원본과 Codex 변환본을 한 명령으로 동기화
- Codex에서도 하네스 단계와 리뷰 게이트를 동일한 이름으로 참조
- Codex 서브에이전트 가능 범위와 Claude 전용 기능 차이를 문서화

## 영향 파일

| 파일 | 역할 |
|---|---|
| `scripts/sync-codex-skills.py` | `docs/skills/rp-*.md`를 `.codex/skills/rp-*/SKILL.md`로 변환 |
| `.codex/skills/rp-*/SKILL.md` | Codex용 프로젝트 로컬 스킬 |
| `.claude/settings.json` / `.claude/hooks/sync-rp-commands.sh` | Claude 스킬 변경 시 Claude command와 Codex skill 동시 갱신 |
| `AGENTS.md` | Codex 스킬 위치, 동기화, 서브에이전트 운용 규칙 |
| `README.md` | Codex 직접 사용과 스킬 동기화 안내 |
| `CLAUDE.md` / `docs/harness-workflow.md` | 프로젝트 구조와 스킬 동기화 규칙 반영 |
| `docs/prd/harness-codex-skill-sync/*` | PRD와 리뷰 증거 |

## 롤백 전략

문제가 있으면 아래 변경을 되돌린다.
- `.codex/skills/` 삭제
- `scripts/sync-codex-skills.py` 삭제
- `.claude/settings.json`, `.claude/hooks/sync-rp-commands.sh`의 Codex 동기화 변경 제거
- `AGENTS.md`, `README.md`, `CLAUDE.md`, `docs/harness-workflow.md`의 Codex 스킬 동기화 문구 제거
- 본 PRD 디렉터리 제거

Claude 원본 스킬(`docs/skills/rp-*.md`)은 변경하지 않으므로 기존 Claude 워크플로우는 유지된다.

## 검증

| 항목 | 기준 |
|---|---|
| 변환 완전성 | `docs/skills/rp-*.md`와 `.codex/skills/rp-*/SKILL.md` 개수가 일치 |
| Codex 형식 | 각 `SKILL.md` frontmatter에 `name`, `description`만 존재 |
| 동기화 | `scripts/sync-codex-skills.py --check` 통과 |
| 로컬 설치 | `scripts/sync-codex-skills.py --install-user`로 `$CODEX_HOME/skills` 심링크 생성 |
| 서브에이전트 | Codex `spawn_agent`가 별도 작업 결과를 반환함을 확인 |
| 문서 품질 | `git diff --check`, 민감정보 스캔 통과 |
