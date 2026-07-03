function getCookie(name) {
    let value = null;
    document.cookie.split(';').forEach(c => {
        c = c.trim();
        if (c.startsWith(name + '=')) {
            value = decodeURIComponent(c.substring(name.length + 1));
        }
    });
    return value;
}

function apiPost(url, data = {}) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(data),
    }).then(r => r.json());
}

function toggleSubscription(url, btn) {
    const unsubText = btn.dataset.unsubText || 'Подписаться';
    apiPost(url).then(data => {
        if (data.subscribed !== undefined) {
            btn.classList.toggle('active', data.subscribed);
            btn.textContent = data.subscribed ? 'Отписаться' : unsubText;
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.sub-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            toggleSubscription(btn.dataset.url, btn);
        });
    });
});
