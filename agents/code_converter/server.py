"""
Code Converter MCP Server
==========================
외부 코드를 내부 표준 코드로 변환하는 MCP 서버.
DeepAgents 프레임워크 기반의 코드 변환 에이전트를 MCP tool로 노출합니다.

Usage:
    python -m agents.code_converter.server
"""

import sys
from pathlib import Path

from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from mcp.server.fastmcp import FastMCP

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.code_converter.config import (
    get_model_config,
    get_system_prompt,
    get_agents_md_path,
    get_skills_paths
)
from agents.code_converter.tools.lookup_code import (
    lookup_standard_code,
    get_supported_patterns,
    CODE_MAPPING_RULES
)

# ============================================================================
# MCP 서버 설정
# ============================================================================

mcp = FastMCP(
    name="code-converter",
)

# ============================================================================
# DeepAgent 설정 (코드 변환 전문가)
# ============================================================================

def create_converter_agent():
    """코드 변환 DeepAgent 생성 (DeepAgents 표준 구조)"""
    
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
    
    # DeepAgent 생성 (DeepAgents 표준 패턴)
    agent = create_deep_agent(
        model=model,
        tools=[lookup_standard_code],
        system_prompt=system_prompt,  # WHO
        memory=[agents_md_path],      # WHEN + WHICH (MemoryMiddleware가 로드)
        skills=skills_paths,           # HOW (SkillsMiddleware가 로드)
        backend=backend,
    )
    
    return agent

# 전역 에이전트 인스턴스
converter_agent = create_converter_agent()


# ============================================================================
# MCP Tools (Agent Wrapper)
# ============================================================================

@mcp.tool()
def convert_code(external_code: str) -> str:
    """
    [Agent 호출] 외부 코드를 내부 표준 코드로 변환합니다.
    내부적으로 DeepAgent를 실행하여 결과를 생성합니다.
    
    Args:
        external_code: 외부 시스템의 코드 (예: EXT-PROD-001)
        
    Returns:
        JSON 형식의 변환 결과 문자열
    """
    # 에이전트 실행
    result = converter_agent.invoke({
        "messages": [
            {"role": "user", "content": f"코드 '{external_code}'를 변환해줘."}
        ]
    })
    
    return result["messages"][-1].content


@mcp.tool()
def batch_convert_codes(external_codes: list[str]) -> str:
    """
    [Agent 호출] 여러 외부 코드를 한 번에 표준 코드로 변환합니다.
    내부적으로 DeepAgent를 실행하여 결과를 생성합니다.
    
    Args:
        external_codes: 외부 코드 목록
        
    Returns:
        JSON 배열 형식의 변환 결과 문자열
    """
    # 에이전트 실행
    result = converter_agent.invoke({
        "messages": [
            {"role": "user", "content": f"다음 코드 목록을 모두 변환해줘: {external_codes}"}
        ]
    })
    
    return result["messages"][-1].content


@mcp.tool()
def get_supported_patterns_tool() -> dict[str, str]:
    """
    지원되는 외부 코드 패턴 목록을 반환합니다.
    """
    return get_supported_patterns()


# ============================================================================
# 서버 실행
# ============================================================================

if __name__ == "__main__":
    # print 문을 stderr로 출력
    print("🚀 Code Converter MCP Server (DeepAgents) 시작...", file=sys.stderr)
    print("📋 지원 패턴:", list(CODE_MAPPING_RULES.keys()), file=sys.stderr)
    print("📚 AGENTS.md: 비즈니스 규칙 로드됨", file=sys.stderr)
    print("🎯 Skills: 재사용 가능한 지침 로드됨", file=sys.stderr)
    mcp.run()
