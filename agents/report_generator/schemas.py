"""
Report Generator Input/Output Schemas
=======================================
리포트 생성 요청 및 응답 스키마
"""

from typing import Any
from pydantic import BaseModel, Field


class ReportInput(BaseModel):
    """리포트 생성 요청 입력"""

    external_codes: list[str] = Field(
        description="외부 코드 목록 (예: ['EXT-PROD-001', 'VENDOR-123'])"
    )
    quantities: list[int] = Field(
        description="각 코드에 해당하는 수량 목록"
    )


class ReportOutput(BaseModel):
    """리포트 생성 결과"""

    report: str = Field(description="마크다운 형식의 집계 리포트")
    summary: dict[str, Any] = Field(description="집계 요약 데이터")
