// ========================================
// DIALOGUS - JAVASCRIPT PRINCIPAL
// Funcionalidades: Tema, Animações, Utilidades
// ========================================

// ========== GERENCIAMENTO DE TEMA ==========
class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        // Aplicar tema salvo
        this.applyTheme(this.currentTheme);

        // Criar botão de toggle - DESABILITADO (seletor na sidebar)
        // this.createToggleButton();
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        localStorage.setItem('theme', theme);
        this.updateToggleIcon();
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    createToggleButton() {
        // Verificar se já existe
        if (document.querySelector('.theme-toggle')) return;

        const button = document.createElement('button');
        button.className = 'theme-toggle';
        button.setAttribute('aria-label', 'Alternar tema');
        button.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';

        button.addEventListener('click', () => this.toggleTheme());

        document.body.appendChild(button);
    }

    updateToggleIcon() {
        const button = document.querySelector('.theme-toggle');
        if (!button) return;

        if (this.currentTheme === 'dark') {
            button.innerHTML = '<i class="bi bi-sun-fill"></i>';
        } else {
            button.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
        }
    }
}

// ========== ANIMAÇÕES DE ENTRADA ==========
class AnimationManager {
    constructor() {
        this.init();
    }

    init() {
        this.observeElements();
    }

    observeElements() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, {
            threshold: 0.1
        });

        // Observar cards e elementos com classe animate
        document.querySelectorAll('.card-modern, .room-card, .contact-item, .animate').forEach(el => {
            observer.observe(el);
        });
    }
}

// ========== NOTIFICAÇÕES ==========
class NotificationManager {
    static show(message, type = 'info', duration = 3000, badge = null) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;

        const badgeHtml = badge && badge > 0
            ? `<span class="notification-badge">${badge}</span>`
            : '';

        notification.innerHTML = `
            <div class="notification-content">
                <i class="bi bi-${this.getIcon(type)}"></i>
                <span>${message}</span>
                ${badgeHtml}
            </div>
        `;

        // Cores por tipo
        const colors = {
            success: { bg: '#10b981', color: '#ffffff' },
            error: { bg: '#ef4444', color: '#ffffff' },
            warning: { bg: '#f59e0b', color: '#ffffff' },
            info: { bg: '#3b82f6', color: '#ffffff' }
        };
        const scheme = colors[type] || colors.info;

        // Estilos inline
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${scheme.bg};
            color: ${scheme.color};
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            z-index: 9999;
            animation: slideInRight 0.3s ease;
            max-width: 300px;
            font-weight: 500;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    static getIcon(type) {
        const icons = {
            success: 'check-circle-fill',
            error: 'x-circle-fill',
            warning: 'exclamation-triangle-fill',
            info: 'info-circle-fill'
        };
        return icons[type] || icons.info;
    }
}

// ========== UTILITÁRIOS DE CHAT ==========
class ChatUtils {
    // Formatar timestamp
    static formatTime(date) {
        const now = new Date();
        const messageDate = new Date(date);
        const diff = now - messageDate;

        // Menos de 1 minuto
        if (diff < 60000) {
            return 'Agora';
        }

        // Menos de 1 hora
        if (diff < 3600000) {
            const minutes = Math.floor(diff / 60000);
            return `${minutes} min atrás`;
        }

        // Menos de 24 horas
        if (diff < 86400000) {
            return messageDate.toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        // Mais de 24 horas
        return messageDate.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }

    // Escapar HTML para prevenir XSS
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Detectar URLs e torná-las clicáveis
    static linkify(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, (url) => {
            return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
        });
    }

    // Scroll suave para o final do chat
    static scrollToBottom(element, smooth = true) {
        if (!element) return;

        if (smooth) {
            element.scrollTo({
                top: element.scrollHeight,
                behavior: 'smooth'
            });
        } else {
            element.scrollTop = element.scrollHeight;
        }
    }
}

// ========== VALIDAÇÃO DE FORMULÁRIOS ==========
class FormValidator {
    static validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    static validatePassword(password) {
        // Mínimo 8 caracteres
        return password.length >= 8;
    }

    static validateUsername(username) {
        // 3-20 caracteres, apenas letras, números e underscore
        const re = /^[a-zA-Z0-9_]{3,20}$/;
        return re.test(username);
    }

    static showError(inputElement, message) {
        // Remover erro anterior
        this.clearError(inputElement);

        // Adicionar classe de erro
        inputElement.classList.add('is-invalid');

        // Criar mensagem de erro
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;

        inputElement.parentNode.appendChild(errorDiv);
    }

    static clearError(inputElement) {
        inputElement.classList.remove('is-invalid');

        const errorDiv = inputElement.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
}

// ========== WEBSOCKET HELPER ==========
class WebSocketManager {
    constructor(url) {
        this.url = url;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
    }

    connect(onMessage, onError) {
        try {
            this.socket = new WebSocket(this.url);

            this.socket.onopen = () => {
                console.log('WebSocket conectado');
                this.reconnectAttempts = 0;
                NotificationManager.show('Conectado ao chat', 'success');
            };

            this.socket.onmessage = (e) => {
                if (onMessage) onMessage(e);
            };

            this.socket.onerror = (error) => {
                console.error('Erro WebSocket:', error);
                if (onError) onError(error);
            };

            this.socket.onclose = () => {
                console.log('WebSocket desconectado');
                this.attemptReconnect(onMessage, onError);
            };

        } catch (error) {
            console.error('Erro ao conectar WebSocket:', error);
            if (onError) onError(error);
        }
    }

    attemptReconnect(onMessage, onError) {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Tentando reconectar... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
                this.connect(onMessage, onError);
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            NotificationManager.show('Não foi possível conectar ao chat', 'error');
        }
    }

    send(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
            return true;
        }
        return false;
    }

    close() {
        if (this.socket) {
            this.socket.close();
        }
    }
}

// ========== LOADER ==========
class LoaderManager {
    static show(message = 'Carregando...') {
        // Remover loader existente
        this.hide();

        const loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.innerHTML = `
            <div class="loader-backdrop">
                <div class="loader-content">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3 mb-0">${message}</p>
                </div>
            </div>
        `;

        // Estilos inline
        loader.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        const backdrop = loader.querySelector('.loader-backdrop');
        backdrop.style.cssText = `
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        const content = loader.querySelector('.loader-content');
        content.style.cssText = `
            background: white;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
        `;

        document.body.appendChild(loader);
    }

    static hide() {
        const loader = document.getElementById('global-loader');
        if (loader) {
            loader.remove();
        }
    }
}

// ========== INICIALIZAÇÃO ==========
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar gerenciador de tema
    window.themeManager = new ThemeManager();

    // Inicializar animações
    window.animationManager = new AnimationManager();

    // Adicionar tooltips do Bootstrap
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Log de inicialização
    console.log('🚀 Dialogus iniciado com sucesso!');
});

// ========== TEMA E WALLPAPER GLOBAIS (usados em base.html) ==========
function applyTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
    localStorage.setItem('dialogus-theme', theme);
}

function toggleTheme() {
    const currentTheme = localStorage.getItem('dialogus-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
}

function applyWallpaper(wallpaper) {
    document.documentElement.removeAttribute('data-wallpaper');
    if (wallpaper && wallpaper !== 'default') {
        document.documentElement.setAttribute('data-wallpaper', wallpaper);
    }
}

// ========== INICIALIZAÇÃO DO LAYOUT BASE ==========
document.addEventListener('DOMContentLoaded', function() {
    // Carregar tema e wallpaper salvos
    const savedTheme = localStorage.getItem('dialogus-theme') || 'light';
    applyTheme(savedTheme);

    const savedWallpaper = localStorage.getItem('wallpaper') || 'default';
    applyWallpaper(savedWallpaper);

    // Busca na sidebar
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            document.querySelectorAll('.conversation-item').forEach(item => {
                const name = item.getAttribute('data-name') || item.textContent.toLowerCase();
                item.style.display = name.includes(query) ? 'flex' : 'none';
            });
        });
    }

    // Limpa badge ao clicar em uma conversa
    document.querySelectorAll('.conversation-item').forEach(function(item) {
        item.addEventListener('click', function() {
            var badge = this.querySelector('.unread-badge');
            if (badge) badge.style.display = 'none';
        });
    });

    // Mobile: toggle sidebar ao clicar em ícone da nav
    const navIcons = document.querySelectorAll('.nav-icon');
    navIcons.forEach(icon => {
        icon.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                document.getElementById('sidebarPanel').classList.add('active');
            }
        });
    });
});

// Fechar sidebar no mobile ao clicar fora
document.addEventListener('click', function(e) {
    if (window.innerWidth <= 768) {
        const sidebar = document.getElementById('sidebarPanel');
        const navSidebar = document.querySelector('.nav-sidebar');
        if (sidebar && navSidebar && !sidebar.contains(e.target) && !navSidebar.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    }
});

// ========== WEBSOCKET DE NOTIFICAÇÕES ==========
(function() {
    const userId = window.DIALOGUS_USER_ID;
    if (!userId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let notifReconnectTimer;

    function connectNotifSocket() {
        var notifSocket = new WebSocket(
            protocol + '//' + window.location.host + '/ws/notifications/' + userId + '/'
        );

        notifSocket.onmessage = function(e) {
            var data = JSON.parse(e.data);
            if (data.type !== 'nova_dm') return;

            // Não notifica se já estiver conversando com este usuário
            var isChattingWithSender = (
                typeof window.currentChatPartner !== 'undefined' &&
                window.currentChatPartner !== null &&
                window.currentChatPartner === data.from_user
            );

            // Atualiza badge do DM específico no sidebar
            var dmBadge = document.querySelector('#dm-unread-' + data.sala_id);
            if (dmBadge && !isChattingWithSender) {
                dmBadge.textContent = (parseInt(dmBadge.textContent) || 0) + 1;
                dmBadge.style.display = 'flex';
            }

            if (!isChattingWithSender && typeof Dialogus !== 'undefined') {
                Dialogus.NotificationManager.show(
                    'Nova mensagem de ' + data.from_user,
                    'info',
                    5000,
                    data.unread_count
                );

                // Atualiza badge de mensagens não lidas na nav
                var navConversas = document.querySelector('.nav-icon[title="Conversas"]');
                if (navConversas) {
                    var badge = navConversas.querySelector('.badge-count');
                    if (!badge) {
                        badge = document.createElement('span');
                        badge.className = 'badge-count';
                        navConversas.appendChild(badge);
                    }
                    badge.textContent = (parseInt(badge.textContent) || 0) + 1;
                }
            }
        };

        notifSocket.onclose = function() {
            clearTimeout(notifReconnectTimer);
            notifReconnectTimer = setTimeout(connectNotifSocket, 3000);
        };
    }

    connectNotifSocket();
})();

// ========== EXPORTAR PARA USO GLOBAL ==========
window.Dialogus = {
    ThemeManager,
    AnimationManager,
    NotificationManager,
    ChatUtils,
    FormValidator,
    WebSocketManager,
    LoaderManager
};
