# DB 연결 가이드

## 서버·계정 정보

> 호스트, 포트, 계정명, 인증서는 **관리자에게 별도 문의**.
> 비밀번호는 `.env` 파일에 저장, `.gitignore`에 반드시 포함.

## SSL 클라이언트 인증서

인증서 없이는 접속 불가. 서버에서 발급받은 인증서 3개 필요.

### 인증서 위치

```
~/.ssl/client-certs/
├── ca-cert.pem        # CA 인증서
├── client-cert.pem    # 클라이언트 인증서
└── client-key.pem     # 클라이언트 키 (chmod 600)
```

> 인증서 발급·설치 방법은 관리자에게 별도 문의.

## CLI 접속

### MySQL

```bash
mysql -h $DB_HOST -u $DB_USER -p \
  --ssl-ca=~/.ssl/client-certs/ca-cert.pem \
  --ssl-cert=~/.ssl/client-certs/client-cert.pem \
  --ssl-key=~/.ssl/client-certs/client-key.pem
```

### PostgreSQL

```bash
psql "host=$DB_HOST user=$DB_USER \
  sslmode=verify-full \
  sslrootcert=$HOME/.ssl/client-certs/ca-cert.pem \
  sslcert=$HOME/.ssl/client-certs/client-cert.pem \
  sslkey=$HOME/.ssl/client-certs/client-key.pem"
```

## 코드 연결 예시

### Node.js — MySQL (mysql2)

```js
const mysql = require('mysql2');
const fs = require('fs');
const path = require('path');

const certDir = path.join(process.env.HOME, '.ssl/client-certs');

const connection = mysql.createConnection({
  host: process.env.DB_HOST,
  port: Number(process.env.DB_PORT),
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  ssl: {
    ca: fs.readFileSync(path.join(certDir, 'ca-cert.pem')),
    cert: fs.readFileSync(path.join(certDir, 'client-cert.pem')),
    key: fs.readFileSync(path.join(certDir, 'client-key.pem')),
  }
});
```

### Node.js — PostgreSQL (pg)

```js
const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

const certDir = path.join(process.env.HOME, '.ssl/client-certs');

const client = new Client({
  host: process.env.DB_HOST,
  port: Number(process.env.DB_PORT),
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  ssl: {
    ca: fs.readFileSync(path.join(certDir, 'ca-cert.pem')),
    cert: fs.readFileSync(path.join(certDir, 'client-cert.pem')),
    key: fs.readFileSync(path.join(certDir, 'client-key.pem')),
  }
});
```

### Python — MySQL (pymysql)

```python
import pymysql
import os

cert_dir = os.path.expanduser('~/.ssl/client-certs')

conn = pymysql.connect(
    host=os.environ['DB_HOST'],
    port=int(os.environ['DB_PORT']),
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    ssl={
        'ca': f'{cert_dir}/ca-cert.pem',
        'cert': f'{cert_dir}/client-cert.pem',
        'key': f'{cert_dir}/client-key.pem',
    }
)
```

### Python — PostgreSQL (psycopg2)

```python
import psycopg2
import os

cert_dir = os.path.expanduser('~/.ssl/client-certs')

conn = psycopg2.connect(
    host=os.environ['DB_HOST'],
    port=int(os.environ['DB_PORT']),
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    sslmode='verify-full',
    sslrootcert=f'{cert_dir}/ca-cert.pem',
    sslcert=f'{cert_dir}/client-cert.pem',
    sslkey=f'{cert_dir}/client-key.pem',
)
```

## 테이블 공통 컬럼 규칙

모든 테이블에 아래 3개 컬럼을 필수 포함한다.

```sql
-- MySQL
id      BIGINT AUTO_INCREMENT PRIMARY KEY,
reg_ts  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
upd_ts  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

-- PostgreSQL
id      BIGSERIAL PRIMARY KEY,
reg_ts  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
upd_ts  TIMESTAMPTZ NOT NULL DEFAULT NOW()  -- 트리거로 자동 갱신
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | BIGINT / BIGSERIAL | Auto Increment PK |
| `reg_ts` | TIMESTAMP | 등록 일시 — DB 자동 삽입 |
| `upd_ts` | TIMESTAMP | 수정 일시 — 로우 변경 시 자동 갱신 |

> PostgreSQL은 `ON UPDATE` 구문이 없으므로 트리거 필요:
> ```sql
> CREATE OR REPLACE FUNCTION update_upd_ts()
> RETURNS TRIGGER AS $$
> BEGIN NEW.upd_ts = NOW(); RETURN NEW; END;
> $$ LANGUAGE plpgsql;
>
> -- 각 테이블에 적용
> CREATE TRIGGER trg_upd_ts BEFORE UPDATE ON {table}
> FOR EACH ROW EXECUTE FUNCTION update_upd_ts();
> ```

## 하네스 DB 절대 규칙 (예외 없음)

`DROP`·`DELETE FROM`·`TRUNCATE` 실행 금지, `DROP COLUMN` 관리자 승인 필수 → SSOT [`docs/harness-absolute-rules.md`](docs/harness-absolute-rules.md) §DB 파괴적 작업 금지

## 주의사항

- 비밀번호는 `.env` 파일에 저장, `.gitignore`에 반드시 포함
- 인증서 파일은 커밋 금지
- `client-key.pem` 권한은 반드시 `600`
- macOS에서 mysql CLI: `brew install mysql-client` 필요
