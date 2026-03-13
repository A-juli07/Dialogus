const form = document.getElementById('inviteForm');
const hiddenInput = document.getElementById('id_destinatario');
const searchInput = document.getElementById('user_search');
const searchResults = document.getElementById('searchResults');
const selectedUserDiv = document.getElementById('selectedUser');

let searchTimeout;
let selectedUser = null;

// Função de busca real de usuários via AJAX
function searchUsers(query) {
    searchResults.innerHTML = '<div class="search-loading"><i class="bi bi-hourglass-split"></i> Buscando...</div>';
    searchResults.classList.add('active');

    if (query.length < 2) {
        searchResults.innerHTML = '<div class="search-no-results">Digite pelo menos 2 caracteres</div>';
        return;
    }

    fetch(`/chat/api/buscar-usuarios/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.usuarios.length === 0) {
                searchResults.innerHTML = `
                    <div class="search-no-results">
                        <i class="bi bi-info-circle"></i>
                        <p>Nenhum usuário encontrado</p>
                        <small style="display: block; margin-top: 0.75rem;">
                            <strong>Alternativa:</strong> Digite o ID diretamente<br>
                            <input type="number"
                                   placeholder="Ex: 123"
                                   style="margin-top: 0.5rem; padding: 0.5rem; border-radius: 8px; border: 2px solid var(--border-color); width: 150px; background: transparent; color: var(--text-primary);"
                                   onchange="selectUserById(this.value)">
                        </small>
                    </div>
                `;
                return;
            }

            let html = '';
            data.usuarios.forEach(user => {
                const initial = user.first_name ? user.first_name[0].toUpperCase() : user.username[0].toUpperCase();
                html += `
                    <div class="search-result-item" onclick="selectUser(${JSON.stringify(user).replace(/"/g, '&quot;')})">
                        <div class="search-result-avatar">${initial}</div>
                        <div class="search-result-info">
                            <p class="search-result-name">${user.full_name}</p>
                            <p class="search-result-username">@${user.username} • ID: ${user.id}</p>
                        </div>
                    </div>
                `;
            });
            searchResults.innerHTML = html;
        })
        .catch(error => {
            console.error('Erro na busca:', error);
            searchResults.innerHTML = `
                <div class="search-no-results">
                    <i class="bi bi-exclamation-triangle"></i>
                    <p>Erro ao buscar. Tente novamente.</p>
                </div>
            `;
        });
}

// Seleção direta por ID
window.selectUserById = function(userId) {
    if (!userId) return;

    selectedUser = {
        id: userId,
        username: `user_${userId}`,
        first_name: 'Usuário',
        last_name: userId
    };

    showSelectedUser();
    searchResults.classList.remove('active');
    searchInput.value = '';
};

// Event listeners
searchInput.addEventListener('input', function() {
    clearTimeout(searchTimeout);
    const query = this.value.trim();

    if (query.length === 0) {
        searchResults.classList.remove('active');
        return;
    }

    searchTimeout = setTimeout(() => {
        searchUsers(query);
    }, 300);
});

// Fechar resultados ao clicar fora
document.addEventListener('click', function(e) {
    if (!e.target.closest('.inv-search-container')) {
        searchResults.classList.remove('active');
    }
});

function selectUser(user) {
    selectedUser = user;
    showSelectedUser();
    searchResults.classList.remove('active');
    searchInput.value = '';
}

function showSelectedUser() {
    if (!selectedUser) return;

    const initial = selectedUser.first_name ? selectedUser.first_name[0].toUpperCase() : 'U';
    const fullName = selectedUser.first_name && selectedUser.last_name
        ? `${selectedUser.first_name} ${selectedUser.last_name}`.trim()
        : selectedUser.username;

    selectedUserDiv.innerHTML = `
        <div class="selected-user-avatar">${initial}</div>
        <div class="selected-user-info">
            <p class="selected-user-name">${fullName}</p>
            <p class="selected-user-id">@${selectedUser.username} (ID: ${selectedUser.id})</p>
        </div>
        <button type="button" class="selected-user-remove" onclick="clearSelectedUser()">
            <i class="bi bi-x-circle"></i>
        </button>
    `;

    selectedUserDiv.classList.add('active');
    hiddenInput.value = selectedUser.id;
}

window.clearSelectedUser = function() {
    selectedUser = null;
    selectedUserDiv.classList.remove('active');
    selectedUserDiv.innerHTML = '';
    hiddenInput.value = '';
    searchInput.focus();
};

// Validação do formulário
form.addEventListener('submit', function(e) {
    if (!hiddenInput.value) {
        e.preventDefault();
        alert('Por favor, selecione um usuário ou digite um ID válido');
        searchInput.focus();
    }
});
