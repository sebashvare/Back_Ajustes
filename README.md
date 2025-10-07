# 🏦 Sistema de Registro de Ajustes Financieros - Backend

> **API REST para gestión integral de ajustes contables y financieros**  
> Backend desarrollado en Dj    "asesor_que_ajusto": "María González",
    "valor_ajustado": "-150000.00",
    "justificacion": "Cliente reportó diferencia en facturación vs servicios recibidos", 5.2 compatible con frontend Svelte

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.16-orange.svg)](https://django-rest-framework.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 ¿Qué es este sistema?

El **Sistema de Registro de Ajustes** es una aplicación empresarial diseñada para gestionar y controlar los ajustes financieros y contables dentro de una organización. Permite a los usuarios registrar, validar y hacer seguimiento a modificaciones en cuentas contables, acuerdos de servicio y cargos facturables.

### 🎯 **Casos de Uso Principales**

- **Corrección de Facturas**: Ajustar valores incorrectos en facturación
- **Descuentos Aplicados**: Registrar descuentos no aplicados automáticamente
- **Correcciones Contables**: Ajustar errores en cuentas contables
- **Reversiones**: Anular o modificar transacciones previas
- **Auditoría Financiera**: Mantener trazabilidad de todos los cambios

### 💼 **Funcionalidades del Negocio**

- ✅ **Registro de Ajustes**: Captura detallada de modificaciones financieras
- ✅ **Validaciones de Negocio**: Reglas automáticas según políticas empresariales
- ✅ **Trazabilidad Completa**: Auditoría de quién, cuándo y por qué se hizo cada ajuste
- ✅ **Filtros Avanzados**: Búsqueda por fechas, asesores, cuentas y montos
- ✅ **Estadísticas**: Reportes de valores totales, promedios y tendencias
- ✅ **Control de Acceso**: Autenticación segura con roles y permisos

## 🏗️ **Arquitectura del Sistema**

### **Modelo de Datos Principal**

El sistema se centra en el modelo `RegistroAjuste` que captura:

```python
RegistroAjuste:
├── id_cuenta              # Cuenta contable afectada
├── id_acuerdo_servicio    # Acuerdo de servicio relacionado
├── id_cargo_facturable    # Cargo específico a ajustar
├── fecha_ajuste           # Cuándo se realiza el ajuste
├── asesor_que_ajusto      # Responsable del ajuste
├── valor_ajustado         # Monto del ajuste (positivo/negativo)
├── justificacion          # Justificación obligatoria
└── metadatos_auditoria    # Timestamps y usuario que creó
```

### **Reglas de Negocio Implementadas**

1. **Validación de Fechas**: No se permiten ajustes con fecha futura
2. **Montos Válidos**: Los valores deben ser diferentes de cero
3. **Justificación Obligatoria**: Mínimo 10 caracteres, 50 para montos altos
4. **Límites de Ajuste**: Configurables según políticas empresariales
5. **Auditoría Automática**: Registro automático de creación y modificación

## ✨ Características Técnicas

- 🔐 **Autenticación JWT** - Sistema seguro con tokens de acceso y refresco
- 📊 **API REST Completa** - Endpoints CRUD con paginación y filtros
- 🔍 **Búsqueda Inteligente** - Filtros por múltiples criterios
- 📈 **Dashboard de Estadísticas** - Métricas agregadas en tiempo real
- 🛡️ **Validaciones Robustas** - Reglas de negocio a nivel de modelo y API
- 📦 **Deployment Ready** - Docker y configuraciones para producción
- 🎯 **Frontend Agnostic** - Compatible con cualquier cliente (Svelte, React, Vue)

## 🚀 Inicio Rápido

### Prerequisitos

- Python 3.11+
- pip o conda
- Git

### Instalación

1. **Clonar repositorio**
   ```bash
   git clone https://github.com/sebashvare/Back_Ajustes.git
   cd Back_Ajustes
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env según tus necesidades
   ```

5. **Preparar base de datos**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python crear_datos_frontend.py  # Datos de ejemplo
   ```

6. **Iniciar servidor**
   ```bash
   python manage.py runserver
   ```

   🌐 **Acceder a**: `http://127.0.0.1:8000`

## 📡 API Principales

### 🔐 Autenticación
```bash
POST /auth/login          # Iniciar sesión
GET  /auth/profile        # Perfil del usuario
POST /auth/logout         # Cerrar sesión
```

### 📊 Gestión de Ajustes
```bash
GET    /api/registros/           # Lista paginada
POST   /api/registros/           # Crear nuevo ajuste
GET    /api/registros/{id}/      # Detalle específico
PUT    /api/registros/{id}/      # Actualizar ajuste
DELETE /api/registros/{id}/      # Eliminar ajuste
GET    /api/registros/stats/     # Estadísticas generales
```

### � Filtros Disponibles
```bash
# Búsqueda por texto en múltiples campos
GET /api/registros/?search=CTA-001

# Filtro por rango de fechas
GET /api/registros/?fecha_desde=2025-01-01&fecha_hasta=2025-12-31

# Filtro por asesor responsable
GET /api/registros/?asesor=Maria

# Paginación personalizada
GET /api/registros/?page=1&page_size=20
```

## 📋 Ejemplo de Registro

### Crear un Ajuste
```json
POST /api/registros/
{
  "id_cuenta": "CTA-001-2025",
  "id_acuerdo_servicio": "AS-PREMIUM-001",
  "id_cargo_facturable": "CF-CONSULTORIA",
  "fecha_ajuste": "2025-10-02",
  "asesor_que_ajusto": "María González",
  "valor_ajustado": "150000.00",
  "justificacion": "Ajuste por diferencia entre servicios facturados vs servicios efectivamente prestados según acuerdo comercial"
}
```

### Respuesta del Sistema
```json
{
  "id": 15,
  "id_cuenta": "CTA-001-2025",
  "id_acuerdo_servicio": "AS-PREMIUM-001",
  "id_cargo_facturable": "CF-CONSULTORIA",
  "fecha_ajuste": "2025-10-02",
  "asesor_que_ajusto": "María González",
  "valor_ajustado": "150000.00",
  "justificacion": "Ajuste por diferencia entre servicios facturados...",
  "created_at": "2025-10-02T10:30:00Z",
  "updated_at": "2025-10-02T10:30:00Z",
  "valor_ajustado_display": "$150,000.00",
  "es_ajuste_alto_valor": true,
  "_metadata": {
    "version": "1.0.0",
    "requires_approval": true
  }
}
```

## �️ Seguridad y Validaciones

### Validaciones Automáticas
- **Fechas**: No futuras, formato válido
- **Montos**: Mayor a cero, dentro de límites configurables
- **Justificación**: Longitud mínima según el monto del ajuste
- **Usuarios**: Autenticación obligatoria para todas las operaciones

### Configuraciones de Seguridad
- Headers de seguridad para producción
- Rate limiting configurado
- Validación de CORS para frontend
- Tokens JWT con expiración automática

## 📊 Dashboard y Estadísticas

El sistema proporciona métricas en tiempo real:

```json
GET /api/registros/stats/
{
  "total_registros": 45,
  "total_valor": "2150000.00",
  "promedio_valor": "47777.78",
  "asesores_activos": 8,
  "ajustes_ultimo_mes": 12
}
```

## 🏭 Deployment para Producción

### Con Docker
```bash
# Configurar variables de producción
cp .env.production .env

# Deployment automático
./deploy.sh deploy
```

### Manual
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos PostgreSQL
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic

# Iniciar con Gunicorn
gunicorn registro_ajustes.wsgi:application
```

## 🤝 Integración con Frontend

Este backend está **optimizado para trabajar con frontend Svelte**, pero es compatible con cualquier tecnología frontend que consuma APIs REST.

### Ejemplo de Integración (JavaScript)
```javascript
// Autenticación
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'usuario@empresa.com',
    password: 'password123'
  })
});

const { access_token } = await response.json();

// Obtener registros
const registros = await fetch('http://localhost:8000/api/registros/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

## 📞 Soporte y Documentación

- **Repositorio**: [https://github.com/sebashvare/Back_Ajustes](https://github.com/sebashvare/Back_Ajustes)
- **Documentación API**: Ver archivo `API_ENDPOINTS.md`
- **Issues**: Reportar en GitHub Issues
- **Contribuciones**: Pull Requests bienvenidos

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**Desarrollado con ❤️ para optimizar la gestión de ajustes financieros empresariales**

## 🚀 Inicio Rápido

### Prerequisitos

- Python 3.11+
- Conda o virtualenv
- PostgreSQL (opcional, usa SQLite por defecto)
- Docker y Docker Compose (para producción)

### Instalación Local

1. **Clonar y configurar entorno**
   ```bash
   git clone <repository-url>
   cd Registro_Ajustes_Back
   
   # Crear entorno conda
   conda create -n Registro python=3.11
   conda activate Registro
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

4. **Ejecutar migraciones y crear datos**
   ```bash
   python manage.py migrate
   python crear_datos_frontend.py
   ```

5. **Iniciar servidor de desarrollo**
   ```bash
   python manage.py runserver 8000
   ```

### Deployment con Docker

1. **Configurar producción**
   ```bash
   cp .env.production .env
   # Configurar variables de producción en .env
   ```

2. **Deployment automático**
   ```bash
   ./deploy.sh deploy
   ```

3. **Otros comandos útiles**
   ```bash
   ./deploy.sh status    # Ver estado de servicios
   ./deploy.sh logs      # Ver logs en tiempo real
   ./deploy.sh backup    # Crear backup de BD
   ./deploy.sh rollback  # Rollback en caso de problemas
   ```

## 📡 API Endpoints

### 🔐 Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/login` | Login con email/password |
| POST | `/auth/logout` | Logout seguro |
| GET | `/auth/profile` | Perfil del usuario actual |

### 📊 Registros de Ajustes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/registros/` | Lista paginada de registros |
| POST | `/api/registros/` | Crear nuevo registro |
| GET | `/api/registros/{id}/` | Obtener registro específico |
| PUT/PATCH | `/api/registros/{id}/` | Actualizar registro |
| DELETE | `/api/registros/{id}/` | Eliminar registro |
| GET | `/api/registros/stats/` | Estadísticas agregadas |
| GET | `/api/registros/asesores/` | Lista de asesores |
| GET | `/api/registros/cuentas/` | Lista de cuentas |

## 📋 Estructura de Datos

### Modelo RegistroAjuste

```json
{
  "id": 1,
  "id_cuenta": "CTA-001-2024",
  "id_acuerdo_servicio": "AS-001-2024",
  "id_cargo_facturable": "CF-001-2024",
  "fecha_ajuste": "2025-10-01",
  "asesor_que_ajusto": "María González",
  "valor_ajustado": "150000.00",
  "justificacion": "Justificación del ajuste",
  "created_at": "2025-10-01T14:02:21Z",
  "updated_at": "2025-10-01T14:02:21Z"
}
```

## 🚀 Estado del Proyecto

✅ **Servidor corriendo**: `http://127.0.0.1:8000`  
✅ **Base de datos configurada** con datos de ejemplo  
✅ **Autenticación JWT** completamente funcional  
✅ **APIs compatibles** con frontend Svelte  
✅ **Sin cambios necesarios** en el frontend - solo URLs  

### 📝 Datos de Prueba

**Usuario de prueba:**
- **Email:** admin@ejemplo.com
- **Password:** admin123
- **Rol:** admin

**6 registros de ejemplo** creados con datos realistas para testing.

### 🔍 Ejemplos de Uso

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@ejemplo.com", "password": "admin123"}'
```

**Obtener registros:**
```bash
curl -X GET http://127.0.0.1:8000/api/registros/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Crear registro:**
```bash
curl -X POST http://127.0.0.1:8000/api/registros/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_cuenta": "CTA-NEW-2025",
    "id_acuerdo_servicio": "AS-NEW-2025",
    "id_cargo_facturable": "CF-NEW-2025",
    "fecha_ajuste": "2025-10-01",
    "asesor_que_ajusto": "Test User",
    "valor_ajustado": "75000.00",
    "justificacion": "Ajuste de prueba desde API"
  }'
```

## ⚙️ Configuración

### Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DEBUG` | Modo debug | `False` |
| `SECRET_KEY` | Clave secreta Django | `your-secret-key` |
| `DATABASE_URL` | URL de base de datos | `postgresql://user:pass@host:5432/db` |
| `ALLOWED_HOSTS` | Hosts permitidos | `domain.com,www.domain.com` |
| `CORS_ALLOWED_ORIGINS` | Orígenes CORS | `https://domain.com` |

### Configuraciones de Negocio

- **Valor máximo de ajuste**: $10,000,000
- **Requiere aprobación arriba de**: $100,000
- **Auto-aprobación debajo de**: $10,000

## 🏗️ Arquitectura

### Stack Tecnológico

- **Framework**: Django 5.2
- **API**: Django REST Framework 3.16
- **Autenticación**: Simple JWT
- **Base de Datos**: PostgreSQL / SQLite
- **Cache**: Redis
- **Servidor**: Gunicorn + Nginx
- **Containerización**: Docker + Docker Compose

### Estructura del Proyecto

```
Registro_Ajustes_Back/
├── 📁 adjustments/           # App principal de ajustes
├── 📁 authentication/        # App de autenticación
├── 📁 analytics/            # App de analytics
├── 📁 registro_ajustes/     # Configuración del proyecto
├── 📄 requirements.txt       # Dependencias Python
├── 📄 Dockerfile           # Imagen Docker
├── 📄 docker-compose.yml   # Orquestación de servicios
├── 📄 deploy.sh            # Script de deployment
└── 📄 README.md            # Este archivo
```

## 🔒 Seguridad

### Validaciones de Negocio

- **Fecha de ajuste**: No puede ser futura
- **Valor**: Debe ser mayor a cero y dentro de límites
- **Justificación**: Mínimo 10 caracteres
- **Integridad**: Validaciones a nivel de modelo y serializer

### Configuraciones de Producción

- ✅ HTTPS forzado
- ✅ Cookies seguras
- ✅ Headers de seguridad
- ✅ Rate limiting
- ✅ Usuario no-root en Docker

## 📞 Soporte

Para más información, consultar:
- **Documentación completa**: `API_ENDPOINTS.md`
- **Email**: admin@ejemplo.com

---

**¡El backend está listo y completamente compatible con el frontend Svelte! 🎉**