# PRD: Antigravity 런타임 지원 정합성·안정성 보강

**상태:** Approved ([4] 8.56 · [5] 8.2 · [9-코드] 2회차 8.86)
**유형:** 하네스 메타 변경 (간소 PRD)

---

## 변경 이유

| # | 문제 | 근거 |
|:-:|------|------|
| 1 | `scripts/token-usage.py`의 `agy_extract_subagents()`가 `GENERIC` 행 `content` 전체를 비앵커 정규식으로 탐색해 일반 명령/파일 출력 내 동일 패턴을 자식 세션으로 오탐 가능 | PR #91 `rp-pr-review` Medium #1 — transcript 조회·`git diff`·로그 출력에 `Created the following subagent:` 문자열이 섞이면 거짓 `(메인만)` 또는 타 세션 토큰 혼입 위험 |
| 2 | `scripts/token-usage.py`에서 병렬 자식 중 일부만 누락/UTF-8 손상 실패 시, 이미 합산된 다른 자식 토큰이 남은 채 `(메인만)` 라벨이 출력돼 라벨과 수치 모순 | PR #91 `rp-pr-review` Medium #2 — `missing_child=True` 경로에서 `totals`에 선행 자식 합계가 잔류 |
| 3 | `scripts/sync-skills.py`의 `sync_claude_links()`에 락·`FileExistsError` 방어가 없어 신규 스킬 병렬 훅 실행 시 후발 훅이 예외로 중단 가능 | PR #91 `rp-pr-review` Low #3 — `sync_target()`과 달리 선행 심링크 생성 구간 미보호 |
| 4 | `scripts/sync-codex-skills.py` 호환 래퍼가 임의 인자를 그대로 넘겨 `--target antigravity` 전달 시 Codex가 아닌 Antigravity 타겟 실행 | PR #91 `rp-pr-review` Low #4 — `argparse` 후행 인자 우선 규칙으로 호환 래퍼 계약 일탈 |
| 5 | `README.md` 트리·설명에 백엔드 테스트 정책 `4-게이트`(실제 SSOT `2-게이트`) 오기 및 핵심 `docs/` 파일 4종 누락 | 전체 정합성 감사 Low #5 — `CLAUDE.md`·`docs/harness-backend-test-policy.md` SSOT 불일치 |
| 6 | `GEMINI.md`에 자동 선택 임계값 수치(`9.0`)가 직접 기재되어 추후 `CLAUDE.md` 변경 시 드리프트 위험 | 전체 정합성 감사 Low #6 — `AGENTS.md`와 동일하게 `CLAUDE.md` SSOT 참조로 통일 필요 |

## 결정 사항

| # | 항목 | 결정 | 기각 대안 | 근거 유형 |
|:-:|------|------|-----------|-----------|
| 1 | `token-usage.py` 서브에이전트 패턴 앵커링 | **가정:** `AGY_SUBAGENT_RE`를 `content` 시작부(`^(?:(?:Created\|Completed) At:[^\r\n]*\r?\n\|[ \t]*\r?\n)*Created the following subagent:\s*\{\s*"conversationId"\s*:\s*"([^"]+)"`)로 앵커링하고 `re.match` 적용(수평 공백 `[ \t]*` 한정으로 ReDoS 차단, 실제 세션 `invoke_subagent` `GENERIC` 원문 형식 대조 확인). 1 `GENERIC` 행 = 1 서브에이전트 전제이며, 향후 Antigravity 헤더 포맷 변경 시 미탐 리스크는 `[9]` 실측 게이트·`--self-test` 헤더 픽스처로 탐지 | `re.findall` 유지 + 블랙리스트 키워드 제외(신규 도구 출력마다 누락) · JSON 전체 파싱(헤더 텍스트 혼재로 실패) | 엔지니어 선호 |
| 2 | `token-usage.py` 부분 자식 누락 시 합계 정책 | **가정:** 메인 합계(`main_totals`)와 자식 합계(`children_totals`)를 분리 유지. 각 자식은 임시 딕셔너리(`child_totals`)와 임시 서브에이전트 목록으로 끝까지 예외 없이 파싱된 경우에만 병합하고, 1건이라도 누락/실패(손자 포함)로 `missing_child=True` 확정 시 즉시 BFS 루프를 `break`하고 `main_totals`만 반환해 `(메인만)` 라벨과 수치를 100% 일치시킴 | 부분 합계 반환 + `(부분 누락)` 신규 라벨 도입(기존 `docs/harness-workflow.md` 출력 규격 변경 필요) · 전체 `Fail` 실패 처리(과도한 실패) | 엔지니어 선호 |
| 3 | `sync_claude_links()` 동시성 방어 | **가정:** 기존 `_dest_lock(commands_dir)` 재사용 + `with contextlib.suppress(FileExistsError):` 내부에 `link.symlink_to(...)`와 `created.append(source.name)`를 함께 배치(경합 실패 시 `created` 반환 목록 미포함) | `FileExistsError` 무시만 적용(락 없음) · 별도 락 구현(중복) | 엔지니어 선호 |
| 4 | `sync-codex-skills.py` 래퍼 인자 격리 | **가정:** 래퍼에서 Codex 전용 인자(`--check`, `--install-user`)만 `argparse`로 파싱 후 `sync_skills.main(["--target", "codex", ...])` 호출(`--target`·`--sync-claude-links` 등 미지원 인자는 `argparse` exit 2로 거부). 래퍼 거부 회귀 검증은 `scripts/sync-skills.py --self-test`에 편입해 CI에서 상시 검증 | `forwarded` 문자열 블랙리스트 검사(`--target=foo` 등 우회 취약) · 래퍼 삭제(하위 호환 파괴) | 엔지니어 선호 |
| 5 | 문서 정합성 정리 | **가정:** `README.md`의 `4-게이트` → `2-게이트` 교정 및 누락 4파일(`harness-infra-review.md`, `harness-trust-boundary.md`, `prd-template.md`, `tasks.md`) 트리 보강; `GEMINI.md`의 `1위 ≥ 9.0 단독` → `임계값·예외는 CLAUDE.md SSOT`로 치환 | `GEMINI.md` 수치 유지(드리프트 위험) · `README.md` 트리 축소 | 엔지니어 선호 |

## 스코프 · 경계 · 예외 분기

- **In-Scope:** `scripts/token-usage.py`, `scripts/sync-skills.py`, `scripts/sync-codex-skills.py`, `README.md`, `GEMINI.md` 5개 파일 보강 및 내장 `--self-test` 회귀 테스트 추가.
- **Out-of-Scope:** `docs/harness-workflow.md` 출력 형식 변경, `CLAUDE.md`·`AGENTS.md`·`docs/skills/` 구조 변경, 로컬 미커밋 파일(`.claude/settings.json`) 수정, 글로벌 스킬 설치(`--install-user` 수동 실행).
- **예외·분기 처리:**
  - `agy_extract_subagents()`: `Created At:`/`Completed At:` 헤더·빈 줄이 0회 이상 반복된 직후 `Created the following subagent:`가 나오는 실제 `invoke_subagent` `GENERIC` 응답만 매칭; `Command exited with code`·`Showing lines` 등 일반 도구 출력 내 동일 문자열은 무시.
  - `agy_usage()`: 자식·손자 1건이라도 누락되거나 파일 중간에 `UnicodeDecodeError` 발생 시 임시 `child_totals` 폐기 + `missing_child=True` 확정 즉시 `break` → `main_totals`만 반환(부분 오염·잔여 I/O 0).
  - `sync_claude_links()`: 락 해제 전 예외 발생 시에도 `finally`에서 안전 해제, 이미 심링크 존재하거나 `FileExistsError` 경합 시 `created`에 미포함·idempotent 무오류 반환.
  - `sync-codex-skills.py`: `--check`, `--install-user`, `-h`/`--help`만 허용, `--target`·`--sync-claude-links` 전달 시 exit 2 + stderr 사용법 출력.

## 우선순위 · 구현 순서

1. **P0 (정확성):** `scripts/token-usage.py` 앵커링 + `main_totals` 분리·조기 `break` + `--self-test` 양성/음성/부분누락 회귀 케이스
2. **P1 (안정성·계약):** `scripts/sync-skills.py` `sync_claude_links()` 락/예외 방어 + `scripts/sync-codex-skills.py` 전용 `argparse` + `sync-skills.py --self-test` 내 경합·래퍼 거부 회귀 테스트 편입
3. **P1 (문서 정합):** `README.md`·`GEMINI.md` 교정

전 항목을 단일 PR 단위로 일괄 ship한다(부분 ship 없음).

## 영향 파일

| 파일 | 역할·변경 내용 |
|------|---------------|
| `scripts/token-usage.py` | `AGY_SUBAGENT_RE` 시작부 앵커링(`re.match`), `main_totals`/`children_totals` 분리·부분 누락 시 조기 `break` 및 `main_totals` 반환, 헤더 양성·오탐 차단·부분 누락 회귀 테스트 추가 |
| `scripts/sync-skills.py` | `sync_claude_links()`에 `_dest_lock(commands_dir)` + `FileExistsError` 방어(`created` 정합), `self_test()`에 경합·idempotency 및 `sync-codex-skills.py` 미지원 인자 거부 검증 추가 |
| `scripts/sync-codex-skills.py` | Codex 전용 인자(`--check`, `--install-user`)만 파싱하도록 제한(`--target`·`--sync-claude-links` 오버라이드 차단) |
| `README.md` | 백엔드 테스트 정책 `4-게이트` → `2-게이트` 교정, 트리에 누락 `docs/` 4파일 추가 |
| `GEMINI.md` | 자동 선택 임계값 하드코딩 수치(`9.0`) 제거 → `CLAUDE.md` SSOT 참조로 통일 |

## 검증

- **자동화·로컬 CI (머지 전):**
  - `python3 scripts/token-usage.py --self-test` (`Created At:`/`Completed At:` 헤더 포함 양성 매칭 + `Command exited with code`/`Showing lines` 일반 도구 출력 오탐 차단 + 정상 자식+누락/손상 자식 혼합 시 `main_totals` 반환·조기 탈출 검증 포함)
  - `python3 scripts/sync-skills.py --self-test` (`sync_claude_links` idempotency·`FileExistsError` 경합 + `sync-codex-skills.py` `--target`/`--target=antigravity`/`--sync-claude-links` exit 2 거부 포함)
  - `python3 scripts/sync-skills.py --check`, `python3 scripts/sync-codex-skills.py --check`, `python3 .agents/hooks/sync-rp-skills.py --self-test`
  - 로컬 CI 동등 검사(필수 파일·500줄·규칙 바이트 예산·내부 링크·서브레포 링크·민감 정보 스캔)
- **독립 리뷰 (머지 전):**
  - Antigravity `invoke_subagent`(`TypeName: "self"`) `[4]` 기획 리뷰 ∥ `[5]` 엔지니어링 리뷰 병렬 통과, `[9-코드]` 코드 리뷰 통과(메타 변경 인프라 축 skip)
- **사용자 검증 게이트 (본 세션 양방향 실측):**
  - **게이트 1 (`[8]` 메타 QA 실측):** 서브에이전트 없는 단계에서 `token-usage.py` 실행 → `집계 실패`·거짓 `(메인만)` 없이 정상 출력 확인.
  - **게이트 2 (`[9-코드]` 리뷰 실측):** 실제 `invoke_subagent` 자식이 실행된 단계에서 `token-usage.py` 실행 → 앵커링 정규식이 실제 자식을 미탐 없이 정상 합산해 출력하는지 확인(실패 시 즉시 수정).

## 롤백 전략

- 단일 PR(`feat/harness-antigravity-hardening`) `git revert`로 완전 원복 가능. 외부 스키마·인터페이스 파괴 없음(기존 `sync-codex-skills.py --check`/`--install-user` 및 `token-usage.py` 출력 형식 100% 유지).
