"""
Report Generator Tools
=======================
데이터 집계 및 마크다운 리포트 생성 도구
"""

from collections import defaultdict
from typing import Any
from langchain.tools import tool


@tool
def aggregate_by_standard_code(
    conversions: list[dict],
    quantities: list[int]
) -> dict[str, int]:
    """
    변환된 표준 코드별로 수량을 집계합니다.
    
    Args:
        conversions: 코드 변환 결과 목록
        quantities: 각 항목의 수량 목록
        
    Returns:
        표준 코드별 총 수량 딕셔너리
    """
    aggregated = defaultdict(int)
    for conv, qty in zip(conversions, quantities):
        std_code = conv.get("standard_code", "UNKNOWN")
        aggregated[std_code] += qty
    return dict(aggregated)
