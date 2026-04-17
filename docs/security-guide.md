# SECURITY Guide

claude-projects 공통 보안 규칙. 신규 프로젝트는 이 문서를 기준으로 시크릿·자격증명을 운영한다.

## 원칙

| 원칙 | 내용 |
|------|------|
| 시크릿 저장소 | sops + age 고정. 타 매니저 혼용 금지 |
| 평문 금지 | `.env` 평문은 로컬에만 존재. git에 커밋 금지 (`.gitignore` 필수) |
| 암호화 형식 | 모든 시크릿은 `.env.enc`(sops+age)로 저장, git 커밋 가능 |
| 공개 정보 범위 | 문서에는 **공개키**만 기재 가능. 비밀번호·호스트·계정명·포트·인증서 경로·내부 IP 금지 |
| 개인키 관리 | `~/.config/sops/age/keys.txt` + `~/Library/Application Support/sops/age/keys.txt` 동일본 2벌. 분실 대비 오프라인 백업 필수 |

## 하위 문서

| 문서 | 내용 |
|------|------|
| [`security/secrets-management.md`](security/secrets-management.md) | sops+age 세팅·운영·rotation·기기 추가·키 복구 |

## 템플릿

| 템플릿 | 용도 |
|--------|------|
| [`templates/sops.yaml.template`](templates/sops.yaml.template) | 새 프로젝트 `.sops.yaml` 초안 |
| [`templates/env.example.template`](templates/env.example.template) | 새 프로젝트 `.env.example` 초안 |

## 에이전트 참조 규칙

- `rp-init` 스킬은 이 문서를 읽고 템플릿 복사 + sops 암호화 단계를 수행한다. 상세: [`skills/rp-init.md`](skills/rp-init.md)
- 시크릿 관련 의사결정이 필요한 지점에서 에이전트는 이 문서의 "원칙" 테이블을 기준으로 판단한다.

## 금지 사항

- [ ] `.env` 커밋
- [ ] 비밀번호를 PR·이슈·문서·커밋 메시지에 포함
- [ ] 공개키 외 인프라 정보(호스트명, DB 계정명, 내부 IP 등) 문서 기재
- [ ] age 개인키를 git 레포·Slack·이메일로 공유
- [ ] `sops exec-env`에 dotenv 파일 사용 (포맷 미지원 — `eval "$(sops -d ...)"` 사용)
