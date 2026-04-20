---
description: '[6] 태스크 분해. PRD F-XX 기능 요구사항을 실행 단위 태스크로 분리'
argument-hint: '[PRD 경로]'
---

# rp-task

PRD 기능 요구사항 기반 태스크 분해.

## 트리거

- 엔지니어링 리뷰 통과 후
- `/rp-task` 명령

## 절차

1. PRD의 F-XX 기능 요구사항을 분석
2. 구현 단위로 태스크 분해
3. 태스크 목록 파일 생성: `docs/tasks.md`
4. 의존성 순서 결정

## 태스크 형식

| 항목 | 내용 |
|------|------|
| ID | T-01, T-02... |
| 설명 | 구현 내용 |
| 상태 | Todo / In Progress / Done |
| 브랜치 | `feat/T-01-[description]` |
| 의존성 | 선행 태스크 ID |

## 브랜치 전략

```
main
  └── feat/[project-name]          ← 통합 브랜치
       ├── feat/T-01-description   ← 태스크 브랜치
       └── feat/T-02-description
```

## 완료 조건

- 태스크 목록 파일(`docs/tasks.md`) 생성
- 모든 F-XX가 최소 1개 태스크에 매핑
- 의존성 순서 확정

## ▶ 자동 전환

완료 즉시 `✓ [6] 태스크 분해 완료` 출력 후 **`/rp-dev` 자동 진입**.

→ 개발: [`rp-dev.md`](rp-dev.md)
