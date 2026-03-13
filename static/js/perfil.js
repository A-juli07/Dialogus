// Preview de imagem antes do upload
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            const preview = document.getElementById('photoPreview');
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;

            // Animação de entrada
            const img = preview.querySelector('img');
            img.style.opacity = '0';
            img.style.transform = 'scale(0.8)';
            setTimeout(() => {
                img.style.transition = 'all 0.3s ease';
                img.style.opacity = '1';
                img.style.transform = 'scale(1)';
            }, 10);
        };

        reader.readAsDataURL(input.files[0]);
    }
}

// Contador de caracteres para Status
const statusInput = document.getElementById('id_status');
const statusCount = document.getElementById('statusCount');

if (statusInput && statusCount) {
    statusInput.addEventListener('input', function() {
        statusCount.textContent = this.value.length;
    });
}

// Contador de caracteres para Biografia
const bioInput = document.getElementById('id_biografia');
const bioCount = document.getElementById('bioCount');

if (bioInput && bioCount) {
    bioInput.addEventListener('input', function() {
        bioCount.textContent = this.value.length;
    });
}

// Validação do formulário
const form = document.getElementById('profileForm');
if (form) {
    form.addEventListener('submit', function(e) {
        const fileInput = document.getElementById('id_foto_perfil');

        // Validar tamanho do arquivo (5MB)
        if (fileInput.files.length > 0) {
            const fileSize = fileInput.files[0].size / 1024 / 1024; // em MB

            if (fileSize > 5) {
                e.preventDefault();

                if (typeof Dialogus !== 'undefined') {
                    Dialogus.NotificationManager.show(
                        'A imagem deve ter no máximo 5MB',
                        'error',
                        4000
                    );
                } else {
                    alert('A imagem deve ter no máximo 5MB');
                }
                return false;
            }
        }

        // Mostrar loader ao submeter
        if (typeof Dialogus !== 'undefined') {
            Dialogus.LoaderManager.show('Salvando perfil...');
        }
    });
}

// Prevenir perda de dados não salvos
let formChanged = false;

if (form) {
    const inputs = form.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('change', () => {
            formChanged = true;
        });
    });

    window.addEventListener('beforeunload', (e) => {
        if (formChanged) {
            e.preventDefault();
            e.returnValue = '';
            return '';
        }
    });

    form.addEventListener('submit', () => {
        formChanged = false;
    });
}
