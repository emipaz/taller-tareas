# 🌐 Sistema Web y API REST de Gestión de Tareas

Sistema completo con **doble arquitectura**:
- 🖥️ **Interfaz Web** con Jinja2 + HTMX para aplicación web moderna
- 🔌 **API REST** con FastAPI + JWT para integraciones y clientes externos

Ambas capas comparten la misma lógica de negocio y autenticación JWT.

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** 0.104+ - Framework web moderno con validación automática
- **Uvicorn** - Servidor ASGI de alto rendimiento
- **Pydantic** - Validación de datos con type hints
- **httpx** - Cliente HTTP para llamadas internas (TestClient)

### Frontend Web
- **Jinja2** 3.0+ - Motor de plantillas server-side
- **HTMX** 1.9.2 - Interactividad HTML sin JavaScript complejo
- **CSS3** - Estilos modernos con variables y grid/flexbox

### Autenticación & Seguridad
- **PyJWT** - Tokens JWT con algoritmo RS256 (RSA + SHA256)
- **cryptography** - Generación de llaves RSA para JWT
- **passlib[bcrypt]** - Hashing seguro de contraseñas
- **python-multipart** - Manejo de forms multipart

### Testing
- **pytest** - Framework de testing
- **pytest-asyncio** - Tests asíncronos
- **TestClient** (FastAPI) - Tests de integración

## 🚀 Inicio Rápido

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar el Sistema Completo

```bash
# Desde el directorio raíz del proyecto
python api.py

# O directamente con uvicorn
uvicorn api-rest.api_rest:app --reload --host 0.0.0.0 --port 8000
```

### Acceder al Sistema

#### 🖥️ Interfaz Web
- **Landing/Login**: http://localhost:8000/
- **Dashboard**: http://localhost:8000/dashboard
- **Admin Panel**: http://localhost:8000/admin/users
- **Estadísticas**: http://localhost:8000/admin/stats

#### 📚 Documentación API
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health check**: http://localhost:8000/api/health

## 📋 Endpoints Disponibles

### 🖥️ Interfaz Web (Jinja2 + HTMX)

#### Páginas HTML
```
GET  /                              # Landing page con login
GET  /dashboard                     # Dashboard principal (🔐 auth)
GET  /tareas/lista                  # Lista de tareas filtrable (🔐 auth)
GET  /tareas/detalle/{nombre}       # Detalle de tarea (🔐 auth)
GET  /admin/users                   # Panel administración usuarios (🔐 admin)
GET  /admin/stats                   # Estadísticas del sistema (🔐 admin)
```

#### Formularios y Acciones Web
```
POST /login                         # Login con cookies HttpOnly
POST /set-password                  # Establecer contraseña inicial
POST /change-password               # Cambiar contraseña (🔐 auth)
GET  /logout                        # Cerrar sesión
POST /admin/create-user             # Crear usuario (🔐 admin)
POST /admin/reset-password          # Resetear contraseña (🔐 admin)
POST /admin/delete-user             # Eliminar usuario (🔐 admin)
POST /admin/create-task             # Crear tarea desde admin (🔐 admin)
```

#### Acciones de Tareas (HTMX)
```
POST   /web/tareas/comentario       # Agregar comentario (🔐 auth)
POST   /web/tareas/asignar          # Asignar usuario a tarea (🔐 auth)
POST   /web/tareas/finalizar        # Finalizar tarea (🔐 auth)
PUT    /web/tareas/{nombre}/reactivar  # Reactivar tarea (🔐 admin)
DELETE /web/tareas/{nombre}         # Eliminar tarea finalizada (🔐 admin)
```

### 🔌 API REST (JSON)

#### Sistema
```
GET  /api                   # Información de la API
GET  /api/health            # Health check
GET  /stats                 # Estadísticas del sistema (🔐 auth)
```

#### Usuarios
```
GET    /usuarios            # Listar usuarios con paginación (🔐 auth)
GET    /usuarios/{nombre}   # Obtener usuario específico (🔐 auth)
POST   /usuarios            # Crear usuario (🔐 auth)
POST   /usuarios/admin      # Crear primer admin (público, solo si no hay admins)
DELETE /usuarios/{nombre}   # Eliminar usuario (🔐 admin)
```

#### Autenticación
```
POST /auth/login            # Login → access_token + refresh_token
POST /auth/refresh          # Renovar access_token con refresh_token
POST /auth/logout           # Invalidar tokens (🔐 auth)
GET  /auth/me               # Información usuario actual (🔐 auth)
POST /auth/set-password     # Establecer contraseña inicial
POST /auth/change-password  # Cambiar contraseña (🔐 auth)
POST /auth/reset-password   # Resetear contraseña (🔐 admin)
```

#### Tareas
```
GET    /tareas                     # Listar todas las tareas (🔐 auth)
GET    /tareas/{nombre}            # Obtener tarea específica (🔐 auth)
GET    /tareas/usuario/{nombre}    # Tareas asignadas a usuario (🔐 auth)
POST   /tareas                     # Crear nueva tarea (🔐 auth)
POST   /tareas/asignar             # Asignar usuario a tarea (🔐 auth)
POST   /tareas/finalizar           # Finalizar tarea (🔐 auth)
POST   /tareas/comentario          # Agregar comentario (🔐 auth)
PUT    /tareas/{nombre}/reactivar  # Reactivar tarea finalizada (🔐 admin)
DELETE /tareas/{nombre}            # Eliminar tarea finalizada (🔐 admin)
```

**Leyenda:**
- 🔐 auth = Requiere token JWT válido
- 🔐 admin = Requiere token JWT de administrador

## 🏗️ Arquitectura del Sistema

### Flujo de Autenticación

#### Interfaz Web (Cookies HttpOnly)
```
1. Usuario → POST /login (form)
2. web.py valida credenciales → llama API /auth/login
3. API retorna tokens JWT
4. web.py establece cookies HttpOnly:
   - access_token (30 min)
   - refresh_token (7 días)
5. Navegador envía cookies automáticamente
6. web.py extrae token → llama API con Authorization header
7. API valida JWT → retorna datos
8. web.py renderiza Jinja2 → HTML al cliente
```

#### API REST (Authorization Headers)
```
1. Cliente → POST /auth/login (JSON)
2. API valida credenciales
3. API retorna: {access_token, refresh_token, token_type, expires_in}
4. Cliente guarda tokens
5. Cliente → GET /tareas con header:
   Authorization: Bearer <access_token>
6. API valida JWT → retorna JSON
```

### Patrón de Arquitectura

```
┌─────────────────┐
│   Navegador     │
│  (HTML/HTMX)    │
└────────┬────────┘
         │ cookies
         ↓
┌─────────────────┐      ┌──────────────┐
│    web.py       │─────→│  api_rest.py │
│  (Jinja2+HTMX)  │ http │  (FastAPI)   │
│  Rutas: /,      │←─────│  Rutas: /api,│
│  /dashboard,    │ json │  /tareas,    │
│  /web/*         │      │  /auth/*     │
└─────────────────┘      └──────┬───────┘
         │                       │
         │  TestClient (httpx)   │ jwt_auth.py
         │                       │
         └───────────┬───────────┘
                     ↓
         ┌──────────────────────┐
         │   GestorSistema      │
         │   (core/*)           │
         └──────────────────────┘
```

### Tecnologías Clave

#### FastAPI + Uvicorn
- **ASGI** server de alto rendimiento
- **Validación automática** con Pydantic
- **Docs automáticas** (OpenAPI/Swagger)
- **Async/await** support nativo

#### Jinja2 Templates
- **Server-side rendering** para SEO y performance
- **Template inheritance** (base templates)
- **Filters**: `|upper`, `|lower`, `|join`, `|length`
- **Control structures**: `{% if %}`, `{% for %}`, `{% include %}`
- **Seguro por defecto** (auto-escaping HTML)

#### HTMX 1.9.2
- **hx-get**, **hx-post**, **hx-put**, **hx-delete** - Requests AJAX
- **hx-target** - Dónde insertar respuesta HTML
- **hx-swap** - Cómo insertar (innerHTML, outerHTML, beforeend, etc.)
- **hx-trigger** - Eventos que disparan request
- **hx-confirm** - Confirmación antes de acción
- Sin necesidad de escribir JavaScript

#### httpx (TestClient)
- Cliente HTTP basado en httpx
- Usado por web.py para llamar api_rest.py
- Maneja cookies automáticamente
- Extrae token de cookies → agrega Authorization header

#### PyJWT con RS256
- **Algoritmo asimétrico** RSA + SHA256
- **Llaves públicas/privadas** generadas automáticamente
- **Access tokens** cortos (30 min)
- **Refresh tokens** largos (7 días)
- **Claims**: sub, exp, iat, tipo_usuario

#### Passlib + Bcrypt
- **Hashing seguro** de contraseñas
- **Salt automático** por usuario
- **Verificación constante** (timing-safe)
- Nunca almacena contraseñas en texto plano

## 🧪 Pruebas

### Cliente de Pruebas Automático

Para probar la API rápidamente:

```bash
python test_api_client.py
```

Selecciona:
- **1** para demo automática completa
- **2** para demo interactiva

### Usando curl

#### Crear administrador
```bash
curl -X POST "http://localhost:8000/usuarios/admin" \
     -H "Content-Type: application/json" \
     -d '{"nombre": "admin", "contraseña": "admin123"}'
```

#### Crear usuario
```bash
curl -X POST "http://localhost:8000/usuarios" \
     -H "Content-Type: application/json" \
     -d '{"nombre": "juan"}'
```

#### Establecer contraseña
```bash
curl -X POST "http://localhost:8000/auth/set-password" \
     -H "Content-Type: application/json" \
     -d '{"nombre": "juan", "contraseña": "juan123"}'
```

#### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"nombre": "juan", "contraseña": "juan123"}'
```

#### Crear tarea
```bash
curl -X POST "http://localhost:8000/tareas" \
     -H "Content-Type: application/json" \
     -d '{"nombre": "Mi Tarea", "descripcion": "Descripción de la tarea"}'
```

#### Asignar tarea
```bash
curl -X POST "http://localhost:8000/tareas/asignar" \
     -H "Content-Type: application/json" \
     -d '{"nombre_tarea": "Mi Tarea", "nombre_usuario": "juan"}'
```

### Usando Python requests

```python
import requests

base_url = "http://localhost:8000"

# Health check
response = requests.get(f"{base_url}/health")
print(response.json())

# Crear administrador
admin_data = {"nombre": "admin", "contraseña": "admin123"}
response = requests.post(f"{base_url}/usuarios/admin", json=admin_data)
print(response.json())

# Listar usuarios
response = requests.get(f"{base_url}/usuarios")
print(response.json())

# Crear tarea
tarea_data = {"nombre": "Nueva Tarea", "descripcion": "Descripción detallada"}
response = requests.post(f"{base_url}/tareas", json=tarea_data)
print(response.json())
```

## 🔧 Esquemas de Datos

### Usuario
```json
{
  "nombre": "string",
  "rol": "user|admin",
  "tiene_password": true
}
```

### Tarea
```json
{
  "nombre": "string",
  "descripcion": "string",
  "estado": "pendiente|finalizada",
  "fecha_creacion": "2025-01-01 12:00:00",
  "usuarios_asignados": ["usuario1", "usuario2"],
  "comentarios": [
    {
      "comentario": "texto del comentario",
      "usuario": "nombre_usuario",
      "fecha": "2025-01-01 12:00:00"
    }
  ],
  "esta_finalizada": false
}
```

### Respuesta Base
```json
{
  "success": true,
  "message": "Operación exitosa"
}
```

### Respuesta de Error
```json
{
  "success": false,
  "message": "Descripción del error",
  "error_code": "CODIGO_ERROR"
}
```

## 📊 Estadísticas

El endpoint `/stats` devuelve:

```json
{
  "usuarios": {
    "total": 10,
    "admins": 2,
    "users": 8,
    "sin_password": 3
  },
  "tareas": {
    "total": 15,
    "pendientes": 10,
    "finalizadas": 5,
    "sin_asignar": 2
  }
}
```

## 🔒 Seguridad

- Las contraseñas se almacenan hasheadas con bcrypt
- Validación de entrada con Pydantic
- Manejo de errores consistente
- CORS configurado (ajustar en producción)

## 🛠️ Características

- ✅ **Documentación automática** con Swagger/OpenAPI
- ✅ **Validación automática** de datos de entrada
- ✅ **Manejo de errores** consistente
- ✅ **Respuestas tipadas** con Pydantic
- ✅ **CORS** habilitado
- ✅ **Health check** endpoint
- ✅ **Cliente de pruebas** incluido

## 🔄 Próximas Mejoras

- [ ] Autenticación JWT
- [ ] Paginación en listados
- [ ] Filtros avanzados
- [ ] Rate limiting
- [ ] Logging estructurado
- [ ] Caché con Redis
- [ ] WebSockets para notificaciones en tiempo real

## 📝 Notas de Desarrollo

- Construida con **FastAPI** (framework moderno y rápido)
- Validación con **Pydantic** (type hints automáticos)
- Servidor **Uvicorn** con recarga automática
- Reutiliza la lógica de negocio existente en `GestorSistema`
- Mantiene compatibilidad con el sistema CLI existente