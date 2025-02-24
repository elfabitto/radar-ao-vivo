# Configuração do Gunicorn para ambiente de produção
import os
import multiprocessing

# Definir variável de ambiente para indicar que estamos em produção
os.environ['PRODUCTION'] = 'true'

# Número de workers (processos)
workers = multiprocessing.cpu_count() * 2 + 1

# Número de threads por worker
threads = 2

# Timeout em segundos
timeout = 120

# Bind address
bind = "0.0.0.0:8000"

# Módulo da aplicação
wsgi_app = "app_web:app"

# Configurações de log
accesslog = "access.log"
errorlog = "error.log"
loglevel = "info"

# Configurações de segurança
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de performance
worker_class = "sync"
worker_connections = 1000
keepalive = 5

# Configurações de reinicialização
max_requests = 1000
max_requests_jitter = 50

# Configurações de segurança
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Configurações de proxy
forwarded_allow_ips = '*'
proxy_protocol = False
proxy_allow_ips = '*'

# Configurações de depuração
capture_output = True
enable_stdio_inheritance = True

# Configurações de reinicialização
graceful_timeout = 30
