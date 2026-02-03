const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const approvalTemplate = document.getElementById('approval-template');

let currentThreadId = null;

// 메시지 추가 함수
function addMessage(content, isUser = false) {
    const div = document.createElement('div');
    div.className = `chat-message ${isUser ? 'user-message' : 'agent-message'}`;

    // Markdown to HTML conversion (simple substitute)
    // 실제로는 marked.js 등을 사용하는 것이 좋습니다.
    const htmlContent = content
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    div.innerHTML = htmlContent;
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 승인 카드 추가 함수
function addApprovalCard(toolName, args, threadId, callback) {
    const clone = approvalTemplate.content.cloneNode(true);
    const card = clone.querySelector('.approval-card');

    clone.querySelector('.tool-name').textContent = toolName;

    // get_exchange_rate의 경우 특별한 UI 제공
    if (toolName === 'get_exchange_rate') {
        const argsDisplay = clone.querySelector('.tool-args');
        const baseCurrency = args.base_currency || 'USD';
        const targetCurrency = args.target_currency || 'KRW';

        argsDisplay.innerHTML = `
            <div class="space-y-2">
                <p><strong>기준 화폐:</strong> ${baseCurrency}</p>
                <p><strong>목표 화폐:</strong> ${targetCurrency}</p>
                <div class="mt-4">
                    <label class="block text-sm font-medium mb-2">다른 화폐로 변경:</label>
                    <select id="currency-select" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        <option value="KRW" ${targetCurrency === 'KRW' ? 'selected' : ''}>KRW (한국 원)</option>
                        <option value="JPY" ${targetCurrency === 'JPY' ? 'selected' : ''}>JPY (일본 엔)</option>
                        <option value="EUR" ${targetCurrency === 'EUR' ? 'selected' : ''}>EUR (유로)</option>
                        <option value="GBP" ${targetCurrency === 'GBP' ? 'selected' : ''}>GBP (영국 파운드)</option>
                        <option value="CNY" ${targetCurrency === 'CNY' ? 'selected' : ''}>CNY (중국 위안)</option>
                    </select>
                </div>
            </div>
        `;
    } else {
        clone.querySelector('.tool-args').textContent = JSON.stringify(args, null, 2);
    }

    const approveBtn = clone.querySelector('.approve-btn');
    const rejectBtn = clone.querySelector('.reject-btn');
    const editBtn = clone.querySelector('.edit-btn');
    const editForm = clone.querySelector('.edit-form');
    const editInput = clone.querySelector('.edit-args-input');
    const confirmEditBtn = clone.querySelector('.confirm-edit-btn');
    const cancelEditBtn = clone.querySelector('.cancel-edit-btn');

    // 승인 버튼
    approveBtn.onclick = () => {
        card.remove();
        callback('approve');
    };

    // 거부 버튼
    rejectBtn.onclick = () => {
        card.remove();
        callback('reject');
    };

    // 수정 버튼 - get_exchange_rate의 경우 드롭다운 값 사용
    if (toolName === 'get_exchange_rate') {
        editBtn.textContent = '선택한 화폐로 조회';
        editBtn.onclick = () => {
            const select = document.getElementById('currency-select');
            const newCurrency = select.value;
            const newArgs = {
                base_currency: args.base_currency || 'USD',
                target_currency: newCurrency
            };
            card.remove();
            callback('edit', newArgs);
        };
    } else {
        // 기존 수정 로직
        editBtn.onclick = () => {
            editForm.classList.remove('hidden');
            editInput.value = JSON.stringify(args, null, 2);
            editBtn.classList.add('hidden');
            approveBtn.classList.add('hidden');
            rejectBtn.classList.add('hidden');
        };
    }

    // 취소 버튼
    cancelEditBtn.onclick = () => {
        editForm.classList.add('hidden');
        editBtn.classList.remove('hidden');
        approveBtn.classList.remove('hidden');
        rejectBtn.classList.remove('hidden');
    };

    // 수정 확인 버튼
    confirmEditBtn.onclick = () => {
        try {
            const newArgs = JSON.parse(editInput.value);
            card.remove();
            callback('edit', newArgs);
        } catch (e) {
            alert('유효한 JSON 형식이 아닙니다.');
        }
    };

    chatContainer.appendChild(clone);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 서버 요청 함수
async function sendMessage(text) {
    // 간단한 파싱: "코드 10개" 같은 입력을 구조화된 데이터로 변환
    // 실제로는 LLM이 파싱해주는 것이 좋지만 여기서는 데모용으로 간단히 처리
    // 혹은 instruction 필드에 전체 텍스트를 넣어서 서버에서 처리하게 함

    // 입력값을 instruction으로 간주
    const payload = {
        external_codes: ["EXT-DEMO"], // Dummy defaults if not parsed
        quantities: [1],
        instruction: text
    };

    // 코드 패턴이 보이면 추출 시도 (간단한 정규식)
    const codeMatch = text.match(/([A-Z]+-[A-Z]+-\d+)/g);
    const numMatch = text.match(/(\d+)개/g);

    if (codeMatch) {
        payload.external_codes = codeMatch;
        payload.quantities = new Array(codeMatch.length).fill(1); // 기본 1개

        if (numMatch && numMatch.length === codeMatch.length) {
            payload.quantities = numMatch.map(s => parseInt(s));
        } else if (numMatch && numMatch.length === 1) {
            // 전체 개수로 가정
            payload.quantities = new Array(codeMatch.length).fill(parseInt(numMatch[0]));
        }
    }

    try {
        const response = await fetch('/report/invoke', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: payload })
        });

        const data = await response.json();
        // LangServe wraps result in 'output'
        if (data.output) {
            handleResponse(data.output);
        } else {
            handleResponse(data);
        }

    } catch (error) {
        addMessage(`Error: ${error.message}`);
    }
}

// Resume 요청 함수
async function resumeReport(decision, editedArgs = null) {
    if (!currentThreadId) return;

    try {
        const response = await fetch('/report/resume', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                thread_id: currentThreadId,
                decision: decision,
                edited_args: editedArgs
            })
        });

        const data = await response.json();
        handleResponse(data);

    } catch (error) {
        addMessage(`Error: ${error.message}`);
    }
}

// 응답 처리 공통 함수
function handleResponse(data) {
    console.log("handleResponse received:", data);

    if (data.thread_id) {
        currentThreadId = data.thread_id;
    }

    if (data.status === 'completed') {
        addMessage(data.report);
    } else if (data.status === 'interrupted') {
        // 인터럽트 발생
        console.log("Interrupt data:", data.interrupts);

        if (!data.interrupts || !data.interrupts.action_requests || data.interrupts.action_requests.length === 0) {
            console.error("Invalid interrupt structure:", data);
            addMessage("⚠️ 인터럽트가 발생했으나 세부 정보를 불러오지 못했습니다.");
            return;
        }

        const interrupt = data.interrupts;
        // action_requests에서 첫 번째 것만 처리 (단순화)
        const action = interrupt.action_requests[0];

        addMessage('⚠️ 작업을 계속하려면 승인이 필요합니다.');
        addApprovalCard(action.name, action.args, currentThreadId, (decision, args) => {
            resumeReport(decision, args);
        });
    } else if (data.error) {
        addMessage(`Error: ${data.error}`);
    } else {
        console.warn("Unknown status:", data.status);
    }
}

// 이벤트 리스너
sendBtn.addEventListener('click', () => {
    const text = userInput.value.trim();
    if (text) {
        addMessage(text, true);
        userInput.value = '';
        sendMessage(text); // TODO: implement sendMessage to properly construct request
    }
});

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});
