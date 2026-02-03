# Report Generator - Business Rules

## WHEN + WHICH: Skills 조합 규칙

이 문서는 리포트 생성 작업 시 어떤 상황에서 어떤 Skills를 사용할지 정의합니다.

---

## 표준 리포트 생성 요청

**상황**: 사용자가 외부 코드 목록과 수량으로 리포트 생성 요청

**Skills 조합**:
1. MCP 서버의 `batch_convert_codes` 도구로 코드 변환
2. `reporting` 스킬의 집계 프로세스 참조
3. `aggregate_by_standard_code` 도구로 수량 집계
4. `reporting` 스킬의 리포트 형식 참조
5. `generate_markdown_report` 도구로 최종 리포트 생성

**예시**:
```
사용자: "EXT-PROD-001 10개, VENDOR-100 5개로 리포트 생성해줘"
→ batch_convert_codes(["EXT-PROD-001", "VENDOR-100"]) 실행
→ reporting 스킬의 집계 방법 참조
→ aggregate_by_standard_code(변환결과, [10, 5]) 실행
→ reporting 스킬의 리포트 형식 참조
→ generate_markdown_report(집계결과, 변환상세) 실행
```

---

## 사용자 정의 형식 리포트

**상황**: 사용자가 특정 형식의 리포트를 요청

**Skills 조합**:
1. `/memories/user_preferences.md` 확인
2. 선호도가 없으면 사용자 요청 저장
3. `reporting` 스킬의 커스터마이징 방법 참조
4. 요청된 형식으로 리포트 생성

**예시**:
```
사용자: "리포트는 항상 표 형식으로 생성해줘"
→ /memories/user_preferences.md에 저장
→ reporting 스킬의 표 형식 생성 방법 참조
→ 표 형식으로 리포트 생성
```

---

## 과거 리포트 참조

**상황**: 사용자가 이전 리포트와 비교 요청

**Skills 조합**:
1. `/memories/history/` 디렉토리에서 과거 리포트 조회
2. `reporting` 스킬의 비교 분석 방법 참조
3. 현재 데이터와 과거 데이터 비교
4. 차이점을 포함한 리포트 생성

**예시**:
```
사용자: "지난주 리포트와 비교해서 보여줘"
→ /memories/history/ 에서 지난주 리포트 조회
→ reporting 스킬의 비교 방법 참조
→ 증감 분석 포함 리포트 생성
```

---

## 템플릿 기반 리포트

**상황**: 사용자가 저장된 템플릿 사용 요청

**Skills 조합**:
1. `/memories/templates/` 디렉토리에서 템플릿 조회
2. `reporting` 스킬의 템플릿 적용 방법 참조
3. 템플릿에 데이터 매핑
4. 템플릿 형식으로 리포트 생성

**예시**:
```
사용자: "월간 리포트 템플릿으로 생성해줘"
→ /memories/templates/monthly_report.md 조회
→ reporting 스킬의 템플릿 사용법 참조
→ 템플릿에 현재 데이터 적용
```

---

## Long-term Memory 사용

**Memory 경로**:
- `/memories/user_preferences.md`: 사용자 선호 형식
- `/memories/templates/`: 리포트 템플릿
- `/memories/history/`: 과거 리포트 보관
- `/memories/report_input.txt`: 최근 입력 데이터 로그

**사용 시점**:
- 사용자 선호도 요청 시 즉시 저장
- 리포트 생성 완료 시 history에 보관
- 템플릿 요청 시 templates에서 조회
