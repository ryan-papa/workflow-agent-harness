# Claude Meta Review — harness-ignore-expand-r2 (r1)

| 항목 | 점수 | 근거 |
|------|:----:|------|
| 1. 변경 이유 명확성 | 9 | 7개 카테고리 명시 + 각 위험성(GB 단위·세션 즉사·누적성) 구체. `docs/prd/` 전체 ignore 비채택 근거도 기재. |
| 2. 영향 파일 정확성 | 10 | `git diff main --stat`: `.claudeignore`/`.codexignore` 각 +68 라인. PRD 기재(루트 2파일, 추가-only)와 정확히 일치. |
| 3. 롤백 계획 | 9 | 단발 커밋 → `git revert` 1회. 의존성 없음 명기. 충분. |
| 4. 검증 방법 구체성 | 9 | 4항목(추가-only diff·미러 diff·`check-ignore` 회귀·`*.bin` 의존 0건) 각각 실행 가능 명령 제시. |
| 5. 변경 안전성 | 9 | 위험 패턴 실측: `git ls-files \| grep -E '\.(tar\|pkl\|onnx\|h5\|safetensors\|hdf5\|npz\|npy\|ckpt\|hprof\|lcov\|suo\|tgz\|iso\|dmg\|deb\|rpm\|bin)$'` → 0건. 현 레포 가림 없음 확인. |
| 6. .codexignore 미러 정합성 | 10 | `diff <(tail -n +6 .claudeignore) <(tail -n +6 .codexignore) \| wc -l` → 1 (trailing newline diff 1줄, 본문 차이 0). 헤더 외 본문 동일. |

**평균: 9.33 / 10**
**판정: 통과 (8.0 이상)**

## High/Critical 지적
- 없음.

## Minor (참고)
- `*.bin` 패턴은 .NET `bin/` 디렉터리(이미 ignore)와 별개로 일반 firmware/raw 바이너리도 포착. 현 시점 영향 0이지만, 향후 신규 레포 추가 시 `git check-ignore` 사전 점검 권장.
- `core.*` 패턴은 `core.js`·`core.ts` 같은 소스를 가릴 위험. 현재 레포에 매칭 0건이나 Node/Python 프로젝트 합류 시 재확인 필요.
- 검증 #2가 `tail -n +6` 비교로 헤더 5줄을 건너뛰는데, 실제 헤더는 `.claudeignore` 5줄 / `.codexignore` 6줄로 비대칭. 현재 1라인 잔차(trailing) 발생 — 다음 r3에서 헤더 줄수 통일 또는 `tail -n +N` 비대칭 처리 권장.
