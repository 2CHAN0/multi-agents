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
    conversion_details: list[dict],
    currency_info: dict | None = None
) -> str:
    """
    집계 데이터를 마크다운 리포트로 생성합니다.
    
    Args:
        aggregated_data: 표준 코드별 집계 데이터
        conversion_details: 변환 상세 내역
        currency_info: (선택사항) 환율 정보 {'base_currency': 'USD', 'target_currency': 'KRW', 'rate': 1400}
        
    Returns:
        마크다운 형식의 리포트
    """
    lines = [
        "# 📊 표준 코드 집계 리포트",
        "",
    ]
    
    # 환율 정보가 있으면 상단에 표시
    if currency_info and currency_info.get("success", True):
        base = currency_info.get("base_currency", "USD")
        target = currency_info.get("target_currency", "KRW")
        rate = currency_info.get("rate", 0)
        lines.extend([
            "## 💱 환율 정보",
            f"- 기준: 1 {base} = {rate:,.2f} {target}",
            "",
        ])

    lines.extend([
        "## 집계 결과",
        "",
        "| 표준 코드 | 총 수량 |",
        "|-----------|---------| ",
    ])
    
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
            f"| {detail.get('external_code', 'N/A')} | "
            f"{detail.get('standard_code', 'N/A')} | "
            f"{detail.get('category', 'N/A')} |"
        )
    
    return "\n".join(lines)
