# rp-init

프로젝트 초기화 + 레포 셋업.

## 트리거

- 새 프로젝트 시작 시
- `/rp-init` 명령

## 절차

1. `repositories/[project]/` 디렉토리 생성
2. `CLAUDE.md` 생성 (프로젝트별 규칙, 아래 템플릿 적용)
3. `README.md` 생성 (유형별 템플릿 적용)
4. `docs/prd/`, `docs/research/` 디렉토리 생성
5. Git 레포 초기화 또는 기존 레포 확인
6. 브랜치 프로텍션 설정 (기존 설정 있으면 스킵)

## README 템플릿 선택

| 유형 | 템플릿 |
|------|--------|
| 오픈소스/라이브러리 | [`templates/readme-opensource.md`](../templates/readme-opensource.md) |
| 사내 서비스/API | [`templates/readme-service.md`](../templates/readme-service.md) |

## CLAUDE.md 템플릿

서브 레포의 CLAUDE.md 최상단에 반드시 아래 문구를 포함한다:

```markdown
> 이 문서는 프로젝트 로컬 규칙이며 최우선 적용된다.
> 상위 공통 규칙(`../../CLAUDE.md`)을 부차적으로 반드시 함께 적용한다.
> 충돌 시 본 문서(프로젝트)가 우선한다.
```

## 레포 초기화 체크리스트

- [ ] 브랜치 프로텍션 (main 직접 push 금지, PR 필수)
- [ ] 시크릿 스캔 (GitHub push protection)
- [ ] 기존 CI/보호 설정 있으면 스킵

## 완료 조건

- 디렉토리 구조 생성 완료
- CLAUDE.md, README.md 존재
- Git 레포 정상 상태

## ▶ 자동 전환

완료 즉시 `✓ [1] 초기화 완료` 출력 후 **`/rp-specify` 자동 진입**.

→ 개발 상세: [`../harness-dev.md`](../harness-dev.md)
