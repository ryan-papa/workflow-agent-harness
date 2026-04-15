# DB 연결 가이드

## 서버 정보

| 항목 | 값 |
|------|------|
| Host | `eepp.shop` |
| MySQL 포트 | `3306` |
| PostgreSQL 포트 | `5432` |

## 계정 정보

| 용도 | MySQL | PostgreSQL |
|------|-------|------------|
| 관리자 | `root` | `postgres` |
| 읽기/쓰기 | `dev_readwrite` | `dev_readwrite` |
| 읽기전용 | `all_readonly` | `all_readonly` |

> 비밀번호는 담당자에게 별도 문의

## SSL 클라이언트 인증서

인증서 없이는 접속 불가. 서버에서 발급받은 인증서 3개 필요.

### 인증서 위치

```
~/.ssl/client-certs/
├── ca-cert.pem        # CA 인증서
├── client-cert.pem    # 클라이언트 인증서 (CN=hose.kim)
└── client-key.pem     # 클라이언트 키 (chmod 600)
```

### 인증서 설치 (신규 머신)

```bash
mkdir -p ~/.ssl/client-certs
scp hose.kim@eepp.shop:/tmp/client-certs/ca-cert.pem ~/.ssl/client-certs/
scp hose.kim@eepp.shop:/tmp/client-certs/client-cert.pem ~/.ssl/client-certs/
scp hose.kim@eepp.shop:/tmp/client-certs/client-key.pem ~/.ssl/client-certs/
chmod 600 ~/.ssl/client-certs/client-key.pem
```

## CLI 접속

### MySQL

```bash
mysql -h eepp.shop -u dev_readwrite -p \
  --ssl-ca=~/.ssl/client-certs/ca-cert.pem \
  --ssl-cert=~/.ssl/client-certs/client-cert.pem \
  --ssl-key=~/.ssl/client-certs/client-key.pem
```

### PostgreSQL

```bash
psql "host=eepp.shop user=dev_readwrite \
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
  host: 'eepp.shop',
  port: 3306,
  user: 'dev_readwrite',
  password: process.env.MYSQL_PASSWORD,
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
  host: 'eepp.shop',
  port: 5432,
  user: 'dev_readwrite',
  password: process.env.PG_PASSWORD,
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
    host='eepp.shop',
    port=3306,
    user='dev_readwrite',
    password=os.environ['MYSQL_PASSWORD'],
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
    host='eepp.shop',
    port=5432,
    user='dev_readwrite',
    password=os.environ['PG_PASSWORD'],
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

## ⛔ 하네스 DB 절대 규칙 (예외 없음)

| 규칙 | 설명 |
|------|------|
| **DB/스키마/테이블 삭제 금지** | 기존 생성된 DATABASE, SCHEMA, TABLE은 **절대 DROP하지 않는다** |
| **DELETE 실행 금지** | `DELETE FROM` 문은 하네스가 실행하지 않는다 — 관리자가 직접 수행 |
| **TRUNCATE 실행 금지** | `TRUNCATE TABLE` 문은 하네스가 실행하지 않는다 — 관리자가 직접 수행 |
| **DROP 실행 금지** | `DROP DATABASE`, `DROP TABLE`, `DROP INDEX` 등 모든 DROP 문 실행 금지 |
| **ALTER 주의** | 컬럼 삭제(`DROP COLUMN`)는 관리자 승인 필수. 컬럼 추가는 허용 |

> 데이터 삭제가 필요한 경우 관리자에게 요청하고, 관리자가 직접 CLI에서 실행한다.
> "급해서", "테스트 데이터라서" 등 어떤 이유로도 예외 불가.

## 주의사항

- 비밀번호는 `.env` 파일에 저장, `.gitignore`에 반드시 포함
- 인증서 파일은 커밋 금지
- `client-key.pem` 권한은 반드시 `600`
- macOS에서 mysql CLI: `brew install mysql-client` 필요
