# PRD: Antigravity 런타임 지원 (`Antigravity-Lead`)

**상태:** Approved ([4] 1회차 8.0 → 재검증 8.7 · [5] 2회차 8.8 · [9-코드] 2회차 8.57 → 재검증 8.86)
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

| # | 문제 | 근거 |
|:-:|------|------|
| 1 | 현재 하네스는 `Claude-Lead`(Claude Code)와 `Codex-Lead`(Codex CLI) 2개 런타임만 정의·지원 | 사용자 요청 — Antigravity(CLI·2.0·IDE) 진입 시에도 동일 12단계 워크플로우·4축 리뷰·자동 머지 가드를 수행해야 함 |
| 2 | Antigravity는 워크스페이스에서 `.agents/skills/*/SKILL.md`·`GEMINI.md`·`.agents/hooks.json`을 탐색하나 레포에 해당 산출물·동기화 파이프라인이 없음 | Antigravity 진입 시 `AGENTS.md`(Codex 전용)만 로드되어 `spawn_agent` 등 타 런타임 지시가 혼재되고 `rp-*` 스킬 자동 발견 불가 |
| 3 | `scripts/token-usage.py`가 Claude·Codex transcript만 파싱하여 Antigravity 단계 토큰 출력 불가 | Antigravity는 `ANTIGRAVITY_CONVERSATION_ID`·`ANTIGRAVITY_APP_DATA_DIR` 환경변수와 `transcript.jsonl`(`PLANNER_RESPONSE` 토큰 필드)을 제공함 |

## 결정 사항

| # | 항목 | 결정 | 기각 대안 (A/B/C/D) | 근거 유형 |
|:-:|------|------|----------------------|-----------|
| 1 | 루트 어댑터 파일 구조 | **사용자 결정:** `GEMINI.md` 경량 어댑터 신설(`≤200줄` AND `≤8,000 bytes`) + `AGENTS.md` 상단에 런타임 분기 1줄 추가 (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md` 3자 대칭, 동시 로드 시 Antigravity는 `GEMINI.md` 우선, `AGENTS.md + GEMINI.md` 합산 `≤22,000 bytes`) | (B) `AGENTS.md` 통합 확장·`GEMINI.md` 미생성 / (C) `GEMINI.md` 완전 독립본(~24KB 중복 점유) / (D) `.agents/rules/harness.md` 전용 분리 | 사용자 결정 (Q1 1번) |
| 2 | 작성 모드·서브에이전트·회신 계약 | **가정:** 신규 모드명 `Antigravity-Lead`. 리뷰 서브에이전트는 `invoke_subagent`(`TypeName: "self"`, 별도 컨텍스트, 읽기·분석 전용 프롬프트, `[4]∥[5]`·`[9-코드]∥[9-인프라]` 동시 발사 후 두 서브에이전트 완료 알림을 모두 수신해 판정하는 비동기 fan-in). **비대칭 `send_message` 계약:** 서브에이전트 → 부모 결과 회신용 `send_message`는 필수 허용(별도 파일·artifact 생성 금지, 텍스트 전달만), 부모 → 이전 리뷰어 재호출용 `send_message`는 전면 금지(재리뷰·조건부 재검증은 반드시 새 `invoke_subagent`). 한 축 기술 실패 시 실패 축만 새 서브에이전트 재발사(정상 축 보존), 동시 발사 불가 환경이면 순차 fallback 허용. 교차 런타임(Claude·Codex) 호출 금지, 리뷰에 `swarm` 금지 | `research`·`define_subagent(EnableWriteTools=False)`(`run_command` 불가로 `git diff`·`gh pr view` 미지원) · 약어 `AGY-Lead` · `swarm` | 엔지니어 선호 |
| 3 | 스킬 동기화 엔진 | **가정:** 공통 엔진 `scripts/sync-skills.py`(`--target all\|codex\|antigravity`, `--check`, `--install-user`, `--self-test`) 신설. 타겟별 선언적 설정(`TARGETS`: 출력 디렉터리·어댑터 노트·본문 치환표·상대 링크 재작성 `../../../docs/`·사용자 설치 경로)으로 `docs/skills/rp-*.md` → `.codex/skills/rp-*/SKILL.md` + `.agents/skills/rp-*/SKILL.md` 생성. 기존 `scripts/sync-codex-skills.py`는 `--check`·`--install-user`·exit code(0/1)·출력을 `sync-skills.py --target codex`로 100% 위임하는 하위 호환 래퍼로 유지 | 별도 `sync-agy-skills.py` 복제(중복 로직) · `sync-codex-skills.py` 삭제(기존 훅·문서 파손) | 엔지니어 선호 |
| 4 | 글로벌 스킬 설치 경로 | **가정:** Antigravity `--install-user` 대상은 `$ANTIGRAVITY_CONFIG_DIR/skills`(하네스 스크립트 오버라이드 변수, 미설정 시 Antigravity 공식 글로벌 경로 `~/.gemini/config/skills/`)에 `.agents/skills/rp-*` 디렉터리 심링크 설치. `--target all --install-user`는 Codex+Antigravity 양쪽 설치. 기존 `sync-codex-skills.py` 정책과 동일하게 현행 `rp-*`만 갱신(비심링크 기존 디렉터리 충돌 시 stderr 경고 후 스킵) | 워크스페이스 `.agents/skills/`만 제공(서브레포 `.git` 경계 밖 미탐색) | 제품 가설 |
| 5 | 라이프사이클 훅 (`PostToolUse` 전용) | **가정:** `.agents/hooks.json`은 **`PostToolUse`(스킬 자동 동기화)만 등록**하고 **`PreToolUse`(`run_command`)는 등록하지 않음**(push 전 README 검증은 `rp-ship` 절차 2번 + `GEMINI.md` 규칙으로 유지 — Antigravity `PreToolUse` `allow`의 권한 정책 우회 및 모든 `run_command` 동기 지연 방지). `hooks.json`은 `.agents/` 기준 상대 경로 `python3 ./hooks/sync-rp-skills.py`(timeout `10`초)로 CLI·IDE/2.0 수정 도구(`write_file\|edit_file\|write_to_file\|replace_file_content\|multi_replace_file_content`)를 매칭. `.claude/hooks/sync-rp-commands.sh`도 `sync-skills.py --target all` 호출로 갱신 | `PreToolUse`(`run_command` allow → Tool Execution Policy 우회 결함 및 전 명령 지연) · 훅 전면 미제공(수동 동기화 누락) | 엔지니어 선호 (보안 리뷰 반영) |
| 6 | 단계 토큰 집계 | **가정:** `scripts/token-usage.py`에 `--runtime antigravity` 및 `auto` 감지(`CLAUDE_CODE_SESSION_ID` → `ANTIGRAVITY_CONVERSATION_ID` → Codex 순) 추가. 경계 = 마지막 `--start N`이 발견된 `PLANNER_RESPONSE` 행의 `step_index` 이상(`>=`, Claude와 대칭) 합산. 경계 이후 구간의 `invoke_subagent` 결과에서 유효 자식 `conversationId`를 수집해 `visited` 집합(중복·순환 차단)으로 1회씩 합산. `format_line`에서 `cache_w_na`와 `main_only`를 분리: Antigravity는 항상 `cache_w n/a`, 자식 호출이 없거나 전건 합산 시 접미사 없음, 자식 transcript 누락·파싱 실패 시에만 `(메인만)` 표기. `ANTIGRAVITY_APP_DATA_DIR` 미설정 시 `~/.gemini/antigravity-cli` → `~/.gemini/antigravity` → `~/.gemini/antigravity-ide` 순으로 `brain/<cid>` 존재 경로 탐색 | 메인만 고정(서브에이전트 비용 누락) · `codex: bool` 단일 플래그 재사용(표기 부정확) | 엔지니어 선호 |

## 스코프 · 경계 · 예외 분기

- **In-Scope:** `Antigravity-Lead` 모드 규칙 정의, `GEMINI.md` 경량 어댑터, `AGENTS.md` 분기 안내, `scripts/sync-skills.py` + `sync-codex-skills.py` 호환 래퍼, `.agents/skills/rp-*/SKILL.md`(15종), `.agents/hooks.json` + `.agents/hooks/sync-rp-skills.py`, `.claude/hooks/sync-rp-commands.sh` 갱신, `scripts/token-usage.py` Antigravity 지원, 관련 하네스 문서·스킬(`rp-init.md` 포함)·README·CI(`.github/workflows/ci.yml`) 동기화.
- **Out-of-Scope:** 서브레포(`repositories/[project]/`) 개별 설정 수정, 기존 미커밋 파일(`.claude/settings.json`) 변경, Antigravity IDE/2.0 전용 GUI 설정, 신규 `rp-*` 단계 추가, 교차 런타임 리뷰 허용, `PreToolUse` 훅 등록.
- **런타임 경계:**
  - **서브레포 단독 오픈:** Antigravity는 `.git` 경계까지만 상위 규칙·훅·스킬을 탐색하므로 하네스 루트(`workflow-agent-harness/`)를 워크스페이스로 여는 것을 권장. 서브레포를 단독 오픈할 경우 `--install-user`로 `rp-*` 스킬을 전역 노출하고 루트 `GEMINI.md`·`CLAUDE.md`는 수동 Read함을 `GEMINI.md`·`README.md`에 명시.
  - **Antigravity 고유 기능 경계:** `GEMINI.md`에 (a) 리뷰 결과·점수표의 artifact 파일 생성 금지(텍스트/메시지 반환만) (b) 리뷰 서브에이전트는 `swarm` 금지·`invoke_subagent`(`TypeName: "self"`)만 사용 명시.
- **예외·보안·성능 분기:**
  - `AGENTS.md` + `GEMINI.md` 동시 로드: Antigravity는 `GEMINI.md` 매핑 우선 적용, Codex CLI는 `GEMINI.md` 미로드로 기존 동작 100% 보존. `GEMINI.md ≤8,000B`, `AGENTS.md ≤24,000B`, 합산 `≤22,000B` 유지.
  - `.agents/hooks/sync-rp-skills.py`: 표준 라이브러리(`json`, `sys`, `pathlib`)만 로드하는 경량 fast-path. stdin camelCase `toolCall.args`에서 `Path` → `TargetFile` → `file_path` 순 추출. `Path(file_path).resolve()`가 하네스 루트(`Path(__file__).resolve().parents[2]`)의 직계 `docs/skills/` 하위(`parent == (root / "docs" / "skills").resolve()`)이고 파일명이 `^rp-[a-z0-9-]+\.md$`일 때만 동기화 실행(서브레포·`..` 경로 차단). 실행 시 `subprocess.run([sys.executable, str(sync_script), "--target", "all"], shell=False, timeout=10)` + `.claude/commands/` 심링크 갱신. 모든 오류 경로에서도 항상 `{}` 출력 + exit 0(fail-open).
  - `sync-skills.py`: frontmatter 누락·손상 시 fail-fast, `--check` 시 누락/변경/잔여(extra) 전부 검출 후 exit 1.
  - `token-usage.py` Antigravity 경로: `cid`·`child_cid`는 `^[A-Za-z0-9-]+$` 검증 + 최종 경로 `.resolve().is_relative_to(brain_dir.resolve())` 경계 검증(경로 순회 차단). `ANTIGRAVITY_CONVERSATION_ID` 부재 또는 transcript 미발견 시 `세션 식별 불가`, 경계 미존재 시 `경계 없음`, `args.CommandLine` 이중 인코딩·비문자열·손상 JSON 행 안전 무시, 출력에 transcript 본문·경로 노출 금지.
  - 메타 단축 경로 예외(`docs/skills/` 전용): 동기화 산출물 범위에 `.agents/skills/` 포함해 기존 예외 규칙 정합 유지.

## 우선순위 · 구현 순서

1. **P0 (코어 규약):** `docs/harness-absolute-rules.md` + `GEMINI.md` + `AGENTS.md` + `CLAUDE.md`
2. **P0 (스킬 동기화·훅):** `scripts/sync-skills.py` + `scripts/sync-codex-skills.py` 래퍼 + `.agents/hooks.json`·`.agents/hooks/sync-rp-skills.py` + `.claude/hooks/sync-rp-commands.sh`
3. **P1 (토큰 집계):** `scripts/token-usage.py` Antigravity 파서 + `--self-test` 픽스처
4. **P1 (문서·스킬·CI 동기화):** `docs/harness-{workflow,prd,qa,code-review,infra-review}.md`, `docs/skills/rp-{init,plan-review,eng-review,code-review,infra-review,pr-review,prd,workflow}.md`, `README.md`, `.github/workflows/ci.yml`
5. **P1 (최종 스킬 동기화):** `docs/skills/` 수정 완료 후 `python3 scripts/sync-skills.py --target all` 실행 → `.agents/skills/rp-*/SKILL.md`·`.codex/skills/rp-*/SKILL.md` 최신화 + `--check` 통과 확인

부분 실패 시 해당 단위를 수정·재검증하고, 전체 PR 단위로 일괄 ship한다(부분 ship 없음).

## 영향 파일

| 파일 | 역할·변경 내용 |
|------|---------------|
| `GEMINI.md` (신규) | Antigravity-Lead 경량 어댑터(모드·도구 매핑·`send_message` 비대칭 계약·artifact/`swarm` 금지·서브레포 경계·규칙 우선순위, ≤200줄·≤8,000B) |
| `AGENTS.md` | 상단에 Codex CLI 전용 / Antigravity는 `GEMINI.md` 우선 안내 + 3모드 매트릭스 반영 |
| `CLAUDE.md` | 프로젝트 트리(`GEMINI.md`·`.agents/`·`sync-skills.py`), 3모드 표·셀프리뷰·병렬·교차런타임·스킬 동기화 갱신 |
| `README.md` | 프로젝트 구조, Antigravity 빠른 시작(루트 워크스페이스 권장·서브레포 안내), 3모드 표(`Claude-Lead` / `Codex-Lead` / `Antigravity-Lead`) |
| `scripts/sync-skills.py` (신규) | 선언적 `TARGETS` 기반 `docs/skills/rp-*.md` → `.codex/skills/` + `.agents/skills/` 변환(`../../../docs/` 링크 재작성·어댑터 노트·치환표)·`--check`·`--install-user`·`--self-test` |
| `scripts/sync-codex-skills.py` | 기존 CLI(`--check`·`--install-user`·exit code) 호환 래퍼(`sync-skills.py --target codex` 위임) |
| `.agents/skills/rp-*/SKILL.md` (신규 15종) | Antigravity 워크스페이스용 `rp-*` 스킬 변환본 |
| `.codex/skills/rp-*/SKILL.md` (동기화) | `docs/skills/` 변경분 반영 재동기화 |
| `.agents/hooks.json` · `.agents/hooks/sync-rp-skills.py` (신규) | Antigravity `PostToolUse` 전용 스킬 자동 동기화 훅(상대 경로 `./hooks/sync-rp-skills.py`, `timeout: 10`, 경로 격리, fail-open `{}`) |
| `.claude/hooks/sync-rp-commands.sh` | `sync-skills.py --target all` 호출로 Claude 수정 시 Codex·Antigravity 동시 갱신 |
| `scripts/token-usage.py` | Antigravity transcript 집계(`--runtime antigravity`, `auto` 감지, `step_index >=` 경계, 자식 `visited` 합산 + 경로 순회 차단, `cache_w_na`/`main_only` 분리, `APP_DATA_DIR` fallback, `--self-test`) |
| `docs/harness-absolute-rules.md` | 3모드 매트릭스 SSOT, `invoke_subagent`·`send_message` 비대칭 계약, 메타 단축·서브레포 grep 대상에 `GEMINI.md`·`.agents/` 추가 |
| `docs/harness-{workflow,prd,qa,code-review,infra-review}.md` | 3모드 실행 주체, 단계 토큰 Antigravity 명세, 간소 PRD·메타 QA 대상(`GEMINI.md`·`.agents/`, `sync-skills.py --check`) 동기화 |
| `docs/skills/rp-{init,plan-review,eng-review,code-review,infra-review,pr-review,prd,workflow}.md` | 3모드 표·`invoke_subagent` 호출·완료 출력·메타 대상(`GEMINI.md`·`.agents/`)·신규 스킬 체크리스트 동기화 |
| `.github/workflows/ci.yml` | `GEMINI.md` 필수 파일·500줄·바이트 상한(`GEMINI.md ≤8000`, `AGENTS.md ≤24000`)·내부 링크 + `sync-skills.py --check`/`--self-test` + `token-usage.py --self-test` |

## 검증

- **자동화·로컬 CI (머지 전):**
  - 필수 파일 존재 확인(`GEMINI.md` 포함), 전 `.md` 파일 ≤500줄, `wc -c GEMINI.md` ≤8,000B · `wc -c AGENTS.md` ≤24,000B · 합산 ≤22,000B, 내부 링크 깨짐 0건
  - `python3 scripts/sync-skills.py --check`, `python3 scripts/sync-codex-skills.py --check`, `python3 scripts/sync-skills.py --self-test`, `python3 scripts/token-usage.py --self-test`(경계 전/후·이중 인코딩·자식 합산/누락 `(메인만)`·`../../` 경로 순회 무시·실패 케이스 포함) 모두 exit 0
  - `cwd=.agents/`에서 `python3 ./hooks/sync-rp-skills.py` 단위 실행: `write_file`(`Path`)·`edit_file`(`Path`)·`write_to_file`(`TargetFile`)·서브레포 경로(`repositories/demo/docs/skills/rp-x.md`)·`../../etc/passwd`·손상 JSON 모두 유효 JSON `{}` + exit 0 및 비대상 시 동기화 미실행 검증
  - `.claude/hooks/sync-rp-commands.sh` stdin 파이프 회귀 테스트 exit 0 확인
  - 하네스 문서 전수 `grep`으로 `Codex-Lead`/`sync-codex-skills`/`.codex/`/`AGENTS.md` 누락 0건, 서브레포 마크다운 링크 0건, 민감 정보 스캔 0건
- **독립 리뷰 (머지 전):**
  - Antigravity `invoke_subagent`(`TypeName: "self"`) 기반 `[4]` 기획 리뷰 ∥ `[5]` 엔지니어링 리뷰 병렬 통과(각 평균 ≥8.0, 최저 ≥7)
  - `[9-코드]` 코드 리뷰 통과(평균 ≥8.0, 최저 ≥7; 메타 변경이므로 인프라 축 skip)
- **사용자 검증 게이트 (시범 확인 — 본 세션·머지 후 첫 실행):**
  - **게이트 1 (본 세션 실측):** 구현 직후 본 Antigravity 세션에서 `token-usage.py --start 8` → `token-usage.py` 실행해 실제 단계 토큰 1줄 출력 확인(합격선: `집계 실패` 없이 `in/out/cache_r` > 0 출력 및 `cache_w n/a` 표기; 실패 시 파서 즉시 수정).
  - **게이트 2 (머지 후 첫 Antigravity 세션):** 새 Antigravity 세션에서 (a) 루트 `GEMINI.md`+`AGENTS.md` 동시 로드 시 `GEMINI.md` 우선 적용, (b) `.agents/skills/rp-*` 자동 탐색, (c) `docs/skills/` 편집 시 `PostToolUse` 훅 자동 동기화 확인(합격선: 3건 모두 오류 0건; 실패 시 후속 메타 PR로 보정).

## 롤백 전략

- **코드·문서 원복:** 단일 PR(`feat/antigravity-support`) `git revert`로 전체 원복 가능. 기존 Claude(`.claude/commands/`, `CLAUDE.md`) 및 Codex(`.codex/skills/`, `AGENTS.md`, `sync-codex-skills.py`) 인터페이스는 하위 호환 유지이므로 revert 시 기존 런타임 기능 손실 0건.
- **로컬 심링크 정리 (해당 시):** `--install-user`를 실행한 로컬 머신은 `~/.gemini/config/skills/rp-*` 심링크만 제거하면 완전 원복.
- **비활성화(부분 끄기):** Antigravity 훅만 즉시 끄려면 `.agents/hooks.json` 해당 훅에 `"enabled": false` 설정(재배포·코드 변경 불요).
