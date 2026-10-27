# Harness: 개발 단계

## 브랜치 전략

```
origin/[base]                      ← 베이스 (develop→main→master 순 자동 감지)
  └── feat/[project-name]          ← 통합 브랜치 (워크트리에서만 체크아웃)
       ├── feat/T-01-description   ← 태스크 브랜치
       ├── feat/T-02-description
       └── ...
  ← 최종 PR (통합 → base)
```

| 규칙 | 내용 |
|------|------|
| 베이스 감지 | 유저 미지정 시 `origin/develop → origin/main → origin/master` 순 첫 존재 채택. SSOT: [`harness-absolute-rules.md`](harness-absolute-rules.md) §배포·머지·브랜치 |
| 최신화 | 통합 브랜치 생성 전 `git fetch origin`, `origin/[base]` 기준 생성 (로컬 stale 금지) |
| 통합 브랜치 | `feat/[project-name]`, `origin/[base]`에서 생성, **워크트리에서만 체크아웃** |
| 태스크 브랜치 | `feat/T-XX-description`, 통합 브랜치에서 생성 (워크트리 내부) |
| 태스크 머지 | 태스크 → 통합 브랜치로 머지 (워크트리 내부) |
| 최종 머지 | 통합 브랜치 → base (PR) |
| **base 직접 push** | **금지** — 반드시 PR 경유 |

## 워크트리 격리 (서브 레포 한정)

통합 브랜치(=서로 다른 기능/프로젝트) 간 작업 공간을 분리해 파일 충돌·stale 머지를 방지한다. **하네스 메타 레포는 적용 외.**

| 규칙 | 내용 |
|------|------|
| 격리 단위 | 통합 브랜치 1개당 워크트리 1개. 동일 통합 브랜치 내 태스크는 단일 워크트리에서 순차 진행(에이전트당 1태스크 규칙) |
| 경로 | `repositories/[project]/worktrees/[통합브랜치명]/` (서브레포 내부, 서브레포 자체 `.gitignore`에 `worktrees/` 제외). 경로 leaf는 브랜치명 슬래시를 대시로 치환 (`feat/[project]` → `feat-[project]`) |
| 메인 클론 정책 | `repositories/[project]/`는 **베이스 브랜치에 유지**. 통합 브랜치는 워크트리에서만 체크아웃 → 동일 브랜치 동시 체크아웃 충돌(git 제약) 회피 |
| 생성 | `git -C repositories/[project] worktree add worktrees/feat-[project] -b feat/[project] origin/[base]` (경로는 `-C` 대상 서브레포 기준 상대경로 → `repositories/[project]/worktrees/feat-[project]`) |
| 베이스 부재 | `origin` 리모트 없거나 develop/main/master 모두 부재 시 **중단 + 사용자 질의** (임의 로컬 fallback 금지) |
| 재진입 | 워크트리 존재 시 재사용 + `git fetch`. clean이면 `origin/[base]` rebase 안내, **미커밋 변경 시 rebase 강행 금지 → 경고 후 사용자 선택(중단/stash)** |
| 정리 | PR 머지 후 `rp-ship`이 `git worktree remove`. 미커밋·미푸시 변경 시 **보류 + 사용자 알림**, 다음 `rp-dev` 진입 시 재확인 |

## 레포 초기화 체크리스트

신규 레포 생성 시 아래 설정 적용. **기존 CI/보호 설정이 있는 레포는 스킵.**

| 항목 | 내용 | 템플릿 |
|------|------|--------|
| 브랜치 프로텍션 | main 직접 push 금지, PR 필수 | `gh api` 설정 |
| PR CI | 빌드 + 테스트 자동 실행, 실패 시 머지 차단 | [`templates/ci-pr.yml`](templates/ci-pr.yml) |
| 시크릿 스캔 | GitHub 기본 secret scanning + push protection | 레포 Settings |
| 머지 조건 | CI 전체 통과 필수 | 브랜치 프로텍션에 포함 |

**적용 판단:**
- `.github/workflows/` 에 CI 파일이 이미 있으면 → CI 템플릿 스킵
- 브랜치 프로텍션이 이미 설정되어 있으면 → 프로텍션 스킵

**머지 후 검증 (필수):**
- `git log [target-branch] --oneline -3`으로 커밋 반영 확인
- 머지 실패 시: 에이전트가 충돌 해결 시도, 불가 시 사용자 보고

## 태스크 분해

- Claude가 PRD 기능 요구사항 기반으로 자동 분해
- 태스크 목록 파일: `repositories/[project]/docs/tasks.md`

| 항목 | 내용 |
|------|------|
| ID | T-01, T-02... |
| 설명 | 구현 내용 |
| 상태 | Todo / In Progress / Done |
| 브랜치 | `feat/T-01-[description]` |

## 스펙 변경 시 플로우

기능 추가/변경/삭제 요청 시: 질문으로 구체화 → PRD 업데이트 → 기획리뷰 → 엔지니어링리뷰 → 코드 작업

**원칙:** 코드보다 문서가 먼저. 문서 없이 코드 수정 금지.
**리뷰 범위:** 전체 PRD가 아닌 변경된 부분에 한해서 수행.

## 태스크별 개발 사이클

브랜치 생성 → 개발(1태스크/에이전트) → 빌드+테스트 검증 → 유닛테스트 작성+실행 → 통합 브랜치 머지+검증
- 실패 시 에이전트 재투입 (최대 3회)

**⛔ 절대 규칙 (위반 시 즉시 중단):**
- **에이전트당 1태스크만 위임** (여러 태스크 한번에 금지)
- 에이전트 완료 후 **빌드 + 테스트 직접 실행하여 검증** (에이전트 보고만 믿지 않음)
- 테스트 코드 없이 커밋/머지 금지
- 테스트 미통과 상태에서 다음 태스크 진행 금지
- 빌드 실패 상태에서 다음 태스크 진행 금지
- 이 규칙은 "급해서", "간단해서", "나중에" 등 어떤 이유로도 예외 불가

**테스트 규칙:**
- 비즈니스 로직·DB 접근 중심으로 작성 (trivial 코드 제외)
- 프론트엔드는 빌드 통과 + 컴포넌트 렌더링 테스트 필수
- 테스트 실패 시 Dev Agent 자동 수정 (최대 3회)
- pre-commit/pre-push 훅이 테스트 미통과 시 커밋·푸시 차단

**각 태스크 완료 시 필수 체크:**
- [ ] 테스트 코드 작성됨
- [ ] 테스트 전체 통과
- [ ] 빌드 성공
- [ ] 통합 브랜치 머지 + git log 검증

**자동 진행 원칙:**
- 검증 통과 시 사용자에게 묻지 않고 다음 태스크 자동 진행
- 검증 실패 시에만 멈추고 보고
- 전체 태스크 완료 후 QA 단계로 자동 전환

## 코드 작성 참고 (중복·구조)

> 참고 가이드 — 이 절 자체는 리뷰 감점·차단 근거가 아니다.

| 구분 | 내용 |
|------|------|
| 추출 고려 | 이번 변경 범위에서 **같은 로직이 2회 이상 반복**되면 메서드·유틸·클래스로 추출해 중복을 제거한다 |
| 피할 것 | 다른 동작을 **플래그·파라미터 추가로 한 메서드에 합치기** · 한 클래스에 책임 몰아넣기 · 사용처 1곳뿐인 선제 일반화 |
| 범위 | 이번 변경이 건드리는 코드 안의 중복만. 무관한 기존 코드 리팩터는 CLAUDE.md Surgical 원칙 적용 |

## 다음 단계

개발 완료 후 자동 전환:

| 단계 | 상세 문서 |
|------|----------|
| QA + 콘텐츠 검수 | [`harness-qa.md`](harness-qa.md) |
| 코드 리뷰 (7항목) | [`harness-code-review.md`](harness-code-review.md) |
| 산출물 보고 + 배포 | [`harness-ship.md`](harness-ship.md) |
| README 규칙 | [`harness-readme.md`](harness-readme.md) |
