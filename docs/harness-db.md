# Harness · DB 스타일 가이드

모든 DDL(신규 테이블·ALTER·마이그레이션)은 아래 규칙을 **강제**한다. 구조 검증 테스트가 규칙 준수를 확인할 수 있어야 한다.

## 1. 네이밍

| 대상 | 규칙 | 예시 |
|------|------|------|
| 테이블 | 복수형 snake_case | `users`, `refresh_tokens` |
| 컬럼 | snake_case | `email_hmac`, `created_at` |
| PK | 단일 `id` BIGINT AUTO_INCREMENT (예외: 단일 세션·키 기반 테이블) | — |
| FK | `fk_<자식>_<부모>` | `fk_refresh_user` |
| UNIQUE | `uk_<의미>` | `uk_email_hmac` |
| INDEX | `idx_<컬럼|의미>` | `idx_created_at`, `idx_board_post` |
| VIEW | `<base>_view` 접미사 필수 | `museum_parking_view`, `user_active_view` |
| ENUM 값 | snake_case 소문자 | `login_ok`, `refresh_reuse_detected` |

## 2. COMMENT 규칙 (예외 없음)

### 2.1 테이블 COMMENT 필수

```sql
CREATE TABLE users (
    ...
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='사용자 계정. 이메일·이름은 AES-GCM 암호문, 비번은 argon2id 해시.';
```

- 한 줄, 60자 이내 권장
- "왜 존재하는가 / 무엇을 담는가"가 드러나야 함

### 2.2 컬럼 COMMENT 필수

```sql
email_hmac  VARBINARY(32)  NOT NULL COMMENT 'HMAC-SHA256(email, AUTH_HMAC_KEY) · 이메일 룩업/유일성 인덱스',
issued_at   DATETIME       NOT NULL COMMENT 'JWT iat. UTC.',
amount      INT            NOT NULL COMMENT '결제 금액 (KRW, 부가세 포함)',
```

- 단위·포맷·의미를 명시(원/초/UTC/암호문 등)
- 암호문·해시 컬럼은 **어떤 키·알고리즘**인지 명시
- NULL 허용 이유가 있으면 COMMENT 에 기재

### 2.3 인덱스·제약 COMMENT 필수

MySQL 5.6+ 은 `INDEX ... COMMENT '...'` 를 지원한다.

```sql
UNIQUE KEY uk_email_hmac (email_hmac) COMMENT '이메일 중복 가입 방지',
INDEX     idx_locked_until (locked_until) COMMENT 'lockout 만료 배치 조회용',
INDEX     idx_window_end (window_end) COMMENT 'rate limit 만료 버킷 purge cron',
```

- 용도(쿼리 패턴·배치명)를 적어 향후 삭제 판단 가능하게

### 2.4 ENUM COMMENT 규칙

MySQL 은 ENUM 항목별 COMMENT 를 지원하지 않으므로 **컬럼 COMMENT 에 항목별 의미를 집약**한다.

```sql
event_type ENUM(
    'signup', 'login_ok', 'login_fail', 'totp_ok', 'totp_fail',
    'refresh_rotated', 'refresh_reuse_detected', 'logout', 'locked'
) NOT NULL COMMENT '인증 이벤트. '
    'signup=가입 완료 / '
    'login_ok=로그인 성공 / '
    'login_fail=비번·이메일 불일치 / '
    'totp_ok=2FA 통과 / '
    'totp_fail=2FA 코드 불일치 / '
    'refresh_rotated=refresh 정상 회전 / '
    'refresh_reuse_detected=폐기된 refresh 재사용(탈취 의심) / '
    'logout=사용자 로그아웃 / '
    'locked=계정 lockout 진입',
```

- ENUM 추가·삭제 시 반드시 COMMENT 동시 갱신
- 구조 테스트가 "ENUM 항목 개수 == COMMENT 내 항목 개수" 검증(권장)

## 3. 마이그레이션 파일 규칙

| 규칙 | 내용 |
|------|------|
| 파일명 | `YYYYMMDD_<설명>.sql` (단방향) |
| 위치 | `db/migrations/` |
| 롤백 | `YYYYMMDD_<설명>.down.sql` 같이 두거나 주석으로 역연산 명시 |
| 검증 | 파일당 구조 테스트 1개 이상 (`db/tests/test_<name>_schema.py`) |
| COMMENT ALTER | 기존 테이블에 COMMENT 만 추가하는 경우 별도 `_comments.sql` 마이그레이션 분리 |

## 4. 테스트 (구조 검증)

`db/tests/` 에 pytest 파일. 실제 DB 연결 없이 정규식·AST 로 DDL 파일 내용을 검증.

최소 체크:

- [ ] 각 `CREATE TABLE` 에 `COMMENT='...'` 존재
- [ ] 각 컬럼 라인에 `COMMENT '...'` 존재(PK 제외 가능)
- [ ] 각 `INDEX`·`UNIQUE KEY` 에 `COMMENT '...'` 존재
- [ ] ENUM 컬럼 COMMENT 에 모든 항목 언급

예시: `db/tests/test_auth_schema.py` 참고.

## 5. 재검토 트리거

- 새 테이블 추가·컬럼 추가·ENUM 값 변경
- 인덱스 추가·삭제
- 위 중 하나라도 COMMENT 미기재 시 CI 실패 처리(향후 규칙)

→ 워크플로우: [`harness-workflow.md`](harness-workflow.md)
