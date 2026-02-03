#!/bin/bash

# Remote MCP Architecture 실행 데모

# 1. Code Converter를 독립된 서버로 실행 (Port 8001)
echo "📡 Code Converter를 독립 서버로 시작합니다 (Port 8001)..."
python -m agents.code_converter.server --port 8001 &
CONVERTER_PID=$!

# 서버가 뜰 때까지 잠시 대기
sleep 3

# 2. Report Generator를 실행하되, 환경 변수로 원격 서버 위치를 알려줌
echo "🚀 Report Generator를 Remote MCP 모드로 시작합니다..."
export CODE_CONVERTER_URL="http://localhost:8001/sse"
python -m agents.report_generator.server

# 종료 시 자식 프로세스 정리
kill $CONVERTER_PID
