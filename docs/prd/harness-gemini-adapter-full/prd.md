# PRD: `GEMINI.md` Antigravity 어댑터 상세화 (`AGENTS.md` 동등 수준)

**상태:** Approved ([4] 8.67 · [5] 8.0 · [9-코드] 8.86)
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

| # | 문제 | 근거 |
|:-:|------|------|
| 1 | 현재 루트 `GEMINI.md`는 39줄(4,672B) 경량 요약본으로, `AGENTS.md`(202줄, 12,383B)에 포함된 기준 문서 목록·작성 모드 관점 분리·필수 워크플로우 순서·리뷰 산출물/기준·문서 스타일·기본 판단이 생략·축약돼 있음 | Antigravity 런타임은 `CLAUDE.md`를 자동 로드하지 않고 `AGENTS.md`와 `GEMINI.md`만 자동 로드함. 상세도가 3배 가까이 차이 나면 Antigravity가 `AGENTS.md`의 Codex 지시(`spawn_agent` 등)를 함께 참조하며 혼선할 여지가 있음 |
| 2 | `.github/workflows/ci.yml`의 규칙 파일 바이트 상한이 `GEMINI.md ≤ 8,000B`, 합산(`GEMINI.md + AGENTS.md`) `≤ 22,000B`로 제한돼 경량 어댑터 외 구성을 차단함 | Antigravity 공식 규칙 한도는 파일당 `24,000B`, 전체 always-on 규칙 예산 `20,000 tokens`(`defaultRulesBudget` — 글로벌 규칙·하위 디렉터리 규칙·`.agents/rules/`와 공유). `GEMINI.md`를 목표 분량(~12~16KB)으로 확장해도 합산 ~25~28KB(한국어 UTF-8 보수 환산 ~2.5~3.0 B/token 기준 ~8,500~11,200토큰)로 서브레포·글로벌 규칙 여유를 확보 가능 |
| 3 | PR #91(`docs/prd/harness-antigravity-support/prd.md` 결정 #1)에서 선택했던 경량 구조를 사용자 요청에 따라 `AGENTS.md` 동등 상세 어댑터로 전환함 | 사용자 명시 요청 — "경량 어댑터 대신 Codex(`AGENTS.md`)처럼 자세하게 구성" |

## 결정 사항

| # | 항목 | 결정 | 기각 대안 (A/B/C/D) | 근거 유형 |
|:-:|------|------|----------------------|-----------|
| 1 | `GEMINI.md` 구조·분량 | **(A) 사용자 결정(요청 번복 — PR #91 결정 #1 대체):** `GEMINI.md`를 `AGENTS.md`와 동등한 섹션 구조(역할·기본 운영·스킬/훅/워크스페이스 경계·기준 문서·도구/계약 변환 규칙·작성 모드 관점 분리·필수 워크플로우·리뷰 산출물·리뷰 기준·절대 규칙·응답 언어/질문 절차/문서 스타일·기본 판단)의 상세 어댑터(구현 목표 180~240줄, `≤ 16,000B`)로 확장. 현행 `GEMINI.md`의 모든 기존 계약·최신 절대 규칙(`send_message` 비대칭 계약, `swarm`/artifact 금지, `PreToolUse` 미등록, 서브레포 `.git` 경계, 단계 토큰 출력, `rp-pr-review` 서브에이전트 의무, 비동기 fan-in + 단일 축 기술 실패 재발사, 글로벌 스킬 설치 경로 `~/.gemini/config/skills/`·`$ANTIGRAVITY_CONFIG_DIR`, `main` 직접 수정·CI 동기 검증 전 `gh pr merge`/`--auto`/`--admin`/`--no-verify`·DB 파괴적 작업·인프라 재기동·auto-memory·민감 정보·서브레포 직접 링크 금지)을 회귀 없이 100% 승계하고, `기준 문서`에 `docs/harness-absolute-rules.md`·`docs/harness-qa.md` 포함 및 `작성 모드` 3종(`Claude-Lead`·`Codex-Lead`·`Antigravity-Lead`)을 SSOT 기준으로 최신화 | (B) 현행 39줄 경량 어댑터 유지 / (C) `CLAUDE.md` 전체를 `GEMINI.md`에 복제(SSOT 드리프트·24KB 한도 근접) / (D) `.agents/rules/*.md`로 다수 분할(서브레포 단독 오픈 시 수동 Read 대상 증가) | 사용자 결정 |
| 2 | SSOT 드리프트 방지 원칙 | **(A) 가정:** 변할 수 있는 수치·임계값·세부 채점표(질문 자동 선택 임계값, 리뷰 항목별 기준, 인프라 5영역 상세 등)는 `GEMINI.md`에 하드코딩하지 않고 `CLAUDE.md`·`docs/harness-*.md` SSOT 링크 전용으로 위임한다(PR #92 결정 #5 준수). 규칙 구조 변경 시 `CLAUDE.md`·`AGENTS.md`·`GEMINI.md` 3자 동기화 경계를 유지한다 | (B) 수치·채점표 전체 인라인 복제(향후 `CLAUDE.md` 변경 시 3중 드리프트 유발) | 엔지니어 선호 |
| 3 | CI 바이트 상한 조정 | **(A) 가정:** `.github/workflows/ci.yml`의 규칙 파일 바이트 상한을 `GEMINI.md ≤ 24,000B`(Antigravity 파일당 한도, `AGENTS.md`와 대칭), `AGENTS.md ≤ 24,000B`(유지), `Combined (GEMINI.md + AGENTS.md) ≤ 36,000B`로 상향한다. 구현 목표 합산은 `≤ 28,000B`(`GEMINI.md ≤ 16,000B`)로 관리하며, `36,000B`는 목표 합산 대비 ~8KB 성장 여유와 글로벌·서브레포 규칙 공존을 전제한 CI 하드 상한(보수 환산 ~12,000~14,400토큰 / 20,000토큰 예산)이다 | (B) 상한 검사 전면 삭제(24KB 초과 시 silent truncation 위험) / (C) `GEMINI.md ≤ 16,000B` 하드캡으로 향후 소폭 확장마다 CI 수정 강제 | 엔지니어 선호 |
| 4 | 관련 문서 표현 동기화 및 3런타임 정합성 안내 | **(A) 사용자 추가 지시 반영:** `CLAUDE.md` 트리 주석과 `README.md` 트리·빠른 시작 문구의 "경량 어댑터" 표현을 `AGENTS.md`와 대칭인 "Antigravity용 하네스 어댑터" / "`GEMINI.md` 어댑터"로 갱신하고, `README.md` 기여 가이드에 기능·규칙 수정 시 Claude·Codex·Antigravity 3런타임 정합성 체크 안내를 추가한다. 과거 완료 PRD(`docs/prd/harness-antigravity-support/prd.md`)는 이력 기록이므로 수정하지 않는다 | (B) 과거 PRD까지 소급 수정(결정 이력 훼손) / (C) `README.md`·`CLAUDE.md` 미갱신(문서 불일치) | 사용자 결정 |

## 스코프 · 경계 · 예외 분기

- **In-Scope:** `GEMINI.md` 상세화, `.github/workflows/ci.yml` 규칙 파일 바이트 예산 상향 및 주석 갱신, `CLAUDE.md`·`README.md`의 "경량 어댑터" 표현 동기화, `README.md` 3런타임(Claude·Codex·Antigravity) 정합성 유지 안내 추가.
- **Out-of-Scope:** `AGENTS.md` 구조 변경, `docs/skills/rp-*.md` 및 `.agents/skills/`·`.codex/skills/` 변경, `scripts/sync-skills.py`·`scripts/token-usage.py` 변경, `.agents/hooks.json` 변경, 과거 PRD(`docs/prd/harness-antigravity-support/prd.md` 등) 수정, 로컬 미커밋 파일(`.claude/settings.json`) 수정, 세션 한정 커밋 시각 규칙의 하네스 문서 반영.
- **런타임·예외 분기:**
  - **동시 로드 및 우선순위:** 루트에서 `AGENTS.md` + `GEMINI.md` 동시 로드 시 Antigravity는 `GEMINI.md`를 우선 적용한다(우선순위: `repositories/[project]/CLAUDE.md` > 루트 `CLAUDE.md` > 루트 `GEMINI.md` > 루트 `AGENTS.md`). Codex CLI는 `GEMINI.md`를 읽지 않으므로 기존 Codex 동작 100% 보존.
  - **서브레포 단독 오픈:** Antigravity는 `.git` 경계까지만 상위 규칙·훅·스킬을 탐색하므로 하네스 루트(`workflow-agent-harness/`) 오픈을 권장한다. `repositories/[project]/` 단독 오픈 시 `--install-user`로 스킬을 전역 노출하고 루트 `GEMINI.md`·`CLAUDE.md`를 직접 Read한다.
  - **컨텍스트 비용 트레이드오프:** Antigravity는 루트 워크스페이스에서 메인 세션뿐 아니라 `invoke_subagent`(`TypeName: "self"`)로 발사되는 리뷰 서브에이전트에도 `AGENTS.md` + `GEMINI.md`를 always-on으로 동시 주입한다. 본 변경은 사용자 명시 요청에 따른 의도된 트레이드오프이며, 구현 목표 분량(`GEMINI.md ≤ 16,000B`, 합산 `≤ 28,000B`)과 CI 하드 상한(`24,000B` / 합산 `36,000B`)으로 비대화를 통제한다.
  - **인클루드·링크·보안 가드:** `GEMINI.md` 내 Antigravity `@` 파일 인클루드 문법은 `wc -c` CI 게이트를 우회해 silent truncation을 유발할 수 있으므로 금지하고 일반 마크다운 상대 링크만 허용한다. 서브레포 내부 파일 직접 링크 및 민감 정보 기재를 전면 금지한다.

## 우선순위 · 구현 순서

1. **P0 (어댑터 본문):** `GEMINI.md`를 `AGENTS.md` 동등 구조 + 현행 `GEMINI.md` 계약·최신 절대 규칙 무손실 승계 형태로 확장
2. **P0 (CI 게이트):** `.github/workflows/ci.yml`의 `GEMINI.md` 및 합산 바이트 상한·주석 갱신
3. **P1 (문서 동기화):** `CLAUDE.md`, `README.md`의 "경량 어댑터" 표현 정리 및 `README.md` 3런타임 정합성 안내 추가

단일 PR 단위로 일괄 ship한다(부분 ship 없음).

## 영향 파일

| 파일 | 역할·변경 내용 |
|------|---------------|
| `GEMINI.md` | 경량 어댑터(39줄) → `AGENTS.md` 동등 수준 상세 Antigravity 하네스 어댑터로 확장(구현 목표 180~240줄·`≤ 16,000B`; 기존 Antigravity 계약·최신 절대 규칙 100% 무손실 승계) |
| `.github/workflows/ci.yml` | 규칙 파일 바이트 상한 조정(`GEMINI.md ≤ 24000B`, `AGENTS.md ≤ 24000B`, `Combined ≤ 36000B`) 및 근거 주석 갱신 |
| `CLAUDE.md` | 프로젝트 트리 주석 `Antigravity용 경량 하네스 어댑터` → `Antigravity용 하네스 어댑터` |
| `README.md` | 프로젝트 구조 주석 및 빠른 시작 문구의 `경량 어댑터` 표현 정리, 기여 가이드에 기능·규칙 수정 시 Claude·Codex·Antigravity 3런타임 정합성 체크 안내 추가 |

## 검증

- **자동화·로컬 CI (머지 전):**
  - 필수 파일 존재 확인, 전 `.md` 파일 ≤500줄
  - `wc -c GEMINI.md` ≤16,000B(구현 목표) AND ≤24,000B(CI 상한) · `wc -c AGENTS.md` ≤24,000B · 합산 ≤28,000B(구현 목표) AND ≤36,000B(CI 상한) 확인
  - 전 문서 내부 링크 깨짐 0건
  - Antigravity `@` 파일 인클루드 문법 0건 (`grep -nE '@\[[^]]+\]\(' GEMINI.md`)
  - 서브레포 직접 마크다운 링크 0건 (`grep -rnE '\]\(.*repositories/[a-z-]+/[^)]+\)' docs/ CLAUDE.md AGENTS.md GEMINI.md README.md`)
  - 민감 정보 스캔 0건 (`git diff` 대상 `grep -iE 'password[[:space:]]*=|api[_-]?key[[:space:]]*=|secret[[:space:]]*=|token[[:space:]]*=|@[a-z0-9]+\.(com|net|org|kr)|age1[a-z0-9]{50,}'`)
  - 현행 `GEMINI.md` 필수 계약·규칙 무손실 보존 확인 (`send_message`, `swarm`, `artifact`, `PreToolUse`, `token-usage.py`, `rp-pr-review`, `fan-in`, `ANTIGRAVITY_CONFIG_DIR`, `--auto`, `auto-memory`, `DROP`, `TRUNCATE`, `.git`, `harness-absolute-rules.md`, `harness-qa.md` 전부 포함)
  - `python3 scripts/sync-skills.py --check`, `python3 scripts/sync-codex-skills.py --check`, `python3 scripts/sync-skills.py --self-test`, `python3 scripts/token-usage.py --self-test`, `python3 .agents/hooks/sync-rp-skills.py --self-test` 전부 exit 0
  - `grep -En '경량 어댑터|8,?000|22,?000' CLAUDE.md README.md GEMINI.md .github/workflows/ci.yml` 잔존 문구 0건 확인
- **독립 리뷰 (머지 전):**
  - Antigravity `invoke_subagent`(`TypeName: "self"`) `[4]` 기획 리뷰 ∥ `[5]` 엔지니어링 리뷰 병렬 통과(각 평균 ≥8.0, 최저 ≥7)
  - `[9-코드]` 코드 리뷰 통과(평균 ≥8.0, 최저 ≥7; 메타 변경이므로 인프라 축 skip)
- **사용자 검증 게이트 (내부 시범 사용 — 머지 후 첫 Antigravity 세션):**
  - 머지 후 새 Antigravity 세션에서 (a) 별도 `read_file` 호출 없이 `GEMINI.md` 최하단 섹션(`## 기본 판단`) 내용이 컨텍스트에 로드됐는지 확인(truncation·파일 포인터 강등 여부 직접 관측), (b) 리뷰 도구 질의 시 `spawn_agent`가 아닌 `invoke_subagent`(`TypeName: "self"`) 기준으로 응답하는지 확인(합격선: 최하단 섹션 누락·`read_file` 강제 재조회·Codex 도구 혼선 각 0건; 실패 시 `GEMINI.md` 분량 압축 또는 롤백 PR 진행).

## 롤백 전략

- **코드·문서 원복:** 단일 PR(`feat/harness-gemini-adapter-full`) `git revert`로 `GEMINI.md`·`.github/workflows/ci.yml`·`CLAUDE.md`·`README.md`를 즉시 경량 어댑터 상태로 완전 원복 가능. 스킬·스크립트·훅 스키마 변경이 없어 양방향(롤백·롤포워드) 100% 호환.
- **부분 비활성화:** 별도 런타임 플래그 없음 — 문서·CI 상한 변경만 포함하므로 `git revert`가 유일하고 충분한 되돌리기 경로.
- **이상 판정 기준:** 머지 후 첫 Antigravity 세션(사용자 검증 게이트)에서 `GEMINI.md` 최하단 섹션(`## 기본 판단`) 누락 또는 `defaultRulesBudget` 초과에 따른 `read_file` 강제 재조회(포인터 강등) 관측 시 즉시 롤백 또는 분량 축소.
