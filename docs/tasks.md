# Tasks: SECURITY 가이드 + rp-init sops 자동화

PRD: `docs/prd/20260417_182747_security-guide_478d1984.md`
통합 브랜치: `feat/security-guide`

## 태스크 목록

| ID | 설명 | 매핑 F-XX | 상태 | 의존성 |
|----|------|-----------|------|--------|
| T-01 | `docs/security-guide.md` 작성 | F-01 | Done | — |
| T-02 | `docs/security/secrets-management.md` 작성 | F-02, F-06, F-07, F-08 | Done | T-01 |
| T-03 | `docs/templates/sops.yaml.template` (플레이스홀더) | F-03 | Done | — |
| T-04 | `docs/templates/env.example.template` | F-04 | Done | — |
| T-05 | `docs/skills/rp-init.md` 수정 | F-05 | Done | T-02, T-03, T-04 |
| T-06 | `CLAUDE.md` 갱신 | F-09 | Done | T-01, T-02 |
| T-07 | 검증 — 파일 존재·gitignore·키 노출·분량 확인 | — | Done | T-01..T-06 |

## 중간 변경 (Option A 도입)

- 공개키는 템플릿에 하드코딩하지 않고 `docs/security/recipients.local.md` (gitignored)에 관리
- `.gitignore`에 `recipients.local.md`, `.env`, `*.env` 추가 (`.env.enc` 예외)
- `recipients.local.md.example`로 구조 가이드 제공

## 검증 결과 (T-07)

| 항목 | 결과 |
|------|------|
| 전체 파일 생성 | ✅ |
| `recipients.local.md` gitignore 적용 | ✅ |
| 커밋 대상 파일 내 실제 공개키 노출 | ✅ 없음 |
| 개인 식별 정보 노출 | ✅ 없음 |
| 파일별 200줄 이하 | ✅ (최대 134줄) |
