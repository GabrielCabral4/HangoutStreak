import os
import sys
import logging

# Configuração de logging
logging.basicConfig(
    filename='/home/HangoutStreak/logs/django.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)

# Log do início da execução
logging.info('Iniciando configuração WSGI')

try:
    # Adicione o diretório do projeto ao path
    path = '/home/HangoutStreak'
    if path not in sys.path:
        sys.path.append(path)
        logging.info(f'Adicionado {path} ao sys.path')
    
    # Log dos caminhos do sistema
    logging.info(f'sys.path: {sys.path}')
    
    # Configurações de ambiente
    os.environ['DJANGO_SETTINGS_MODULE'] = 'hangout_streak.settings_prod'
    logging.info('DJANGO_SETTINGS_MODULE configurado')
    
    # Configurações do banco de dados
    os.environ['DB_NAME'] = 'HangoutStreak$default'
    os.environ['DB_USER'] = 'HangoutStreak'
    os.environ['DB_PASSWORD'] = 'Gabriel2004'
    os.environ['DB_HOST'] = 'HangoutStreak.mysql.pythonanywhere-services.com'
    logging.info('Configurações do banco de dados definidas')
    
    # Configuração do Django Secret Key (chave gerada aleatoriamente)
    os.environ['DJANGO_SECRET_KEY'] = 'django-insecure-k9l3c#6y2$u4tl8)g3c1q9s8n2p5x7m0v4j1h8d6f9a2e5r7t0'
    logging.info('DJANGO_SECRET_KEY configurada')
    
    # Inicialize a aplicação WSGI
    logging.info('Importando get_wsgi_application')
    from django.core.wsgi import get_wsgi_application
    
    logging.info('Inicializando aplicação WSGI')
    application = get_wsgi_application()
    logging.info('Aplicação WSGI inicializada com sucesso')

except Exception as e:
    logging.error(f'Erro ao inicializar aplicação: {str(e)}', exc_info=True)
    raise 