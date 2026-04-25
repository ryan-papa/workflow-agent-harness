# PRD — 하네스 ignore 패턴 확장 r2 (실용 우선 추가)

| 항목 | 값 |
|------|----|
| 유형 | 하네스 메타 변경 (간소 PRD, 4섹션) |
| 브랜치 | `feat/harness-ignore-expand-r2` |
| 영향 범위 | 루트 `.claudeignore`, 루트 `.codexignore` (미러) |
| 선행 | r1 (`feat/harness-ignore-expand` PR #33 머지 완료) |

## 1. 변경 이유

r1으로 기본 누락 패턴을 막았으나, 실제 작업 중 폭발 위험이 큰 다음 카테고리가 여전히 노출:

- **ML 모델·웨이트** (단일 파일 GB 단위) — `*.pt`·`*.safetensors`·`*.onnx` 등. 한 번 잘못 Read하면 세션 즉사.
- **Cypress/Playwright 캐시·산출물** — `cypress/videos/`·`cypress/screenshots/`·`playwright/.cache/`. CI 실행 후 누적 시 수십 MB.
- **DB·힙 덤프** — `dump.rdb`·`*.bak`·`*.hprof`·`core.*`. 무가치 + 대용량.
- **Archive·패키지 바이너리** — `*.tar`·`*.dmg`·`*.deb` 등.
- **회전 로그·커버리지** — `*.log.*`·`lcov.info` 등 누적성.
- **추가 IDE 캐시·Python 캐시·락** — `.tox/`·`.nox/`·`.ipynb_checkpoints/`·`.fleet/`·`.zed/`·`Pipfile.lock` 외.
- **브라우저 드라이버 바이너리** — `chromedriver`·`geckodriver`.

`docs/prd/`는 통째 ignore 비권장(rp-ship 게이트·회고·감사 의존). 운영 정리(아카이브)로 별도 처리.

## 2. 영향 파일

| 파일 | 변경 |
|------|------|
| `.claudeignore` | 8개 신규 섹션 추가 (ML / Python 추가 / 회전로그 / 힙덤프 / DB 백업 / Cypress·Playwright / 드라이버 / IDE 추가 / 커버리지 / Archive) |
| `.codexignore` | `.claudeignore` 본문 동일 미러 (헤더만 차이) |

기존 규칙 삭제·수정 없음. 추가만 발생.

## 3. 롤백

- `git revert <commit>` 단발 커밋 — 즉시 원복.
- 기능적 의존성 없음. 회귀 시 토큰 절감 효과 소실뿐.

## 4. 검증

| # | 항목 | 방법 |
|---|------|------|
| 1 | 추가-only | `git diff main -- .claudeignore` 결과에 삭제 라인(`-` prefix, 헤더 변경 외) 0건 |
| 2 | 미러 정합성 | `diff <(tail -n +6 .claudeignore) <(tail -n +6 .codexignore)` 0 라인 |
| 3 | 회귀 없음 | `git check-ignore -v` 로 `repositories/**/src/`·`docs/`·`*.md` 미적용 확인 |
| 4 | 잠재 위험 패턴 | `*.bin`은 ML 외 일반 바이너리도 포착 가능 — 실제 코드/문서에 `*.bin` 의존 없음 확인 (현 레포 트리 grep 결과 0건) |
