// window.CRIAR_SALA_IS_PRIVATE é definido inline no template

// Character counter
const textarea = document.getElementById('id_descricao');
const charCount = document.getElementById('charCount');

if (textarea && charCount) {
    charCount.textContent = textarea.value.length;
    textarea.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });
}

// Privacy toggle
const publicOption = document.getElementById('publicOption');
const privateOption = document.getElementById('privateOption');
const passwordField = document.getElementById('passwordField');
const privadaInput = document.getElementById('id_privada');
let isPrivate = window.CRIAR_SALA_IS_PRIVATE || false;

function updatePrivacyUI() {
    if (isPrivate) {
        publicOption.classList.remove('active');
        privateOption.classList.add('active');
        passwordField.style.display = 'block';
        privadaInput.value = 'on';
    } else {
        publicOption.classList.add('active');
        privateOption.classList.remove('active');
        passwordField.style.display = 'none';
        privadaInput.value = '';
    }
}

publicOption.addEventListener('click', function() {
    isPrivate = false;
    updatePrivacyUI();
});

privateOption.addEventListener('click', function() {
    isPrivate = true;
    updatePrivacyUI();
});

updatePrivacyUI();

function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const button = field.parentElement.querySelector('.cg-password-toggle');
    const icon = button.querySelector('i');

    if (field.type === 'password') {
        field.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    } else {
        field.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    }
}
