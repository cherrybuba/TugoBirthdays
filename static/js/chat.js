function initChat(streamUrl, sendUrl, lastMessageId) {
    const container = document.getElementById('chat-messages');
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send');
    let currentLastId = lastMessageId;
    let myUsername = document.getElementById('chat-username').value;
    let es = null;

    function scrollToBottom() {
        container.scrollTop = container.scrollHeight;
    }

    function addMessage(msg) {
        const div = document.createElement('div');
        div.className = 'chat-message';
        if (msg.author === myUsername) {
            div.classList.add('mine');
        }
        div.innerHTML = `
            <span class="author">${msg.author}</span>
            <span class="time">${msg.created_at}</span>
            <div class="text">${msg.text}</div>
        `;
        container.appendChild(div);
        scrollToBottom();
    }

    function startStream() {
        es = new EventSource(streamUrl + '?last_id=' + currentLastId);
        es.onmessage = function(e) {
            const msg = JSON.parse(e.data);
            addMessage(msg);
            if (msg.id > currentLastId) currentLastId = msg.id;
        };
        es.onerror = function() {
            es.close();
            setTimeout(startStream, 3000);
        };
    }

    window.addEventListener('beforeunload', function() {
        if (es) es.close();
    });

    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            if (es) es.close();
        } else {
            startStream();
        }
    });

    function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        const formData = new FormData();
        formData.append('text', text);

        fetch(sendUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        }).then(r => r.json()).then(msg => {
            addMessage(msg);
            if (msg.id > currentLastId) currentLastId = msg.id;
            input.value = '';
        });
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
    });

    scrollToBottom();
    startStream();
}
