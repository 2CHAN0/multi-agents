"""
Markdown Report Generator
==========================
집계 데이터를 마크다운 리포트로 생성하는 도구
"""

from typing import Any
from langchain.tools import tool


@tool
def generate_markdown_report(
    aggregated_data: dict[str, int],
    conversion_details: list[dict]
) -> str:
    """
    집계 데이터를 마크다운 리포트로 생성합니다.
    
    Args:
        aggregated_data: 표준 코드별 집계 데이터
        conversion_details: 변환 상세 내역
        
    Returns:
        마크다운 형식의 리포트
    """
    lines = [
        "# 📊 표준 코드 집계 리포트",
        "",
        "## 집계 결과",
        "",
        "| 표준 코드 | 총 수량 |",
        "|-----------|---------| ",
    ]
    
    total_qty = 0
    for code, qty in sorted(aggregated_data.items()):
        lines.append(f"| {code} | {qty} |")
        total_qty += qty
    
    lines.extend([
        "",
        f"**총 항목 수**: {len(aggregated_data)}개",
        f"**총 수량**: {total_qty}",
        "",
        "## 변환 내역",
        "",
        "| 외부 코드 | 표준 코드 | 카테고리 |",
        "|-----------|-----------|----------|",
    ])
    
    for detail in conversion_details:
        lines.append(
            f"| {detail['external_code']} | "
            f"{detail['standard_code']} | "
            f"{detail['category']} |"
        )
    
    return "\n".join(lines)
