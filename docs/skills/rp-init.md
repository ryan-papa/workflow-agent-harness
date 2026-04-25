---
description: '[1] 프로젝트 초기화. CLAUDE.md·README.md·PRD 디렉터리 등 기본 구조 생성'
argument-hint: '[프로젝트명] [유형: 코드|콘텐츠]'
model: sonnet
---

# rp-init

프로젝트 초기화 + 레포 셋업.

## 트리거

- 새 프로젝트 시작 시
- `/rp-init` 명령

## 절차

1. `repositories/[project]/` 디렉토리 생성
2. `CLAUDE.md` 생성(프로젝트별 규칙, 아래 템플릿 적용)
3. `README.md` 생성(유형별 템플릿 적용)
4. `docs/prd/`, `docs/research/` 디렉토리 생성
5. Git 레포 초기화 또는 기존 레포 확인
6. 브랜치 프로텍션 설정(기존 설정 있으면 스킵)
7. **시크릿 관리 세팅** — 아래 "시크릿 세팅" 블록 수행

## README 템플릿 선택

| 유형 | 템플릿 |
|------|--------|
| 오픈소스/라이브러리 | [`templates/readme-opensource.md`](../templates/readme-opensource.md) |
| 사내 서비스/API | [`templates/readme-service.md`](../templates/readme-service.md) |

## CLAUDE.md 템플릿

서브 레포 CLAUDE.md 최상단에 반드시 아래 문구 포함:

```markdown
> 이 문서는 프로젝트 로컬 규칙이며 최우선 적용된다.
> 상위 공통 규칙(`../../CLAUDE.md`)을 부차적으로 반드시 함께 적용한다.
> 충돌 시 본 문서(프로젝트)가 우선한다.
```

## 레포 초기화 체크리스트

- [ ] 브랜치 프로텍션(main 직접 push 금지, PR 필수)
- [ ] 시크릿 스캔(GitHub push protection)
- [ ] 기존 CI·보호 설정 있으면 스킵

## 신규 rp-* 스킬 추가 체크리스트

새 하네스 스킬(`rp-*.md`)을 만들 때:
- [ ] `docs/skills/rp-<이름>.md` 생성(YAML frontmatter `description` + `argument-hint` 포함)
- [ ] `.claude/commands/rp-<이름>.md` 심링크 확인 — `PostToolUse` 훅이 자동 생성. 미생성 시 수동 fallback: `cd .claude/commands && ln -s ../../docs/skills/rp-<이름>.md rp-<이름>.md`
- [ ] `CLAUDE.md`·`docs/harness-workflow.md`·`docs/skills/rp-workflow.md` 트리·링크 갱신
- [ ] `/reload-plugins` 후 자동완성에서 노출 확인

## 시크릿 세팅

[`../security-guide.md`](../security-guide.md) 원칙을 따른다. 상세 절차: [`../security/secrets-management.md`](../security/secrets-management.md)

에이전트 실행 순서:

1. 전제조건 확인
   - sops·age 설치 여부(`command -v sops age`) — 미설치면 [`../security/secrets-management.md`](../security/secrets-management.md) "기기 초기 세팅" 안내 후 대기
   - `claude-projects/docs/security/recipients.local.md` 존재 여부 — 없으면 `recipients.local.md.example` 복사 후 사용자에게 공개키 입력 요청

2. 템플릿 복사 + 공개키 치환
   ```bash
   cp ../../docs/templates/sops.yaml.template .sops.yaml
   cp ../../docs/templates/env.example.template .env.example
   ```
   → `.sops.yaml`의 `age1PLACEHOLDER_...` 라인을 `recipients.local.md`의 실제 공개키로 치환 후 플레이스홀더 전부 삭제

3. `.gitignore`에 `.env` 없으면 추가(`.env.enc`는 제외 금지)

4. 사용자에게 `.env.example` 기반 `.env` 작성 요청 → 응답 대기

5. 사용자 응답 후 암호화
   ```bash
   sops -e --input-type dotenv --output-type dotenv .env > .env.enc
   ```

6. 커밋
   ```bash
   git add .sops.yaml .env.enc .gitignore .env.example
   ```

**중단 조건:**
- sops/age 미설치 → 사용자 안내 후 대기
- `recipients.local.md` 부재 → 템플릿 제시 후 사용자 입력 대기

## 완료 조건

- 디렉토리 구조 생성 완료
- CLAUDE.md, README.md 존재
- Git 레포 정상 상태

## ▶ 자동 전환

완료 즉시 `✓ [1] 초기화 완료` 출력 후 **`/rp-specify` 자동 진입**.

→ 개발 상세: [`../harness-dev.md`](../harness-dev.md)
