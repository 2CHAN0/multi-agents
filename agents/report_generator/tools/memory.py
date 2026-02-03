"""
Memory Tools
============
사용자 선호도 및 기록을 저장하는 도구
"""

from pathlib import Path
from langchain.tools import tool

# 에이전트 경로 설정
AGENT_DIR = Path(__file__).parent.parent
MEMORIES_DIR = AGENT_DIR / "memories"

@tool
def save_user_preference(content: str) -> str:
    """
    사용자의 선호도나 요청 사항을 memories/user_preferences.md 파일에 저장합니다.
    리포트 형식, 선호하는 통화 등을 저장할 때 사용하세요.
    
    Args:
        content: 저장할 내용 (마크다운 형식 권장)
    """
    MEMORIES_DIR.mkdir(parents=True, exist_ok=True)
    file_path = MEMORIES_DIR / "user_preferences.md"
    
    try:
        # 기존 내용이 있으면 유지하면서 추가하거나, 상황에 따라 덮어쓰기
        # 여기서는 단순화를 위해 덮어쓰기로 구현 (필요시 append 모드로 변경 가능)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# User Preferences\n\n{content}\n")
        return f"성공적으로 메모리에 저장되었습니다: {file_path}"
    except Exception as e:
        return f"저장 중 오류 발생: {str(e)}"
