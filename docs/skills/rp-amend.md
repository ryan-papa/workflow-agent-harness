---
description: 기존 프로젝트에 기능 수정·추가. rp-init 스킵, rp-specify부터 rp-retro까지 전 단계 실행
argument-hint: '[프로젝트명] [기능 수정·추가 설명]'
---

# rp-amend

**기존 프로젝트**에 기능 **수정·추가**를 위한 진입 스킬.
신규 프로젝트 초기화(`rp-init`)는 스킵, 이후 전 단계는 기존 `rp-workflow`와 동일.

## 트리거

- 기존 `repositories/[project]/`에 기능 수정·추가 요청
- `/rp-amend` 명령
- 사용자가 "수정", "추가", "고쳐", "바꿔" 등 기존 기능 변경 의도 표현

## 적용 대상

| 적용 | 비적용 |
|------|-------|
| 기능 수정 (동작 변경) | 신규 프로젝트 생성 (→ `rp-workflow`) |
| 기능 추가 (기존 도메인 내) | 하네스 메타 변경 (→ `rp-workflow` 메타 단축 경로) |
| 기능 삭제 | 핫픽스·단일 버그 픽스 (→ Lite 트랙) |

## 플로우

| 순서 | 스킬 | 비고 |
|:---:|------|------|
| 1 | — | `rp-init` **스킵** (프로젝트 이미 존재) |
| 2 | `/rp-specify` | **기능 단위**로 5단계 질문 전체 실행 |
| 3 | `/rp-prd` | **Full PRD** (간소 PRD 아님) |
| 4 | `/rp-plan-review` | Claude + Codex 1회 |
| 5 | `/rp-eng-review` | Claude + Codex 1회 |
| 6 | `/rp-task` | 기능 변경분만 태스크 분해 |
| 7 | `/rp-dev` | feat 브랜치에서 구현 |
| 8 | `/rp-qa` | QA·콘텐츠 검수 |
| 9 | `/rp-code-review` | Claude 7항목 + Codex 1회 |
| 10 | 산출물 보고 | 사용자 승인 |
| 11 | `/rp-ship` | 커밋·PR·머지·배포 |
| 12 | `/rp-retro` | 회고 |

## 절차

1. 진입 시 프로젝트명 확인 (`repositories/[project]/` 존재 여부 검증)
2. 존재하지 않으면 `/rp-workflow`로 리다이렉트 안내
3. 존재하면 `/rp-specify`부터 순차 실행
4. 이후 단계는 각 스킬 파일 절차를 따름

## 자동 전환

각 단계 완료 시 다음 스킬로 자동 진입. 배포 `[11]`에서만 사용자 승인 대기.

## ⛔ 절대 규칙

- `rp-init` 스킵해도 **기능 단위 `rp-specify`는 생략 불가**
- 간소 PRD 아님 — Full PRD 필수
- QA·코드리뷰·회고 **생략 불가** (워크플로우와 동일)
- `main` 직접 수정 금지, feat 브랜치 필수
- `rp-ship` 스킬 경유 필수

→ 전체 플로우: [`../harness-workflow.md`](../harness-workflow.md)
→ 오케스트레이터: [`rp-workflow.md`](rp-workflow.md)
