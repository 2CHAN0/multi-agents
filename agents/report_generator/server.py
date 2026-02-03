"""
Report Generator Agent Server
==============================
DeepAgents 프레임워크 기반: 외부 코드를 표준 코드로 변환하고 집계 리포트를 생성

Usage:
    python -m agents.report_generator.server
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableLambda
from langserve import add_routes
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_mcp_adapters.client import MultiServerMCPClient

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.report_generator.config import (
    get_model_config,
    get_system_prompt,
    get_agents_md_path,
    get_skills_paths,
    get_mcp_server_config
)
from agents.report_generator.schemas import ReportInput, ReportOutput
from agents.report_generator.tools.aggregate import aggregate_by_standard_code
from agents.report_generator.tools.markdown import generate_markdown_report

# 전역 MCP 클라이언트
mcp_client = None

# ============================================================================
# DeepAgent 설정 (리포트 생성 전문가)
# ============================================================================

# 모델 설정 로드
model_config = get_model_config()
model = init_chat_model(**model_config)

# System Prompt (WHO - 정체성과 절대 규칙)
system_prompt = get_system_prompt()

# AGENTS.md 경로 (WHEN + WHICH - 비즈니스 규칙)
agents_md_path = get_agents_md_path()

# Skills 경로 (HOW - 재사용 가능한 지침)
skills_paths = get_skills_paths()

# Backend 설정 (FilesystemBackend)
agent_dir = Path(__file__).parent
backend = FilesystemBackend(root_dir=agent_dir)


async def process_report_request(input_data: ReportInput) -> ReportOutput:
    """리포트 생성 요청 처리 (DeepAgent 사용)"""
    
    global mcp_client

    # MCP 도구 가져오기
    mcp_tools = await mcp_client.get_tools()
    
    # 로컬 도구와 MCP 도구 결합
    all_tools = [
        aggregate_by_standard_code,
        generate_markdown_report
    ] + mcp_tools
    
    # DeepAgent 생성 (DeepAgents 표준 패턴)
    agent = create_deep_agent(
        model=model,
        tools=all_tools,
        system_prompt=system_prompt,  # WHO
        memory=[agents_md_path],      # WHEN + WHICH (MemoryMiddleware가 로드)
        skills=skills_paths,           # HOW (SkillsMiddleware가 로드)
        backend=backend,
    )
    
    # 사용자 메시지 구성
    user_message = f"""다음 데이터를 처리하여 리포트를 생성해주세요:

외부 코드 목록: {input_data.external_codes}
수량 목록: {input_data.quantities}

1. 먼저 batch_convert_codes 도구로 외부 코드를 변환하세요.
2. 그 다음 aggregate_by_standard_code로 수량을 집계하세요.
3. 마지막으로 generate_markdown_report로 리포트를 생성하세요."""
    
    # DeepAgent 실행 (비동기)
    result = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": user_message}
        ]
    })
    
    # 결과에서 최종 응답 추출
    final_message = result["messages"][-1].content
    
    return ReportOutput(
        report=final_message,
        summary={
            "input_codes": input_data.external_codes,
            "input_quantities": input_data.quantities,
            "total_items": len(input_data.external_codes),
        }
    )


# ============================================================================
# FastAPI 앱 설정
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 컨텍스트 매니저"""
    print("🚀 Report Generator Agent Server (DeepAgents) 시작...")
    print("� AGENTS.md: 비즈니스 규칙 로드됨")
    print("🎯 Skills: 재사용 가능한 지침 로드됨")
    
    global mcp_client
    mcp_server_config = get_mcp_server_config()
    print(f"📋 MCP 서버 설정: {list(mcp_server_config.keys())}")
    
    mcp_client = MultiServerMCPClient(mcp_server_config)

    yield
    
    print("👋 서버 종료")
    # MCP Client Cleanup
    if mcp_client:
        try:
            await mcp_client.__aexit__(None, None, None)
        except Exception:
            pass


app = FastAPI(
    title="Report Generator Agent (DeepAgents)",
    description="DeepAgents 프레임워크 기반: 외부 코드를 표준 코드로 변환하고 집계 리포트를 생성",
    version="3.0.0",
    lifespan=lifespan,
)


# 체인 래퍼 (LangServe 호환)
async def _process_input(input_data: dict) -> dict:
    """입력 처리 래퍼"""
    report_input = ReportInput(**input_data)
    result = await process_report_request(report_input)
    return result.model_dump()

report_chain = RunnableLambda(_process_input)

# LangServe 라우트 추가
add_routes(
    app,
    report_chain,
    path="/report",
    input_type=ReportInput,
    output_type=ReportOutput,
)


@app.get("/")
async def root():
    """API 정보"""
    return {
        "name": "Report Generator Agent (DeepAgents)",
        "framework": "LangChain DeepAgents",
        "version": "3.0.0",
        "structure": {
            "system_prompt": "WHO - 정체성과 절대 규칙",
            "agents_md": "WHEN + WHICH - 비즈니스 규칙",
            "skills": "HOW - 재사용 가능한 지침",
        },
        "endpoints": {
            "/report/invoke": "POST - 리포트 생성",
            "/report/stream": "POST - 스트리밍 리포트 생성",
            "/report/playground": "GET - 인터랙티브 플레이그라운드",
            "/docs": "GET - API 문서",
        }
    }


# ============================================================================
# 서버 실행
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "agents.report_generator.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
