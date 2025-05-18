from .settings import *
import os

# SECURITY
DEBUG = False
SECRET_KEY = 'temporario-para-teste'
ALLOWED_HOSTS = ['.pythonanywhere.com']

# Database - usando PyMySQL
import pymysql
pymysql.install_as_MySQLdb()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'HangoutStreak$default',
        'USER': 'HangoutStreak',
        'PASSWORD': 'Gabriel2004',
        'HOST': 'HangoutStreak.mysql.pythonanywhere-services.com',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
} 