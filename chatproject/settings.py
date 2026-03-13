from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Em produção, defina DJANGO_SECRET_KEY como variável de ambiente
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-abc123-use-env-var-in-production')

# Em produção, defina DEBUG=False via variável de ambiente
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# Em produção, defina como o domínio real: DJANGO_ALLOWED_HOSTS=meusite.com
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chatproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chatproject.wsgi.application'
ASGI_APPLICATION = 'chatproject.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.environ.get('REDIS_HOST', '127.0.0.1'), int(os.environ.get('REDIS_PORT', 6379)))],
        },
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ── Segurança ──────────────────────────────────────────────────────────────
# Protege cookies contra acesso via JavaScript (mitigação de XSS)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Impede que o navegador adivinhe o Content-Type dos arquivos (MIME sniffing)
SECURE_CONTENT_TYPE_NOSNIFF = True

# Impede que o site seja exibido em iframes (proteção contra clickjacking)
X_FRAME_OPTIONS = 'DENY'

# Em produção (HTTPS), descomente as linhas abaixo:
# SESSION_COOKIE_SECURE = True   # Cookies apenas via HTTPS
# CSRF_COOKIE_SECURE = True      # CSRF apenas via HTTPS
# SECURE_SSL_REDIRECT = True     # Redireciona HTTP → HTTPS
# SECURE_HSTS_SECONDS = 31536000 # HTTP Strict Transport Security (1 ano)
