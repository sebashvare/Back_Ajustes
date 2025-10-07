# 📋 API Endpoints para Frontend Svelte

## 🔗 Base URL
```
http://127.0.0.1:8000
```

## 🔐 Autenticación

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "admin@ejemplo.com",
  "password": "admin123"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "admin@ejemplo.com",
    "name": "Administrador Sistema",
    "role": "admin"
  }
}
```

### Perfil Usuario
```http
GET /auth/profile
Authorization: Bearer {access_token}
```

### Logout
```http
POST /auth/logout
Authorization: Bearer {access_token}

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 📊 Registros de Ajustes

### Obtener Registros (con paginación)
```http
GET /api/registros/
GET /api/registros/?page=1&page_size=10
```

**Respuesta:**
```json
{
  "registros": [
    {
      "id": 1,
      "id_cuenta": "CTA-001-2024",
      "id_acuerdo_servicio": "AS-001-2024",
      "id_cargo_facturable": "CF-001-2024",
      "fecha_ajuste": "2025-09-26",
      "asesor_que_ajusto": "María González",
      "valor_ajustado": "150000.00",
      "justificacion": "Cliente reportó diferencia...",
      "created_at": "2025-10-01T14:02:21Z",
      "updated_at": "2025-10-01T14:02:21Z"
    }
  ],
  "total": 5,
  "count": 5,
  "next": null,
  "previous": null,
  "page_size": 10,
  "total_pages": 1
}
```

### Filtros Disponibles
```http
GET /api/registros/?search=CTA-001
GET /api/registros/?fecha_desde=2025-01-01&fecha_hasta=2025-12-31
GET /api/registros/?asesor=María
GET /api/registros/?cuenta=CTA-001
```

### Crear Registro
```http
POST /api/registros/
Content-Type: application/json

{
  "id_cuenta": "CTA-006-2025",
  "id_acuerdo_servicio": "AS-006-2025",
  "id_cargo_facturable": "CF-006-2025",
  "fecha_ajuste": "2025-10-01",
  "asesor_que_ajusto": "Juan Pérez",
  "valor_ajustado": "-250000.00",
  "justificacion": "Ajuste por diferencia detectada en auditoría interna"
}
```

### Obtener Registro Específico
```http
GET /api/registros/{id}/
```

### Actualizar Registro
```http
PUT /api/registros/{id}/
PATCH /api/registros/{id}/
```

### Eliminar Registro
```http
DELETE /api/registros/{id}/
```

## 📈 Endpoints de Datos

### Estadísticas
```http
GET /api/registros/stats/
```

**Respuesta:**
```json
{
  "total_registros": 5,
  "total_valor": 750000.00,
  "promedio_valor": 150000.00
}
```

### Lista de Asesores
```http
GET /api/registros/asesores/
```

**Respuesta:**
```json
{
  "asesores": [
    "María González",
    "Carlos Rodríguez",
    "Ana Martínez",
    "Luis Torres",
    "Patricia Vega"
  ]
}
```

### Lista de Cuentas
```http
GET /api/registros/cuentas/
```

**Respuesta:**
```json
{
  "cuentas": [
    "CTA-001-2024",
    "CTA-002-2024",
    "CTA-003-2024",
    "CTA-004-2024",
    "CTA-005-2024"
  ]
}
```

## 👥 Usuarios

### Obtener Usuarios
```http
GET /api/users/
```

### Usuario Actual
```http
GET /api/users/me/
```

## 🎯 Campos del Modelo RegistroAjuste

Los campos del modelo están exactamente como los espera el frontend:

- `id` (auto-generado)
- `id_cuenta` (string)
- `id_acuerdo_servicio` (string)  
- `id_cargo_facturable` (string)
- `fecha_ajuste` (date)
- `asesor_que_ajusto` (string)
- `valor_ajustado` (decimal)
- `justificacion` (text)
- `created_at` (datetime, auto)
- `updated_at` (datetime, auto)

## 🚀 Estado del Servidor

✅ Servidor corriendo en: `http://127.0.0.1:8000`
✅ Base de datos configurada con datos de ejemplo
✅ Autenticación JWT configurada
✅ APIs compatibles con la estructura del frontend Svelte
✅ Sin necesidad de cambios en el frontend - solo las URLs

## 📝 Datos de Prueba

Usuario de prueba creado:
- **Email:** admin@ejemplo.com
- **Password:** admin123
- **Rol:** admin

Se crearon 5 registros de ejemplo con datos realistas para probar el frontend.

---

**¡El backend está listo y completamente compatible con el frontend Svelte! 🎉**