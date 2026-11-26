# PRD: 스킬 수동 동기화 명령(`--sync-claude-links`) 및 `--check` 범위 문서 정합화

**상태:** Approved ([4] 8.22 · [5] 8.6 · [9-코드] 9.00)
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

| # | 문제 | 근거 |
|:-:|------|------|
| 1 | `README.md:160`의 "3런타임 정합성 유지" 안내가 `python3 scripts/sync-skills.py` 실행 시 `.claude/commands/`·`.codex/skills/`·`.agents/skills/`가 동시 반영되고 `--check`로 검증된다고 서술하나 실제 구현과 불일치함 | PR #93 `rp-pr-review` Medium #1 — `scripts/sync-skills.py:472-498`은 `--sync-claude-links` 없이 `.claude/commands/` 심링크를 생성하지 않으며, `--check`(485-490행)도 `.codex/skills/`·`.agents/skills/`만 검증함. 훅 없는 환경(예: Codex CLI)에서 신규 `docs/skills/rp-*.md` 추가 시 `.claude/commands/` 누락이 무음으로 남음 |
| 2 | `CLAUDE.md:164`와 `GEMINI.md:43`도 수동 동기화 명령을 `python3 scripts/sync-skills.py`로만 기재해 `docs/skills/rp-init.md:52`·`docs/skills/rp-workflow.md:55`(`--sync-claude-links`)와 불일치함 | 3런타임 어댑터 정합성 확인 결과 — `CLAUDE.md`·`GEMINI.md`·`README.md`의 수동 명령 표기를 `scripts/sync-skills.py` 실제 CLI 계약과 통일 필요 |

## 결정 사항

| # | 항목 | 결정 | 기각 대안 (A/B/C/D) | 근거 유형 |
|:-:|------|------|----------------------|-----------|
| 1 | 수정 범위(문서 정합화 vs 스크립트 변경) | **(A) 사용자 결정:** `scripts/sync-skills.py` 구현은 변경하지 않고, `README.md`·`CLAUDE.md`·`GEMINI.md`의 수동 동기화 명령을 `python3 scripts/sync-skills.py --sync-claude-links`로, `--check` 검증 대상을 `.codex/skills/`·`.agents/skills/`로 정확히 명시 | (B) `sync-skills.py` 기본 동작을 `--sync-claude-links` 자동 포함으로 변경(기존 `--target codex`·래퍼 동작 및 `--self-test` 계약 변경) / (C) `README.md`만 수정하고 `CLAUDE.md`·`GEMINI.md` 불일치 방치 / (D) `--check`에 `.claude/commands/` 검사 추가(요청 범위 초과 기능 변경) | 사용자 결정 (PR #93 `rp-pr-review` 후속 제안 승인) |
| 2 | `AGENTS.md` 변경 여부 | **(A) 가정:** `AGENTS.md:39-41`은 훅 동작 사실과 변환본 검증(`--check`)만 기술하고 `sync-skills.py` 단독 실행의 `.claude/commands/` 갱신을 주장하지 않으며, 공통 3런타임 규칙은 `AGENTS.md:48`이 상위 우선순위 `CLAUDE.md`(164행) 선확인을 위임하므로 수정하지 않는다(Surgical 원칙) | (B) `AGENTS.md`에도 Claude 전용 플래그 추가(Codex 전용 어댑터 관심사 초과) | 엔지니어 선호 |

## 스코프 · 경계 · 예외 분기

- **In-Scope:** `README.md` 160행, `CLAUDE.md` 164행, `GEMINI.md` 43행의 스킬 수동 동기화 명령(`--sync-claude-links`) 및 `--check` 검증 범위 명시.
- **Out-of-Scope:** `scripts/sync-skills.py`·`scripts/sync-codex-skills.py` 코드 변경, `AGENTS.md` 변경, `docs/skills/rp-*.md`(이미 `--sync-claude-links` 기재됨) 변경, `.github/workflows/ci.yml` 변경, 기존 로컬 미커밋 파일(`.claude/settings.json`) 수정.
- **예외·경계 분기:**
  - `--target` 기본값은 `all`(`scripts/sync-skills.py:463`)이므로 `python3 scripts/sync-skills.py --sync-claude-links`는 `rp-init.md:52`·`rp-workflow.md:55`의 `--target all --sync-claude-links`와 기능적으로 동치다.
  - `python3 scripts/sync-skills.py --sync-claude-links`는 기존 `.claude/commands/rp-*.md` 심링크를 유지하며 누락분만 생성(idempotent)하고 `.codex/skills/`·`.agents/skills/`를 동시 재생성한다. 단, 스킬 삭제·개명 시 `.claude/commands/`의 잔여/깨진 심링크는 자동 제거하지 않으며 `--check`도 `.claude/commands/` 누락·잔여를 탐지하지 않으므로 수동 정리 대상이다.
  - `--check`는 `scripts/sync-skills.py:485-490`에서 조기 반환(`return rc`)하므로 `--sync-claude-links --check` 병행 시 `--sync-claude-links`가 무음 무시된다. 동기화와 검증은 반드시 분리 실행한다.
  - `scripts/sync-codex-skills.py`는 Codex 변환본 단독 호환 래퍼로 `--check`·`--install-user`만 허용하며 `--sync-claude-links` 전달 시 exit 2로 거부한다(`CLAUDE.md:164` 문구에서 지원 범위 오해가 없도록 구분 표기).
  - `GEMINI.md` 바이트 예산(`≤ 16,000B` 목표, `≤ 24,000B` CI 상한)과 합산 예산(`≤ 28,000B` 목표, `≤ 36,000B` CI 상한)을 유지한다.

## 우선순위 · 구현 순서

1. **P0 (핵심 교정):** `README.md:160`의 `sync-skills.py` 수동 동기화 명령(`--sync-claude-links`) 및 `--check` 범위 명시
2. **P1 (3문서 정합화):** `CLAUDE.md:164`(래퍼 지원 범위 구분 포함), `GEMINI.md:43` 동일 계약으로 통일

단일 PR 단위로 일괄 ship한다(부분 ship 없음).

## 영향 파일

| 파일 | 역할·변경 내용 |
|------|---------------|
| `README.md` | 160행: 수동 동기화 명령을 `python3 scripts/sync-skills.py --sync-claude-links`로 수정하고 `--check` 검증 범위(`.codex/skills/`·`.agents/skills/`) 및 동기화·검증 분리 실행 명시 |
| `CLAUDE.md` | 164행: 수동 동기화 명령에 `--sync-claude-links`(신규 스킬 `.claude/commands/` 심링크 생성 포함), `--check` 대상(`.codex/skills/`·`.agents/skills/`, 분리 실행), `sync-codex-skills.py` 단독 호환 범위(`--check`·`--install-user`만 지원) 명시 |
| `GEMINI.md` | 43행: 수동 동기화 명령에 `--sync-claude-links`(신규 스킬 `.claude/commands/` 심링크 생성 포함)와 변환본 검증 `--check` 대상·분리 실행 명시 |

## 검증

- **자동화·로컬 CI (머지 전):**
  - 필수 파일 존재, 전 `.md` 파일 ≤500줄, `GEMINI.md` ≤16,000B(CI 24,000B) · 합산 ≤28,000B(CI 36,000B), 내부 링크 깨짐 0건, `@` 파일 인클루드 0건, 서브레포 직접 마크다운 링크 0건, 민감 정보 스캔 0건
  - `python3 scripts/sync-skills.py --sync-claude-links` 실제 실행 exit 0 및 `git status -- .claude/commands .codex/skills .agents/skills` 변경 0건(idempotent 확인)
  - `python3 scripts/sync-skills.py --check`, `python3 scripts/sync-codex-skills.py --check`, `python3 scripts/sync-skills.py --self-test`, `python3 scripts/token-usage.py --self-test`, `python3 .agents/hooks/sync-rp-skills.py --self-test` 전부 exit 0
  - `grep -n "sync-skills.py" README.md CLAUDE.md GEMINI.md`로 3파일 모두 `--sync-claude-links`와 `--check` 범위가 일치하는지 대조 확인
  - `rp-ship` 절차 2번 푸시 전 `README.md` 검증(5항목 평균 ≥8.0) 수행
- **독립 리뷰 (머지 전):**
  - Antigravity `invoke_subagent`(`TypeName: "self"`) `[4]` 기획 리뷰 ∥ `[5]` 엔지니어링 리뷰 병렬 통과(각 평균 ≥8.0, 최저 ≥7)
  - `[9-코드]` 코드 리뷰 통과(평균 ≥8.0, 최저 ≥7; 메타 변경이므로 인프라 축 skip)
- **사용자 검증 게이트 (내부 시범 사용 — 머지 전 본 세션 실측):**
  - 본 세션에서 문서에 기재한 명령 `python3 scripts/sync-skills.py --sync-claude-links && python3 scripts/sync-skills.py --check`를 직접 실행해 문서 서술과 실제 CLI 출력·exit code가 100% 일치하는지 확인(합격선: exit 0 및 문서 서술과 모순 0건; 불일치 시 즉시 문구 보정).

## 롤백 전략

- **코드·문서 원복:** 단일 PR(`feat/harness-sync-skills-doc-fix`) `git revert`로 3개 문서(`README.md`·`CLAUDE.md`·`GEMINI.md`)의 해당 1줄씩 즉시 원복 가능. 코드·스키마 변경이 없어 양방향(롤백·롤포워드) 100% 호환.
- **부분 비활성화:** 별도 런타임 플래그 없음 — 문서 표기 교정 전용 변경이므로 `git revert`가 유일하고 충분한 되돌리기 경로.
- **이상 판정 기준:** 문서에 기재된 `--sync-claude-links` 플래그가 CLI에서 실패(비정상 종료)하거나 CI `lint-docs` 실패 시 즉시 원복·재수정.
