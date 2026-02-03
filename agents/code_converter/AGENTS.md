# Code Converter - Business Rules

## WHEN + WHICH: Skills 조합 규칙

이 문서는 코드 변환 작업 시 어떤 상황에서 어떤 Skills를 사용할지 정의합니다.

---

## 단일 코드 변환 요청

**상황**: 사용자가 하나의 외부 코드 변환을 요청

**Skills 조합**:
1. `code-mapping` 스킬 참조
2. `lookup_standard_code` 도구 사용
3. JSON 형식으로 결과 반환

**예시**:
```
사용자: "EXT-PROD-001을 변환해줘"
→ code-mapping 규칙 확인
→ lookup_standard_code("EXT-PROD-001") 실행
→ {"external_code": "EXT-PROD-001", "standard_code": "STD-001-A", ...} 반환
```

---

## 배치 코드 변환 요청

**상황**: 사용자가 여러 외부 코드의 일괄 변환을 요청

**Skills 조합**:
1. `code-mapping` 스킬 참조
2. 각 코드에 대해 `lookup_standard_code` 도구 사용
3. JSON 배열 형식으로 결과 반환

**예시**:
```
사용자: "EXT-PROD-001, VENDOR-100을 변환해줘"
→ code-mapping 규칙 확인
→ 각 코드에 대해 lookup_standard_code 실행
→ [{"external_code": "EXT-PROD-001", ...}, {"external_code": "VENDOR-100", ...}] 반환
```

---

## 알 수 없는 패턴 처리

**상황**: 매핑 규칙에 없는 새로운 패턴의 코드 발견

**Skills 조합**:
1. `code-mapping` 스킬의 기본 변환 규칙 적용
2. 카테고리 X로 변환
3. `/memories/new_patterns.md`에 패턴 기록

**예시**:
```
사용자: "UNKNOWN-999를 변환해줘"
→ code-mapping의 기본 규칙 적용
→ {"external_code": "UNKNOWN-999", "standard_code": "STD-999-X", "category": "X"} 반환
→ /memories/new_patterns.md에 "UNKNOWN-999" 패턴 기록
```

---

## Long-term Memory 사용

**상황**: 변환 패턴 학습 및 캐싱

**Memory 경로**:
- `/memories/new_patterns.md`: 새로 발견된 패턴 기록
- `/memories/cache.json`: 자주 사용되는 변환 결과 캐싱
- `/memories/patterns.md`: 업데이트된 변환 규칙

**사용 시점**:
- 새 패턴 발견 시 즉시 기록
- 동일 코드 재변환 시 캐시 확인
- 규칙 업데이트 시 patterns.md 갱신
