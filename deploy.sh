#!/bin/bash

# =============================================================================
# SCRIPT DE DEPLOYMENT - SISTEMA DE REGISTRO DE AJUSTES
# =============================================================================
# Script automatizado para deployment en producción
# Incluye validaciones, backups y rollback automático

set -e  # Exit on any error

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
PROJECT_NAME="registro_ajustes"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.production"
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Verificando prerequisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker no está instalado"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose no está instalado"
        exit 1
    fi
    
    # Verificar archivo de ambiente
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Archivo de ambiente $ENV_FILE no encontrado"
        log_info "Copiando template desde .env.production"
        cp .env.production $ENV_FILE
        log_warning "IMPORTANTE: Configurar variables en $ENV_FILE antes de continuar"
        exit 1
    fi
    
    log_success "Prerequisites verificados"
}

create_backup() {
    log_info "Creando backup de la base de datos..."
    
    mkdir -p $BACKUP_DIR
    
    # Backup de la base de datos si el contenedor existe
    if docker ps -a | grep -q "${PROJECT_NAME}_db"; then
        docker exec ${PROJECT_NAME}_db pg_dump -U registro_user registro_ajustes_prod > "$BACKUP_DIR/database_backup.sql"
        log_success "Backup de base de datos creado en $BACKUP_DIR"
    else
        log_warning "Contenedor de base de datos no encontrado, saltando backup"
    fi
}

run_tests() {
    log_info "Ejecutando tests..."
    
    # Build test image
    docker build -t ${PROJECT_NAME}_test -f Dockerfile.test . || {
        log_error "Falló la construcción de imagen de test"
        return 1
    }
    
    # Run tests
    docker run --rm ${PROJECT_NAME}_test python manage.py test || {
        log_error "Tests fallaron"
        return 1
    }
    
    log_success "Tests pasaron exitosamente"
}

deploy() {
    log_info "Iniciando deployment..."
    
    # Build and start containers
    docker-compose -f $DOCKER_COMPOSE_FILE --env-file $ENV_FILE build
    docker-compose -f $DOCKER_COMPOSE_FILE --env-file $ENV_FILE up -d
    
    # Wait for services to be ready
    log_info "Esperando que los servicios estén listos..."
    sleep 30
    
    # Run migrations
    log_info "Ejecutando migraciones..."
    docker-compose -f $DOCKER_COMPOSE_FILE exec web python manage.py migrate --settings=registro_ajustes.settings_production
    
    # Collect static files
    log_info "Recopilando archivos estáticos..."
    docker-compose -f $DOCKER_COMPOSE_FILE exec web python manage.py collectstatic --noinput --settings=registro_ajustes.settings_production
    
    # Health check
    log_info "Verificando salud de la aplicación..."
    if docker-compose -f $DOCKER_COMPOSE_FILE exec web python manage.py check --deploy --settings=registro_ajustes.settings_production; then
        log_success "Deployment completado exitosamente"
    else
        log_error "Health check falló"
        rollback
        exit 1
    fi
}

rollback() {
    log_warning "Iniciando rollback..."
    
    # Stop current containers
    docker-compose -f $DOCKER_COMPOSE_FILE down
    
    # Restore database if backup exists
    if [ -f "$BACKUP_DIR/database_backup.sql" ]; then
        log_info "Restaurando backup de base de datos..."
        docker-compose -f $DOCKER_COMPOSE_FILE up -d db
        sleep 10
        docker exec -i ${PROJECT_NAME}_db psql -U registro_user -d registro_ajustes_prod < "$BACKUP_DIR/database_backup.sql"
    fi
    
    log_warning "Rollback completado"
}

cleanup() {
    log_info "Limpiando recursos no utilizados..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (careful with this in production)
    # docker volume prune -f
    
    log_success "Cleanup completado"
}

show_logs() {
    docker-compose -f $DOCKER_COMPOSE_FILE logs -f --tail=100
}

show_status() {
    log_info "Estado de los servicios:"
    docker-compose -f $DOCKER_COMPOSE_FILE ps
    
    log_info "Uso de recursos:"
    docker stats --no-stream
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            create_backup
            # run_tests  # Uncomment when tests are ready
            deploy
            cleanup
            ;;
        "rollback")
            rollback
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "backup")
            create_backup
            ;;
        "test")
            run_tests
            ;;
        "help"|*)
            echo "Uso: $0 {deploy|rollback|logs|status|backup|test|help}"
            echo ""
            echo "Comandos:"
            echo "  deploy   - Deployment completo (default)"
            echo "  rollback - Rollback a estado anterior"
            echo "  logs     - Mostrar logs en tiempo real"
            echo "  status   - Mostrar estado de servicios"
            echo "  backup   - Crear backup de base de datos"
            echo "  test     - Ejecutar tests"
            echo "  help     - Mostrar esta ayuda"
            ;;
    esac
}

# =============================================================================
# EJECUCIÓN
# =============================================================================

main "$@"