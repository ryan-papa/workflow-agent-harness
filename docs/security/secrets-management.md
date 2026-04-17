# Secrets Management (sops + age)

sops + age 기반 시크릿 운영 상세. 모든 명령은 프로젝트 레포 루트에서 실행.

## 기기 초기 세팅 (1회)

```bash
brew install sops age

# age 키 생성 (~/.config/sops/age/keys.txt + macOS 기본 경로 양쪽에 배치)
mkdir -p ~/.config/sops/age "$HOME/Library/Application Support/sops/age"
age-keygen -o ~/.config/sops/age/keys.txt
chmod 600 ~/.config/sops/age/keys.txt
cp ~/.config/sops/age/keys.txt "$HOME/Library/Application Support/sops/age/keys.txt"

# 공개키 출력 (이 값만 공유 가능)
grep "public key" ~/.config/sops/age/keys.txt
```

**개인키(`keys.txt`) 백업:** 분실 시 `.env.enc` 복호화 불가. 오프라인 매체에 반드시 백업.

## 신규 프로젝트 초기화

```bash
cd /path/to/new-repo

# 1. 템플릿 복사 (claude-projects 상대경로 기준)
cp ../../docs/templates/sops.yaml.template .sops.yaml
cp ../../docs/templates/env.example.template .env.example

# 2. .sops.yaml의 age1PLACEHOLDER... 를 실제 공개키로 치환
#    공개키는 ../../docs/security/recipients.local.md 참조
$EDITOR .sops.yaml

# 3. .env 작성 (평문, 로컬 전용)
cp .env.example .env
$EDITOR .env

# 4. .gitignore에 .env 추가
echo ".env" >> .gitignore

# 5. 암호화
sops -e --input-type dotenv --output-type dotenv .env > .env.enc

# 6. 커밋
git add .sops.yaml .env.enc .gitignore .env.example
git commit -m "chore: sops 시크릿 관리 초기 세팅"
```

## 일상 운영

| 작업 | 명령 |
|------|------|
| 복호화 (표준 출력) | `sops -d --input-type dotenv --output-type dotenv .env.enc` |
| 편집 (자동 복호화→편집→재암호화) | `sops .env.enc` |
| 로컬 `.env` 재생성 | `sops -d --input-type dotenv --output-type dotenv .env.enc > .env` |
| 런타임 주입 (bash) | 하단 "실행 래퍼 패턴" 참조 |

## 기기 추가 (공개키 등록)

```bash
# 1. 신규 기기에서 "기기 초기 세팅" 수행 후 공개키 획득
# 2. 해당 공개키를 .sops.yaml의 age: 리스트에 추가 (기존 기기에서)
# 3. 기존 .env.enc 재암호화 (sops updatekeys는 dotenv에서 실패하므로 재암호화 사용)
sops -d --input-type dotenv --output-type dotenv .env.enc > /tmp/plain.env
rm .env.enc
sops -e --input-type dotenv --output-type dotenv /tmp/plain.env > .env.enc
rm /tmp/plain.env

# 4. 커밋 + 푸시
git add .sops.yaml .env.enc
git commit -m "chore: add <device> public key to sops"
git push
```

## 기기 제거 (공개키 폐기)

동일 절차 — `.sops.yaml`에서 공개키 라인 삭제 후 재암호화. 폐기 후에도 시크릿 값이 외부에 노출됐다면 **비밀번호·토큰 rotation 필수** (암호화 제거만으론 과거 파일의 복호화를 막지 못함).

## 시크릿 rotation

```bash
# 1. 새 값으로 DB·API 키 rotate (외부 시스템)
# 2. .env.enc 편집
sops .env.enc
#    → 새 값 저장
# 3. 기기별 환경 반영 (LaunchAgent 재기동 등)
# 4. 커밋
git add .env.enc
git commit -m "chore: rotate <service> credential"
```

## 실행 래퍼 패턴 (LaunchAgent / cron)

`sops exec-env`는 dotenv 입력을 지원하지 않는다. `eval` 방식 사용:

```bash
#!/bin/bash
set -euo pipefail
cd /path/to/repo
export PATH="/opt/homebrew/bin:$PATH"

set -a
eval "$(sops -d --input-type dotenv --output-type dotenv .env.enc)"
set +a

exec <실제 프로세스>
```

LaunchAgent plist에서 이 래퍼를 `ProgramArguments`로 호출. plist에 평문 시크릿을 기재하지 않는다.

## 키 분실 복구

| 상황 | 복구 방법 |
|------|----------|
| 1개 기기 개인키 분실, 다른 기기는 정상 | 정상 기기에서 신규 기기 공개키 등록 + 재암호화 (위 "기기 추가" 절차) |
| 모든 기기 개인키 분실, 백업 없음 | **복구 불가**. 외부 시스템 비밀번호·토큰 전면 rotation + 신규 키로 처음부터 재구성 |
| 백업 있음 | 백업 파일을 `~/.config/sops/age/keys.txt`에 복원 후 `chmod 600` |

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `error loading config: no matching creation rules found` | `.sops.yaml`의 `path_regex`가 암호화 대상 파일명과 안 맞음 | regex `(^|/)\.env(\.enc)?$` 사용 |
| `Failed to get the data key` | sops가 개인키 파일을 못 찾음 | macOS 기본 경로 `~/Library/Application Support/sops/age/keys.txt`에도 복사 |
| `Error unmarshalling input json: invalid character '#'` | `sops exec-env`가 dotenv를 JSON으로 파싱 시도 | `eval "$(sops -d ...)"` 방식으로 전환 |
| `updatekeys` 실패 | dotenv 포맷 미지원 | 재암호화 절차 사용 (위 "기기 추가" 참조) |
