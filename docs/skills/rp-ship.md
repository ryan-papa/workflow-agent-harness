---
description: '[11] 커밋·PR·CI·머지·배포. 수동 git/gh 우회 금지, 반드시 이 스킬 경유'
argument-hint: '[브랜치명] [변경 요약]'
---

# rp-ship

커밋 → PR → CI 확인 → 머지 → 배포.

## 트리거

- 산출물 보고 후 **사용자 승인** 시
- `/rp-ship` 명령

## 절차

### ⛔ 사전 체크 게이트 (커밋 전 필수)

커밋 직전 `<project-root>/docs/prd/[feature]/` 디렉터리에서 리뷰 증거 파일 존재를 검증. 누락 시 ship **중단**하고 해당 리뷰 단계로 복귀.

| PRD 유형 | 필수 파일 |
|---------|----------|
| 일반 기능 | `review-claude-plan-r{N}.md` + `review-codex-plan.md` + `review-claude-eng-r{N}.md` + `review-codex-eng.md` + `review-claude-code-r{N}.md` + `review-codex-code.md` |
| 하네스 메타 변경 | `review-claude-meta-r{N}.md` + `review-codex-meta.md` |
| 회고 반영 사이클 | 상기 조건 + `retro-r{N}.md`(반영 근거) |

검증 방식: **PRD 유형별 필수 파일을 개별적으로 존재 확인**. 부분 존재는 통과 불가.

```bash
# 일반 기능 — 6개 전부 존재해야 통과 (단, review-claude-*-r*.md는 최소 1개 이상 회차)
FEATURE=docs/prd/[feature]
for f in \
  "$FEATURE"/review-codex-plan.md \
  "$FEATURE"/review-codex-eng.md \
  "$FEATURE"/review-codex-code.md; do
  [ -f "$f" ] || { echo "MISSING: $f"; exit 1; }
done
# Claude 회차 파일은 단계별로 최소 1개
for stage in plan eng code; do
  ls "$FEATURE"/review-claude-${stage}-r*.md >/dev/null 2>&1 \
    || { echo "MISSING: review-claude-${stage}-r*.md"; exit 1; }
done

# 하네스 메타 변경 — 2종 존재 필수
ls "$FEATURE"/review-claude-meta-r*.md >/dev/null 2>&1 || exit 1
[ -f "$FEATURE"/review-codex-meta.md ] || exit 1
```

하나라도 누락 시 "리뷰 증거 부족 — 해당 리뷰 단계로 복귀" 메시지 출력 후 ship 중단.

### 자동 수행 (게이트 통과 시)
0. **PR base 결정 (fail-closed)**: 아래 "PR base 자동 감지" 섹션에 따라 감지. 비정상 상태는 ship 중단 후 사용자 확인 요구.
1. **커밋**: 변경 파일만 `git add` + `git commit`
2. **README 검증**: 푸시 전 README.md 점검 (아래 참조)
3. **푸시**: `git push -u origin [branch]`
4. **PR 상태 확인**: `gh pr list --head [branch] --state all --json number,state,baseRefName`
   - OPEN PR 존재 + base 일치 → 해당 PR 재사용
   - OPEN PR 존재 + base 불일치 → `gh pr edit <num> --base <detected-base>` 로 보정 후 **CI 재실행 대기 + 사용자 재승인 체크포인트** (base 변경은 diff 범위 재정의)
   - MERGED/CLOSED만 존재하거나 PR 없음 → 신규 PR 생성
5. **PR 생성/재사용**: `gh pr create --base <detected-base> ...` (제목 + 변경 요약 + 테스트 계획)
6. **CI 확인**: CI 통과 대기

### ⏸ 사용자 승인 대기
7. **배포 승인 요청**: PR URL + CI 결과를 사용자에게 보고, 배포 승인 대기
8. **머지**: 승인 후 `gh pr merge --merge`
9. **배포 확인**: 배포 워크플로우 완료 대기 + 결과 보고

## PR base 자동 감지

PR 생성/리타깃 전 **통합 브랜치 선언을 감지**해 `--base` 에 주입. `gh pr create` 기본값(레포 default branch)에 의존 금지.

### 감지 순서 (엄격)

| # | 소스 | 규칙 | 실패 시 |
|:-:|------|------|--------|
| 1 | 프로젝트 `docs/tasks.md` | 라인 시작 앵커 정규식 `^[\s\-\*|]*통합 브랜치:\s*`?([A-Za-z0-9/_\-]+)`?` 로 **정확히 1건** 매칭 | 2건 이상 → fail-closed / 0건 → 다음 소스 |
| 2 | 프로젝트 `CLAUDE.md` | 동일 정규식 정확히 1건 매칭 | 2건 이상 → fail-closed / 0건 → 다음 소스 |
| 3 | 레포 default branch | `gh repo view --json defaultBranchRef` | 결정 불가 → fail-closed |

**예시 (museum-finder `docs/tasks.md`)**: `- 통합 브랜치: \`feat/mvp-v1\` · 태스크 브랜치 \`feat/T-NN-{slug}\`` → `feat/mvp-v1` 1건 매칭 → `--base feat/mvp-v1`.

### 수동 오버라이드

사용자가 `rp-ship --base <X>` 로 명시 전달 시 자동 감지 **비활성화**하고 `<X>` 사용. 감지 로직을 거치지 않는 유일한 우회 경로.

### Fail-closed 조건 (ship 중단, 사용자 확인 요구)

- 감지된 브랜치 값에 공백/`\n` 포함
- 감지 정규식이 2건 이상 매칭 (모호성)
- 감지된 브랜치가 원격에 부재 (`git ls-remote --exit-code origin refs/heads/<base>` 실패)
- `HEAD` 가 detached 상태
- 프로젝트 루트(`.git` 디렉터리)를 찾지 못함
- 느슨한 브랜치명 추론(`feat/mvp-*` 등) 금지 — 반드시 `통합 브랜치:` 앵커 필드만 권위

## README 검증

커밋 후, 푸시 전에 README.md가 현재 프로젝트와 일치하는지 검증한다.

**검증 항목** (각 10점):

| # | 항목 |
|---|------|
| 1 | 프로젝트 개요 — 목적/기능 설명 일치 |
| 2 | 디렉토리 구조 — 주요 폴더/파일 반영 |
| 3 | 설치/실행 방법 — 의존성·스크립트 일치 |
| 4 | 기능 목록 — 구현된 주요 기능 기재 |
| 5 | 기술 스택 — 실제 사용 기술 명시 |

**통과:** 평균 8.0점 이상
**실패 시:** README 수정 → 재검증 (최대 3회) → 3회 실패 시 사용자 판단 위임

## CI 분기

```
PR 생성 시점에 .github/workflows/ 확인
  ├── CI 있음 → gh pr merge --merge --auto (CI 통과 대기)
  └── CI 없음 → "CI가 없습니다. 추가할까요?" 사용자에게 질문
       ├── 추가 원함 → CI 워크플로우 생성 후 재푸시
       └── 추가 안 함 → 사용자에게 수동 머지 안내
```

## 절대 규칙

- **CI 통과 전 머지 금지** (예외 없음)
- `--admin` 플래그로 강제 머지 **금지**
- **배포(머지) 전 사용자 승인 필수** — 커밋·PR까지는 자동, 머지는 승인 후
- **동일 브랜치 재PR**: MERGED/CLOSED된 PR이 있어도 신규 PR을 생성 (OPEN PR이 있을 때만 재사용)
- **feat·통합 브랜치 직접 배포 금지**: 프로덕션 프로세스(서버 재기동, 트래픽 수신) 는 **main 머지 이후**에만. 로컬 개발 서버(dev/`--reload`)는 예외.
- **QA·코드리뷰 이수 확인 게이트**: PR 생성 직전 `rp-qa` 와 `rp-code-review` 가 모두 완료 상태인지 체크. 하나라도 미완이면 ship 중단하고 해당 단계로 복귀.
- **리뷰 증거 파일 게이트**: 위 "사전 체크 게이트" 통과 없이 커밋 금지. 생략·우회 금지.
- **PR base 자동 감지 게이트**: 위 "PR base 자동 감지" 순서·fail-closed 조건을 모두 적용. 감지 생략·느슨한 브랜치 추론 금지. 수동 오버라이드(`--base <X>`)만 예외. base 리타깃 후에는 CI 재실행 + 사용자 재승인 필수.

## 머지 후 검증

- `git log [target-branch] --oneline -3`으로 커밋 반영 확인
- 배포 워크플로우 상태 확인: `gh run list --limit 1`
- 배포 완료 시 라이브 URL 안내

## 완료 조건

- PR 머지 완료
- 배포 워크플로우 성공
- 라이브 URL 사용자에게 전달

## ▶ 자동 전환

배포 완료 즉시 `✓ [11] 배포 완료` 출력 후 **`/rp-retro` 자동 진입** (생략 불가).

→ 배포 상세: [`../harness-ship.md`](../harness-ship.md)
