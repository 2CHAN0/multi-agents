"""
Code Converter Tools
====================
외부 코드를 내부 표준 코드로 변환하는 도구 모음
"""

import re
from typing import Any


# 외부 코드 패턴별 매핑 규칙
CODE_MAPPING_RULES = {
    "EXT-PROD": {"prefix": "STD", "category": "A"},  # 외부 제품
    "EXT-SVC": {"prefix": "STD", "category": "B"},   # 외부 서비스
    "EXT-MAT": {"prefix": "STD", "category": "C"},   # 외부 자재
    "VENDOR": {"prefix": "STD", "category": "V"},    # 벤더 코드
    "PARTNER": {"prefix": "STD", "category": "P"},   # 파트너 코드
}


def _extract_code_number(external_code: str) -> str:
    """외부 코드에서 숫자 부분 추출"""
    match = re.search(r'(\d+)', external_code)
    return match.group(1) if match else "000"


def _convert_single_code(external_code: str) -> dict[str, Any]:
    """
    단일 외부 코드를 표준 코드로 변환 (내부 로직)
    
    Args:
        external_code: 외부 시스템의 코드 (예: EXT-PROD-001)
        
    Returns:
        변환 결과 딕셔너리
    """
    external_code = external_code.strip().upper()
    
    # 매핑 규칙 찾기
    for pattern, rule in CODE_MAPPING_RULES.items():
        if external_code.startswith(pattern):
            code_num = _extract_code_number(external_code)
            standard_code = f"{rule['prefix']}-{code_num.zfill(3)}-{rule['category']}"
            return {
                "external_code": external_code,
                "standard_code": standard_code,
                "category": rule["category"],
                "success": True,
                "message": f"코드가 성공적으로 변환되었습니다."
            }
    
    # 알 수 없는 패턴인 경우 기본 변환
    code_num = _extract_code_number(external_code)
    standard_code = f"STD-{code_num.zfill(3)}-X"
    return {
        "external_code": external_code,
        "standard_code": standard_code,
        "category": "X",
        "success": True,
        "message": "알 수 없는 패턴입니다. 기본 카테고리(X)로 변환되었습니다."
    }


def lookup_standard_code(external_code: str) -> dict[str, Any]:
    """
    외부 코드에 대한 매핑 규칙을 찾아 표준 코드를 반환합니다.
    에이전트가 사용하는 도구입니다.
    
    Args:
        external_code: 외부 시스템의 코드
        
    Returns:
        변환 결과 딕셔너리
    """
    return _convert_single_code(external_code)


def get_supported_patterns() -> dict[str, str]:
    """
    지원되는 외부 코드 패턴 목록을 반환합니다.
    
    Returns:
        패턴별 설명 딕셔너리
    """
    return {
        "EXT-PROD-XXX": "외부 제품 코드 → STD-XXX-A",
        "EXT-SVC-XXX": "외부 서비스 코드 → STD-XXX-B",
        "EXT-MAT-XXX": "외부 자재 코드 → STD-XXX-C",
        "VENDOR-XXX": "벤더 코드 → STD-XXX-V",
        "PARTNER-XXX": "파트너 코드 → STD-XXX-P",
    }
