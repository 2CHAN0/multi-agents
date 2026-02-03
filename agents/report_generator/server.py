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
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableLambda
from langserve import add_routes
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.types import Command

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
from agents.report_generator.tools.finance import get_exchange_rate
from agents.report_generator.tools.memory import save_user_preference

from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

# 전역 MCP 클라이언트
mcp_client = None

# HITL 및 Long-term Memory를 위한 전역 저장소
checkpointer = MemorySaver()
store = InMemoryStore()

class ResumeInput(BaseModel):
    thread_id: str
    decision: str  # approve, reject, edit
    edited_args: dict | None = None


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


async def process_report_request(input_data: ReportInput) -> dict:
    """리포트 생성 요청 처리 (DeepAgent 사용)"""
    
    global mcp_client

    # MCP 도구 가져오기 (비동기 그대로 사용)
    mcp_tools = await mcp_client.get_tools()
    
    # 로컬 도구와 MCP 도구 결합
    all_tools = [
        aggregate_by_standard_code,
        generate_markdown_report,
        get_exchange_rate,
        save_user_preference
    ] + mcp_tools
    
    # DeepAgent 생성 (DeepAgents 표준 패턴)
    agent = create_deep_agent(
        model=model,
        tools=all_tools,
        system_prompt=system_prompt,  # WHO
        memory=[agents_md_path],      # WHEN + WHICH (MemoryMiddleware가 로드)
        skills=skills_paths,           # HOW (SkillsMiddleware가 로드)
        backend=backend,
        checkpointer=checkpointer,     # Required for HITL
        interrupt_on={"get_exchange_rate": True}  # 환율 조회 시 인터럽트
    )
    
    # 사용자 메시지 구성
    user_message = f"""다음 데이터를 처리하여 리포트를 생성해주세요:

외부 코드 목록: {input_data.external_codes}
수량 목록: {input_data.quantities}
"""

    if input_data.instruction:
        user_message += f"\n추가 지침: {input_data.instruction}\n"

    user_message += """
1. 먼저 batch_convert_codes 도구로 외부 코드를 변환하세요.
2. 그 다음 aggregate_by_standard_code로 수량을 집계하세요.
3. 마지막으로 generate_markdown_report로 리포트를 생성하세요."""
    
    # DeepAgent 실행 (thread_id 포함)
    import uuid
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"🔄 리포트 요청 처리 시작 (Thread ID: {thread_id})")
    
    print("🤖 에이전트 실행 시작...")
    try:
        # 비동기 실행 (ainvoke 사용)
        result = await agent.ainvoke(
            {
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            },
            config=config
        )
    except Exception as e:
        print(f"❌ 에이전트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise e
        
    print("✅ 에이전트 실행 완료")
    
    # 인터럽트 처리
    if result.get("__interrupt__"):
        print("⏸️ 인터럽트 감지됨")
        return {
            "status": "interrupted",
            "thread_id": thread_id,
            "interrupts": result["__interrupt__"][0].value,
            "messages": [m.content for m in result["messages"]]
        }
    
    print("🎉 최종 결과 반환")
    # 결과에서 최종 응답 추출
    final_message = result["messages"][-1].content
    
    return {
        "status": "completed",
        "thread_id": thread_id,
        "report": final_message,
        "summary": {
            "input_codes": input_data.external_codes,
            "input_quantities": input_data.quantities,
            "total_items": len(input_data.external_codes),
        }
    }


# ============================================================================
# FastAPI 앱 설정
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 컨텍스트 매니저"""
    print("🚀 Report Generator Agent Server (DeepAgents) 시작...")
    print(" AGENTS.md: 비즈니스 규칙 로드됨")
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
    version="3.2.0",
    lifespan=lifespan,
)

# UI 정적 파일 제공
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/ui", StaticFiles(directory=str(static_dir), html=True), name="ui")

@app.post("/report/resume")
async def resume_report(input_data: ResumeInput):
    """중단된 리포트 생성 재개"""
    global mcp_client
    
    # 도구 및 에이전트 재구성 (동일한 설정 필요)
    mcp_tools = await mcp_client.get_tools()
    all_tools = [
        aggregate_by_standard_code,
        generate_markdown_report,
        get_exchange_rate,
        save_user_preference
    ] + mcp_tools
    
    # 인터럽트 설정
    interrupt_on = {"get_exchange_rate": True}
    
    # 수정(edit) 결정인 경우, 해당 도구의 인터럽트를 비활성화하여 무한 루프 방지
    if input_data.decision == "edit":
        # 현재 코드에서는 get_exchange_rate만 인터럽트 대상이므로 이를 수정 중이라면 제외
        if "get_exchange_rate" in interrupt_on:
             del interrupt_on["get_exchange_rate"]

    agent = create_deep_agent(
        model=model,
        tools=all_tools,
        system_prompt=system_prompt,
        memory=[agents_md_path],
        skills=skills_paths,
        backend=backend,
        checkpointer=checkpointer,
        interrupt_on=interrupt_on
    )
    
    config = {"configurable": {"thread_id": input_data.thread_id}}
    
    # 결정 구성
    decisions = []
    if input_data.decision == "approve":
        decisions = [{"type": "approve"}]  # 기본 파라미터로 실행
    elif input_data.decision == "reject":
        decisions = [{"type": "reject"}]  # 도구 호출 건너뛰기
    elif input_data.decision == "edit":
        # 파라미터 수정 (예: 다른 화폐로 변경)
        decisions = [{
            "type": "edit",
            "edited_action": {
                "name": "get_exchange_rate",
                "args": input_data.edited_args
            }
        }]
    
    
    # 재개 (ainvoke 사용)
    try:
        result = await agent.ainvoke(
            Command(resume={"decisions": decisions}),
            config=config
        )
    except Exception as e:
        return {"error": str(e)}
    
    # 결과 처리
    if result.get("__interrupt__"):
        return {
            "status": "interrupted",
            "thread_id": input_data.thread_id,
            "interrupts": result["__interrupt__"][0].value,
            "messages": [m.content for m in result["messages"]]
        }

    final_message = result["messages"][-1].content
    
    return {
        "status": "completed",
        "thread_id": input_data.thread_id,
        "report": final_message
    }


# 체인 래퍼 (LangServe 호환 - 단순화)
async def _process_input(input_data: dict) -> dict:
    """입력 처리 래퍼"""
    # LangServe 요청은 새로운 thread_id 생성 또는 전달된 ID 사용
    if "instruction" not in input_data:
        input_data["instruction"] = None
        
    report_input = ReportInput(**input_data)
    
    # process_report_request modified to return dict
    result = await process_report_request(report_input)
    return result

# LangServe 라우트 추가
add_routes(
    app,
    RunnableLambda(_process_input),
    path="/report",
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
