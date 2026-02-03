# LangChain DeepAgents Multi-Agent System

LangChain **DeepAgents 프레임워크** 기반의 Multi-Agent 시스템 데모입니다.

## 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Main Agent (LangServe)               │
│                    http://localhost:8000                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Report Generator DeepAgent (Gemini)            │   │
│  │  - create_deep_agent() 사용                     │   │
│  │  - MCP 서버 호출 (코드 변환)                    │   │
│  │  - 데이터 집계 + 마크다운 리포트 생성           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Code Converter Agent (MCP Server)          │
│                       stdio                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │  MCP Tools:                                      │   │
│  │  - convert_code: 단일 코드 변환                  │   │
│  │  - batch_convert_codes: 일괄 변환                │   │
│  │  - get_supported_patterns: 패턴 조회             │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 설치

```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## 환경변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일에 Gemini API 키 입력
GOOGLE_API_KEY=your_gemini_api_key_here
```

API 키는 [Google AI Studio](https://aistudio.google.com/apikey)에서 발급받을 수 있습니다.

## 실행

### LangServe 서버 실행 (메인 에이전트)

```bash
python -m main_agent.report_agent_server
```

서버가 실행되면:
- API 문서: http://localhost:8000/docs
- 플레이그라운드: http://localhost:8000/report/playground

### API 호출 예시

```bash
curl -X POST http://localhost:8000/report/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "external_codes": ["EXT-PROD-001", "EXT-PROD-002", "VENDOR-100"],
      "quantities": [10, 20, 15]
    }
  }'
```

### MCP 서버 단독 테스트

```bash
python -m mcp_server.code_converter_server
```

## 지원 코드 패턴

| 외부 코드 패턴 | 변환 결과 | 설명 |
|---------------|----------|------|
| EXT-PROD-XXX | STD-XXX-A | 외부 제품 |
| EXT-SVC-XXX | STD-XXX-B | 외부 서비스 |
| EXT-MAT-XXX | STD-XXX-C | 외부 자재 |
| VENDOR-XXX | STD-XXX-V | 벤더 코드 |
| PARTNER-XXX | STD-XXX-P | 파트너 코드 |
| 기타 | STD-XXX-X | 알 수 없는 패턴 |

## 프로젝트 구조

```
multi-agents/
├── requirements.txt        # 의존성 패키지
├── .env.example           # 환경변수 예시
├── README.md              # 이 파일
├── mcp_server/
│   ├── __init__.py
│   └── code_converter_server.py  # MCP 서버 (DeepAgent 기반)
└── main_agent/
    ├── __init__.py
    └── report_agent_server.py    # LangServe 서버 (DeepAgent 기반)
```

## 기술 스택

- **DeepAgents**: LangChain의 Deep Agent 프레임워크
- **LangGraph**: 상태 기반 에이전트 런타임
- **LangServe**: HTTP API 서버
- **MCP (Model Context Protocol)**: 에이전트 간 통신
- **Google Gemini**: LLM (gemini-2.0-flash)
- **FastAPI**: 웹 프레임워크

## DeepAgents 핵심 패턴

```python
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

# Gemini 모델 초기화
model = init_chat_model(model="google_genai:gemini-2.0-flash")

# DeepAgent 생성
agent = create_deep_agent(
    model=model,
    tools=[my_tool],
    system_prompt="You are an expert..."
)

# 에이전트 실행
result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
```
