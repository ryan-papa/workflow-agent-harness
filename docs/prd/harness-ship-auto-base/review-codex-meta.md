# Codex Meta Review — harness-ship-auto-base

**대상 PRD:** docs/prd/harness-ship-auto-base/prd.md
**영향 파일:** docs/skills/rp-ship.md · docs/harness-ship.md · CLAUDE.md
**실행일:** 2026-04-22
**점수화:** 없음 (High/Critical 지적 위주)

---

## 리뷰 결과

### [HIGH] 문서 미반영 — PRD 구현이 impacted docs에 없음

**영향 파일:** docs/skills/rp-ship.md (L51), docs/harness-ship.md (L15), CLAUDE.md (L115)

**설명:**
impacted docs가 PRD를 구현하지 않고 있다. `rp-ship.md`는 여전히 `PR base 결정` 단계 없이 단순 `gh pr create`만 문서화하고 있고, `harness-ship.md`는 flow와 CI 규칙에서 base 감지를 생략하며, `CLAUDE.md`에는 `rp-ship PR base 자동 감지 게이트`가 없다. 현재 문서 상태에서는 레포지터리 기본 브랜치로 향하도록 안내되고 있어 PRD가 설명하는 wrong-base 실패가 여전히 발생 가능하다.

**권장 수정:**
세 문서를 원자적으로 업데이트하여 동일한 강제 동작을 명시할 것: PR 생성/조회 전 base 결정, 생성 시 `--base <detected-base>` 전달, 리타겟 가드레일 문서화, `CLAUDE.md`에 절대 규칙 게이트 추가.

---

### [HIGH] 불안전한 감지 규칙 — 오탐(false-positive) 위험

**영향 파일:** docs/prd/harness-ship-auto-base/prd.md (L20)

**설명:**
제안된 감지 규칙이 `docs/tasks.md`의 명시적 `통합 브랜치:` 필드 또는 `feat/mvp-*` 패턴 매칭 두 가지 모두에서 PR base를 추출하도록 허용한다. tasks 파일은 예시, 히스토리, 여러 브랜치 레퍼런스를 포함할 수 있으며 PRD는 앵커링이나 유일성을 요구하지 않는다. 이 값이 `gh pr create --base`와 `gh pr edit --base`에 직접 공급되므로 오탐 매칭 시 PR이 잘못된 통합 브랜치로 전송될 수 있다.

**권장 수정:**
`통합 브랜치:` 필드만 `tasks.md`의 유일한 권위 있는 소스로 취급할 것. 앵커링된 규칙으로 파싱하고 정확히 하나의 매칭을 요구하며 모호 시 fail-closed. 없는 경우 프로젝트 `CLAUDE.md`의 동등하게 명시적인 필드로만 폴백하고, 느슨한 브랜치명 regex 매칭으로 base를 추론하지 말 것.

---

### [HIGH] 실패 경로 미정의 — fail-closed 경로 및 탈출구 없음

**영향 파일:** docs/prd/harness-ship-auto-base/prd.md (L14)

**설명:**
PRD는 기본 브랜치 자동 폴백과 `gh pr edit --base` 자동 리타겟팅을 정의하지만, 비정상 브랜치 상태에 대한 fail-closed 경로나 탈출구가 없다. detached HEAD, 프로젝트 루트 미확인, 누락/stale 원격 대상 브랜치, 복수 선언, 또는 리타겟 후 검토 diff가 실질적으로 변경된 기존 OPEN PR에 대한 처리가 명시되지 않았다. 이로 인해 자동화가 잘못된 브랜치로 작업을 조용히 리포인트하거나 명시적 체크포인트 없이 리뷰/CI 범위를 변경할 수 있다.

**권장 수정:**
명시적 abort 조건과 수동 오버라이드 경로를 추가할 것. 모호하거나 비정상 레포 상태에서는 멈추고 명시적 사용자 확인을 요구. OPEN PR이 리타겟되면 CI 재실행과 머지 전 새 승인 체크포인트 필요. `--base` 명시적 오버라이드 또는 해당 실행의 auto-detect 비활성화 지시 등 탈출구를 문서화할 것.

---

## 총평

High 심각도 이슈 3건 발견. Critical 이슈 없음.

PRD 자체의 의도(wrong-base 실수 방지)는 타당하나, (1) 문서 반영 완료 여부 확인 필요, (2) 감지 로직의 안전성 강화, (3) 비정상 상태 fail-closed 처리 명시가 선행되어야 다음 단계 진입 가능.

---

## 반영

| # | Codex 지적 | 반영 파일 / 라인 | 요약 |
|:-:|-----------|-----------------|------|
| 1 | HIGH — 문서 미반영 | `docs/skills/rp-ship.md` (0단계 + PR base 자동 감지 섹션 + 절대 규칙 게이트), `docs/harness-ship.md` (흐름도 `PR base 결정` 단계 + CI 규칙 표 항목), `CLAUDE.md` (절대 규칙 1줄 추가) | 세 문서 원자 업데이트. PR 생성·리타깃 로직·CI 재실행·사용자 재승인 체크포인트 포함 |
| 2 | HIGH — 불안전 감지 규칙 | `docs/prd/harness-ship-auto-base/prd.md` + 3개 구현 문서 | 앵커링 정규식 `^[\s\-\*\|]*통합 브랜치:\s*` + 정확히 1건 매칭 강제 + 느슨한 `feat/*` 추론 금지 명문화. `통합 브랜치:` 필드만 유일 권위 소스 |
| 3 | HIGH — 실패 경로 미정의 | PRD + `rp-ship.md` Fail-closed 조건 블록 | detached HEAD · 프로젝트 루트 미확인 · 원격 부재 · 공백 포함 · 2건+ 매칭 시 ship 중단 + 사용자 확인. 수동 오버라이드(`rp-ship --base <X>`) 탈출구 추가. OPEN PR 리타깃 시 CI 재실행 + 사용자 재승인 필수 |

3건 모두 반영 완료. 다음 단계 rp-ship 진입.
