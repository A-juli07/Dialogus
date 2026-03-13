// Variáveis de configuração são definidas inline no template:
// roomName, userLogged, window.currentChatPartner

const chatLog = document.querySelector('#chat-log');
const messageInput = document.querySelector('#chat-message-input');
const sendButton = document.querySelector('#chat-message-submit');

// Função para toggle sidebar no mobile
function toggleSidebarMobile() {
    const sidebar = document.getElementById('sidebarPanel');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
}

// WebSocket com gerenciamento melhorado
let chatSocket;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connectWebSocket() {
    chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + roomName + '/');

    chatSocket.onopen = function() {
        console.log('Conectado ao WebSocket');
        reconnectAttempts = 0;

        if (typeof Dialogus !== 'undefined') {
            Dialogus.NotificationManager.show('Conectado ao chat', 'success', 2000);
        }
    };

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        addMessage(data.username, data.message, data.username === userLogged);

        if (data.username !== userLogged) {
            playNotificationSound();
        }
    };

    chatSocket.onerror = function(error) {
        console.error('Erro no WebSocket:', error);
    };

    chatSocket.onclose = function(e) {
        console.log('WebSocket fechado. Tentando reconectar...');

        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            setTimeout(connectWebSocket, 2000 * reconnectAttempts);
        } else {
            if (typeof Dialogus !== 'undefined') {
                Dialogus.NotificationManager.show('Erro de conexão. Recarregue a página.', 'error');
            }
        }
    };
}

connectWebSocket();

function addMessage(username, message, isOwn) {
    const emptyState = chatLog.querySelector('.wa-empty-chat');
    if (emptyState) emptyState.remove();

    const messageClass = isOwn ? 'outgoing' : 'incoming';
    const now = new Date();
    const timeString = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

    const messageElement = document.createElement('div');
    messageElement.className = `wa-message ${messageClass}`;

    let messageHTML = '<div class="wa-message-bubble">';
    if (!isOwn) {
        messageHTML += `<span class="wa-message-sender">${escapeHtml(username)}</span>`;
    }
    messageHTML += `
        <p class="wa-message-text">${escapeHtml(message)}</p>
        <span class="wa-message-meta">
            <span class="wa-message-time">${timeString}</span>
            ${isOwn ? '<i class="bi bi-check2-all wa-read-receipt"></i>' : ''}
        </span>
    </div>`;

    messageElement.innerHTML = messageHTML;
    chatLog.appendChild(messageElement);
    chatLog.scrollTop = chatLog.scrollHeight;
}

function sendMessage() {
    const message = messageInput.value.trim();
    if (message.length === 0) return;

    if (message.length > 5000) {
        if (typeof Dialogus !== 'undefined') {
            Dialogus.NotificationManager.show('Mensagem muito longa (máx 5000 caracteres)', 'warning');
        }
        return;
    }

    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify({ 'message': message }));
        messageInput.value = '';
        messageInput.focus();
    } else {
        if (typeof Dialogus !== 'undefined') {
            Dialogus.NotificationManager.show('Erro ao enviar mensagem. Reconectando...', 'error');
        }
    }
}

sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function playNotificationSound() {
    // const audio = new Audio('/static/sounds/notification.mp3');
    // audio.volume = 0.3;
    // audio.play().catch(e => {});
}

window.addEventListener('load', function() {
    if (typeof Dialogus !== 'undefined') {
        Dialogus.ChatUtils.scrollToBottom(chatLog, false);
    } else {
        chatLog.scrollTop = chatLog.scrollHeight;
    }
});

document.addEventListener('DOMContentLoaded', function() {
    messageInput.focus();
});

window.addEventListener('beforeunload', function() {
    if (chatSocket) chatSocket.close();
});

// ========== BUSCA DE MENSAGENS ==========
const searchBar = document.getElementById('chatSearchBar');
const searchInput = document.getElementById('chatSearchInput');
const searchCountEl = document.getElementById('searchCount');
let searchMatches = [];
let currentMatchIndex = -1;
let originalTexts = new Map();

function toggleSearchBar() {
    const isActive = searchBar.classList.toggle('active');
    if (isActive) {
        searchInput.focus();
    } else {
        clearSearch();
    }
}

function clearSearch() {
    searchInput.value = '';
    searchCountEl.textContent = '';
    searchMatches = [];
    currentMatchIndex = -1;

    // Restaurar textos originais
    originalTexts.forEach((text, el) => {
        el.innerHTML = text;
    });
    originalTexts.clear();
}

function performSearch() {
    const query = searchInput.value.trim().toLowerCase();

    // Limpar highlights anteriores
    originalTexts.forEach((text, el) => {
        el.innerHTML = text;
    });
    originalTexts.clear();
    searchMatches = [];
    currentMatchIndex = -1;

    if (query.length === 0) {
        searchCountEl.textContent = '';
        return;
    }

    const messages = chatLog.querySelectorAll('.wa-message-text');

    messages.forEach(msgEl => {
        const text = msgEl.textContent;
        const lowerText = text.toLowerCase();

        if (lowerText.includes(query)) {
            // Salvar texto original
            if (!originalTexts.has(msgEl)) {
                originalTexts.set(msgEl, msgEl.innerHTML);
            }

            // Escapar o texto antes de usar como innerHTML para evitar XSS
            const safeText = escapeHtml(text);
            const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
            msgEl.innerHTML = safeText.replace(regex, '<mark class="search-highlight">$1</mark>');

            // Registrar matches
            const marks = msgEl.querySelectorAll('.search-highlight');
            marks.forEach(mark => searchMatches.push(mark));
        }
    });

    if (searchMatches.length > 0) {
        currentMatchIndex = 0;
        highlightCurrentMatch();
        searchCountEl.textContent = `1 de ${searchMatches.length}`;
    } else {
        searchCountEl.textContent = 'Nenhum resultado';
    }
}

function highlightCurrentMatch() {
    // Remover active de todos
    searchMatches.forEach(m => m.classList.remove('active'));

    if (currentMatchIndex >= 0 && currentMatchIndex < searchMatches.length) {
        const current = searchMatches[currentMatchIndex];
        current.classList.add('active');

        // Scroll até a mensagem
        const msgBubble = current.closest('.wa-message');
        if (msgBubble) {
            msgBubble.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}

function navigateSearch(direction) {
    if (searchMatches.length === 0) return;

    currentMatchIndex += direction;

    // Circular
    if (currentMatchIndex >= searchMatches.length) currentMatchIndex = 0;
    if (currentMatchIndex < 0) currentMatchIndex = searchMatches.length - 1;

    highlightCurrentMatch();
    searchCountEl.textContent = `${currentMatchIndex + 1} de ${searchMatches.length}`;
}

// Event listeners da busca
searchInput.addEventListener('input', performSearch);

searchInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        if (e.shiftKey) {
            navigateSearch(-1);
        } else {
            navigateSearch(1);
        }
    }
    if (e.key === 'Escape') {
        toggleSearchBar();
    }
});

// Atalho Ctrl+F para abrir busca
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        if (!searchBar.classList.contains('active')) {
            toggleSearchBar();
        } else {
            searchInput.focus();
            searchInput.select();
        }
    }
});

// ========== EMOJI PICKER ==========
let emojiPickerReady = false;

async function initEmojiPicker() {
    if (emojiPickerReady) return;
    emojiPickerReady = true;

    const response = await fetch('https://cdn.jsdelivr.net/npm/@emoji-mart/data@1/sets/14/native.json');
    const data = await response.json();

    const htmlEl = document.documentElement;
    const theme = htmlEl.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';

    const picker = new EmojiMart.Picker({
        data,
        locale: 'pt',
        theme,
        previewPosition: 'none',
        skinTonePosition: 'search',
        onEmojiSelect: (emoji) => {
            insertEmoji(emoji.native);
            closeEmojiPicker();
        },
    });

    document.getElementById('emoji-picker-container').appendChild(picker);
}

function toggleEmojiPicker() {
    const container = document.getElementById('emoji-picker-container');
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        initEmojiPicker();
    } else {
        container.classList.add('hidden');
    }
}

function closeEmojiPicker() {
    document.getElementById('emoji-picker-container').classList.add('hidden');
}

function insertEmoji(native) {
    const pos = messageInput.selectionStart;
    const before = messageInput.value.substring(0, pos);
    const after = messageInput.value.substring(pos);
    messageInput.value = before + native + after;
    messageInput.selectionStart = messageInput.selectionEnd = pos + native.length;
    messageInput.focus();
}

// Fechar picker ao clicar fora
document.addEventListener('click', function(e) {
    const container = document.getElementById('emoji-picker-container');
    const btn = document.getElementById('emoji-btn');
    if (!container.contains(e.target) && !btn.contains(e.target)) {
        closeEmojiPicker();
    }
});
