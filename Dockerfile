# =============================================================================
# DOCKERFILE - SISTEMA DE REGISTRO DE AJUSTES
# =============================================================================
# Dockerfile optimizado para producción del Sistema de Registro de Ajustes
# Incluye mejores prácticas de seguridad y performance.

# Usar imagen base oficial de Python (Alpine para menor tamaño)
FROM python:3.11-alpine3.18

# =============================================================================
# METADATOS DE LA IMAGEN
# =============================================================================
LABEL maintainer="Sistema de Desarrollo <dev@empresa.com>"
LABEL version="1.0.0"
LABEL description="Sistema de Registro de Ajustes - API Backend"

# =============================================================================
# VARIABLES DE ENTORNO
# =============================================================================
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ENVIRONMENT=production

# =============================================================================
# INSTALACIÓN DE DEPENDENCIAS DEL SISTEMA
# =============================================================================
RUN apk update && apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev \
    linux-headers \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    harfbuzz-dev \
    fribidi-dev \
    libimagequant-dev \
    libxcb-dev \
    libpng-dev \
    && rm -rf /var/cache/apk/*

# =============================================================================
# CONFIGURACIÓN DE USUARIO
# =============================================================================
# Crear usuario no-root por seguridad
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# =============================================================================
# CONFIGURACIÓN DE DIRECTORIOS
# =============================================================================
# Crear directorios de trabajo
WORKDIR /app

# Crear directorios para logs y archivos estáticos
RUN mkdir -p /var/log/registro_ajustes \
    /var/run/registro_ajustes \
    /app/staticfiles \
    /app/media \
    && chown -R appuser:appgroup /var/log/registro_ajustes \
    && chown -R appuser:appgroup /var/run/registro_ajustes \
    && chown -R appuser:appgroup /app

# =============================================================================
# INSTALACIÓN DE DEPENDENCIAS PYTHON
# =============================================================================
# Copiar requirements primero para aprovechar el cache de Docker
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

# =============================================================================
# COPIA DEL CÓDIGO FUENTE
# =============================================================================
# Copiar código fuente
COPY . /app/

# Cambiar propietario de archivos
RUN chown -R appuser:appgroup /app

# =============================================================================
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS
# =============================================================================
# Cambiar a usuario no-root
USER appuser

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput --settings=registro_ajustes.settings_production

# =============================================================================
# CONFIGURACIÓN DE SALUD Y PUERTOS
# =============================================================================
# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python manage.py check --deploy || exit 1

# =============================================================================
# COMANDO DE INICIO
# =============================================================================
# Comando por defecto
CMD ["gunicorn", "--config", "gunicorn.conf.py", "registro_ajustes.wsgi:application"]