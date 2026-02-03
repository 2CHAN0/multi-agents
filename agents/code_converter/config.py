"""
Code Converter Agent Configuration
====================================
에이전트 설정 및 모델 초기화
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 에이전트 디렉토리
AGENT_DIR = Path(__file__).parent


def get_model_config() -> dict:
    """
    OpenRouter 모델 설정을 반환합니다.
    
    Returns:
        모델 설정 딕셔너리
    """
    return {
        "model": "google/gemini-3-flash-preview",
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
    return """당신은 **코드 변환 전문 에이전트**입니다.

## 정체성 (WHO)

- 외부 시스템의 코드를 내부 표준 코드로 변환하는 전문가
- 정확성과 일관성을 최우선으로 하는 변환 시스템

## 절대 규칙

1. **반드시 도구 사용**: 모든 변환은 `lookup_standard_code` 도구를 통해서만 수행
2. **JSON 형식 준수**: 변환 결과는 항상 정확한 JSON 형식으로 반환
3. **실패 시에도 응답**: 알 수 없는 패턴도 기본 카테고리(X)로 변환하여 응답
4. **학습 기록**: 새로운 패턴 발견 시 `/memories/new_patterns.md`에 반드시 기록
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
    return [str(skills_dir)]
