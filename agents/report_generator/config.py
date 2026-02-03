"""
Report Generator Agent Configuration
======================================
에이전트 설정 및 모델 초기화
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 에이전트 디렉토리
AGENT_DIR = Path(__file__).parent
PROJECT_ROOT = AGENT_DIR.parent.parent


def get_model_config() -> dict:
    """
    OpenRouter 모델 설정을 반환합니다.
    
    Returns:
        모델 설정 딕셔너리
    """
    return {
        "model": "openai/gpt-5-nano",
        "model_provider": "openai",
        "openai_api_key": os.getenv("OPENROUTER_API_KEY"),
        "openai_api_base": "https://openrouter.ai/api/v1",
    }


def get_system_prompt() -> str:
    """
    System Prompt를 반환합니다 (WHO - 정체성과 절대 규칙).
    
    Returns:
        시스템 프롬프트 문자열
    """
    return """당신은 **코드 집계 및 리포트 생성 전문가**입니다.

## 정체성 (WHO)

- 외부 코드를 표준 코드로 변환하고 집계하여 리포트를 생성하는 전문가
- 정확하고 읽기 쉬운 마크다운 리포트를 제공하는 시스템

## 절대 규칙

1. **도구 사용 순서 준수**: batch_convert_codes → aggregate_by_standard_code → generate_markdown_report
2. **데이터 정확성**: 각 단계의 결과를 다음 단계의 입력으로 정확히 전달
3. **실패 시에도 리포트**: 변환 실패 항목이 있어도 가능한 범위 내에서 리포트 작성
4. **사용자 선호도 기억**: 특정 형식 요청 시 `/memories/user_preferences.md`에 저장
"""


def get_agents_md_path() -> str:
    """
    AGENTS.md 파일 경로를 반환합니다.
    
    Returns:
        AGENTS.md 절대 경로
    """
    return str(AGENT_DIR / "AGENTS.md")


def get_skills_paths() -> list[str]:
    """
    Skills 디렉토리 경로를 반환합니다.
    
    Returns:
        스킬 디렉토리 경로 리스트
    """
    skills_dir = AGENT_DIR / "skills"
    return [
        str(skills_dir / "reporting"),
        str(skills_dir / "finance"),
    ]


def get_mcp_server_config() -> dict:
    """
    MCP 서버 설정을 반환합니다.
    
    Returns:
        MCP 서버 설정 딕셔너리
    """
    return {
        "code_converter": {
            "command": "python",
            "args": ["-m", "agents.code_converter.server"],
            "cwd": str(PROJECT_ROOT),
            "transport": "stdio",
        }
    }
