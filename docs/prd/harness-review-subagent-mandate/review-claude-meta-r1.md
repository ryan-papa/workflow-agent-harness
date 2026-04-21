# 메타 변경 리뷰 결과 (서브에이전트)

**판정**: 1차 미달 (high 2, medium 2) → **반영 완료 후 재확인 예정**

## 반영 내역

| 지적 | 심각도 | 반영 |
|------|:------:|------|
| Codex 실행 주체 모호 (서브 vs 메인) | high | 3개 스킬 + CLAUDE.md에 "서브에이전트=Claude 채점만, Codex 실행=메인 에이전트" 역할 경계 명시 |
| 서브에이전트 실패 fallback 부재 | high | 기술 실패 vs 평가 미달 구분. 기술 실패 최대 2회 재호출 → 지속 실패 시 사용자 보고 + 셀프 채점 우회 금지 |
| "또는 지정 리뷰어" 모호 | medium | 3개 스킬 모두 `subagent_type=general-purpose` 단일 기준으로 정리 |
| 검증 체크 실측성 부족 | medium | 각 스킬에 `review-claude-{plan,eng,code}.md` 저장 단계 추가, PRD 검증 체크리스트에도 포함 |

## 추가 반영 (PRD 검증 체크리스트 보강)

- [ ] 리뷰 산출물 `review-claude-{plan,eng,code}.md`가 실제 생성되는지 다음 워크플로에서 확인
- [ ] 다음 `/rp-retro`에 "셀프 채점 재발 여부" 점검 항목 추가

## 후속 검토 (blocker 아님, 로드맵)

- `docs/templates/review-subagent-prompt.md` 공통 템플릿 분리
- settings.json hook으로 Agent 툴 호출 여부 자동 검증
