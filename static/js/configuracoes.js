// Mostrar seção
function showSection(sectionId) {
    // Esconder todas as seções
    document.querySelectorAll('.settings-section').forEach(section => {
        section.style.display = 'none';
    });

    // Remover active de todos os itens
    document.querySelectorAll('.settings-item').forEach(item => {
        item.classList.remove('active');
    });

    // Mostrar seção selecionada
    const section = document.getElementById('section-' + sectionId);
    if (section) {
        section.style.display = 'block';
    }

    // Marcar item como ativo
    const item = document.querySelector(`.settings-item[data-section="${sectionId}"]`);
    if (item) {
        item.classList.add('active');
    }

    // Mobile: mostrar content
    if (window.innerWidth <= 900) {
        document.querySelector('.settings-content').classList.add('active');
    }
}

// Voltar no mobile
document.addEventListener('click', function(e) {
    if (e.target.closest('.section-header') && window.innerWidth <= 900) {
        document.querySelector('.settings-content').classList.remove('active');
    }
});

// Definir tema
function setTheme(theme) {
    // Remover active de todas as opções
    document.querySelectorAll('.theme-option').forEach(opt => {
        opt.classList.remove('active');
    });

    // Adicionar active na opção selecionada
    document.querySelector(`.theme-option[data-theme="${theme}"]`).classList.add('active');

    // Aplicar tema
    if (theme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
        document.documentElement.setAttribute('data-theme', theme);
    }

    // Salvar preferência
    localStorage.setItem('theme', theme);
}

// Definir papel de parede
function setWallpaper(wallpaper) {
    document.querySelectorAll('.wallpaper-option').forEach(opt => {
        opt.classList.remove('active');
    });
    document.querySelector(`.wallpaper-option[data-wallpaper="${wallpaper}"]`).classList.add('active');
    localStorage.setItem('wallpaper', wallpaper);

    // Aplicar imediatamente
    if (typeof applyWallpaper === 'function') {
        applyWallpaper(wallpaper);
    }
}

// Definir tamanho da fonte
function setFontSize(size) {
    document.querySelectorAll('.font-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`.font-btn[data-size="${size}"]`).classList.add('active');
    localStorage.setItem('fontSize', size);
}

// Modal
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId, event) {
    if (!event || event.target.classList.contains('modal-overlay')) {
        document.getElementById(modalId).classList.remove('active');
    }
}

// Pesquisar configurações
const searchSettingsEl = document.getElementById('searchSettings');
if (searchSettingsEl) {
    searchSettingsEl.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase();

        document.querySelectorAll('.settings-item').forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(query) ? 'flex' : 'none';
        });
    });
}

// Inicializar tema selecionado
document.addEventListener('DOMContentLoaded', function() {
    // Restaurar tema selecionado
    const savedTheme = localStorage.getItem('theme') || 'light';
    const themeOption = document.querySelector(`.theme-option[data-theme="${savedTheme}"]`);
    if (themeOption) {
        themeOption.classList.add('active');
    }

    // Restaurar wallpaper selecionado
    const savedWallpaper = localStorage.getItem('wallpaper') || 'default';
    document.querySelectorAll('.wallpaper-option').forEach(opt => opt.classList.remove('active'));
    const wallpaperOption = document.querySelector(`.wallpaper-option[data-wallpaper="${savedWallpaper}"]`);
    if (wallpaperOption) {
        wallpaperOption.classList.add('active');
    }
});

// Fechar modal com ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }
});
