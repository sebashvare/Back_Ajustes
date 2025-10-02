# =============================================================================
# CONFIGURACIÓN GUNICORN - SERVIDOR WSGI PARA PRODUCCIÓN
# =============================================================================
# Archivo de configuración para Gunicorn optimizado para el Sistema de 
# Registro de Ajustes en producción.

import multiprocessing
import os

# =============================================================================
# CONFIGURACIÓN DEL SERVIDOR
# =============================================================================

# Puerto en el que escucha el servidor
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Número de workers (procesos)
# Recomendación: (2 x CPU cores) + 1
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))

# Tipo de worker (sync para CPU-bound tasks, gevent para I/O-bound)
worker_class = "sync"

# Conexiones simultáneas por worker
worker_connections = 1000

# Timeout para requests (en segundos)
timeout = int(os.getenv('TIMEOUT', 30))

# Timeout para keep-alive connections
keepalive = 2

# =============================================================================
# CONFIGURACIÓN DE LOGS
# =============================================================================

# Nivel de logging
loglevel = os.getenv('LOG_LEVEL', 'info')

# Archivo de logs de acceso
accesslog = "/var/log/registro_ajustes/gunicorn_access.log"

# Archivo de logs de errores
errorlog = "/var/log/registro_ajustes/gunicorn_error.log"

# Formato de logs de acceso
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Capturar stdout/stderr
capture_output = True

# =============================================================================
# CONFIGURACIÓN DE PROCESOS
# =============================================================================

# PID file
pidfile = "/var/run/registro_ajustes/gunicorn.pid"

# Usuario para ejecutar los workers (solo en sistemas Unix)
user = os.getenv('GUNICORN_USER', 'www-data')
group = os.getenv('GUNICORN_GROUP', 'www-data')

# Reiniciar workers después de N requests (para prevenir memory leaks)
max_requests = 1000
max_requests_jitter = 100

# =============================================================================
# CONFIGURACIÓN DE DESARROLLO
# =============================================================================

# Recargar automáticamente en cambios de código (solo desarrollo)
if os.getenv('ENVIRONMENT') == 'development':
    reload = True
    workers = 1
    loglevel = 'debug'

# =============================================================================
# HOOKS DE APLICACIÓN
# =============================================================================

def when_ready(server):
    """Hook ejecutado cuando el servidor está listo."""
    server.log.info("Servidor Gunicorn iniciado para Sistema de Registro de Ajustes")

def worker_int(worker):
    """Hook ejecutado cuando un worker recibe SIGINT."""
    worker.log.info("Worker interrumpido, cerrando conexiones...")

def on_exit(server):
    """Hook ejecutado al cerrar el servidor."""
    server.log.info("Servidor Gunicorn detenido")

# =============================================================================
# CONFIGURACIÓN SSL (OPCIONAL)
# =============================================================================

# Certificados SSL (si se manejan en el servidor de aplicación)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
# ssl_version = 2  # TLS
# ciphers = "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"