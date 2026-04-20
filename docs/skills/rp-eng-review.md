# rp-eng-review

엔지니어링 리뷰. PRD의 기술적 실현 가능성, 아키텍처 적합성을 검증한다.

## 트리거

- 기획 리뷰 통과 후
- `/rp-eng-review` 명령

## 절차

1. Claude 엔지 리뷰 서브에이전트가 PRD를 엔지니어링 관점에서 검토
2. 평가 항목별 10점 만점 채점
3. 기술적 리스크, 대안 제시
4. 평균 >= 8.0 + 각 항목 >= 7 → Claude 통과, 미달 → PRD 수정 후 재검토 (최대 3회)
5. **Claude 통과 후 Codex 추가 리뷰 (1회)**:
   - **해당 PRD가 있는 프로젝트 루트 cwd**에서 `/codex:review --wait` 실행 (하위 기능은 `repositories/[project]/`, 하네스 메타 변경은 `claude-projects/`)
   - stdout을 `<project-root>/docs/prd/[feature]/review-codex-eng.md`에 저장
   - High / Critical 지적만 PRD에 반영, 반영 내역을 같은 파일 `## 반영` 섹션에 기록
6. 반영 완료 후 다음 단계 진입

## 평가 항목

| 항목 | 설명 |
|------|------|
| 아키텍처 | 기술 스택, 구조 적합성 |
| 확장성 | 트래픽/데이터 증가 대응 |
| 보안 | 인증, 데이터 보호, 취약점 |
| 성능 | 응답 시간, 리소스 효율 |
| 운영성 | 배포, 모니터링, 장애 대응 |

## 판정

- 평균 >= 8.0 + 각 항목 >= 7 → 통과
- 평균 미달 또는 항목별 최저 < 7 → Doc Agent 재작성 (최대 3회)
- 3회 실패 → 사용자에게 보고

## ▶ 자동 전환

Claude 통과 + Codex High/Critical 반영 완료 시 `✓ [5] 엔지니어링 리뷰 통과 (Claude+Codex)` 출력 후 **`/rp-task` 자동 진입**.

→ PRD 상세: [`../harness-prd.md`](../harness-prd.md)
→ Codex 리뷰 규칙: [`../harness-codex-review.md`](../harness-codex-review.md)
