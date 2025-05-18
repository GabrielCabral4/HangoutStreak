from .settings import *
import os

# SECURITY
DEBUG = False
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'change-me-in-production')
ALLOWED_HOSTS = ['.pythonanywhere.com']

# Database - usando PyMySQL
import pymysql
pymysql.install_as_MySQLdb()

# Garantindo que o nome do banco de dados tenha o $ escapado
db_name = os.getenv('DB_NAME', 'HangoutStreak$default').replace('\\$', '$')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': db_name,
        'USER': os.getenv('DB_USER', 'HangoutStreak'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'Gabriel2004'),
        'HOST': os.getenv('DB_HOST', 'HangoutStreak.mysql.pythonanywhere-services.com'),
        'PORT': '',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'sql_mode': 'STRICT_TRANS_TABLES',
        },
    }
}

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_ROOT = BASE_DIR / 'media'

# Channels - Usando InMemoryChannelLayer para o plano gratuito
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# HTTPS
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
} 