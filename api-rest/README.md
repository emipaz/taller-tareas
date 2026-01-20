# 🌐 API REST del Sistema de Gestión de Tareas

Implementación completa con **doble arquitectura**:
- 🖥️ **Interfaz Web** (`web.py`) - Jinja2 + HTMX + cookies HttpOnly
- 🔌 **API REST** (`api_rest.py`) - FastAPI + JWT + Authorization headers

## 📁 Estructura

```
api-rest/
├── __init__.py              # Módulo API REST
├── api_rest.py             # API REST (endpoints /api/, /tareas/, /auth/)
├── web.py                  # Interfaz Web (endpoints /, /dashboard, /web/*)
├── api_models.py           # Modelos Pydantic de validación
├── jwt_auth.py             # Sistema de autenticación JWT (RS256)
├── templates/              # Plantillas Jinja2
│   ├── index.html          # Landing page con login
│   ├── dashboard.html      # Dashboard principal
│   ├── admin_users.html    # Panel de administración
│   ├── set_password.html   # Establecer contraseña
│   └── _tareas_fragment.html # Fragmento HTMX de tareas
├── static/                 # Recursos estáticos
│   ├── main.css            # Estilos CSS
│   └── common.js           # JavaScript común
└── tests/                  # Tests automatizados
    ├── run_all_tests.py    # Ejecutor de todos los tests
    ├── test_app.py         # Tests de la aplicación
    ├── test_jwt_integration.py  # Tests JWT
    ├── test_jwt_unit.py    # Tests unitarios JWT
    ├── test_api_client.py  # Cliente de pruebas
    ├── test_api_endpoints_unit.py # Tests unitarios API
    └── test_api_endpoints.ipynb   # Notebook Jupyter
```

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** - Framework web ASGI moderno
- **Uvicorn** - Servidor ASGI de alto rendimiento
- **Pydantic** - Validación de datos con type hints
- **httpx** - Cliente HTTP (TestClient para llamadas internas)
- **python-multipart** - Manejo de formularios multipart

### Frontend Web
- **Jinja2** 3.0+ - Motor de plantillas server-side
- **HTMX** 1.9.2 - Interactividad sin JavaScript complejo
- **CSS3** - Variables CSS, Grid, Flexbox

### Seguridad
- **PyJWT[crypto]** - Tokens JWT con RS256
- **cryptography** - Generación de llaves RSA
- **passlib[bcrypt]** - Hashing de contraseñas
- **HttpOnly cookies** - Protección contra XSS

### Testing
- **pytest** + **pytest-asyncio**
- **TestClient** (FastAPI/httpx)

## 🚀 Inicio Rápido

### Ejecutar el Sistema

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

#### 📚 Documentación API
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## � Endpoints Disponibles

### 🖥️ Interfaz Web (Jinja2 + HTMX)

#### Páginas HTML (Renderizadas server-side)
```
GET  /                              # Landing page con formulario login
GET  /dashboard                     # Dashboard principal (🔐 auth)
GET  /tareas/lista                  # Lista de tareas filtrable (🔐 auth)
GET  /tareas/detalle/{nombre}       # Detalle completo de tarea (🔐 auth)
GET  /admin/users                   # Panel administración usuarios (🔐 admin)
GET  /admin/stats                   # Estadísticas del sistema (🔐 admin)
```

#### Formularios y Acciones
```
POST /login                         # Login (establece cookies HttpOnly)
POST /set-password                  # Primera contraseña
POST /change-password               # Cambiar contraseña (🔐 auth)
GET  /logout                        # Cerrar sesión (invalida tokens)
POST /admin/create-user             # Crear usuario (🔐 admin)
POST /admin/reset-password          # Resetear contraseña (🔐 admin)
POST /admin/delete-user             # Eliminar usuario (🔐 admin)
POST /admin/create-task             # Crear tarea (🔐 admin)
```

#### Acciones de Tareas (HTMX - retornan HTML fragments)
```
POST   /web/tareas/comentario         # Agregar comentario (🔐 auth)
POST   /web/tareas/asignar            # Asignar usuario (🔐 auth)
POST   /web/tareas/desasignar         # Quitar usuario (🔐 admin)
POST   /web/tareas/finalizar          # Finalizar tarea (🔐 auth)
PUT    /web/tareas/{nombre}/reactivar # Reactivar tarea (🔐 admin)
DELETE /web/tareas/{nombre}           # Eliminar tarea (🔐 admin)
```

### 🔌 API REST (JSON)

#### Sistema
```
GET  /api                   # Info de la API
GET  /api/health            # Health check
GET  /stats                 # Estadísticas (🔐 auth)
```

#### Usuarios
```
GET    /usuarios            # Listar con paginación (🔐 auth)
GET    /usuarios/{nombre}   # Usuario específico (🔐 auth)
POST   /usuarios            # Crear usuario (🔐 auth)
POST   /usuarios/admin      # Crear primer admin (público)
DELETE /usuarios/{nombre}   # Eliminar usuario (🔐 admin)
```

#### Autenticación JWT
```
POST /auth/login            # Login → tokens JWT
POST /auth/refresh          # Renovar access_token
POST /auth/logout           # Invalidar tokens (🔐 auth)
GET  /auth/me               # Usuario actual (🔐 auth)
POST /auth/set-password     # Primera contraseña
POST /auth/change-password  # Cambiar contraseña (🔐 auth)
POST /auth/reset-password   # Resetear contraseña (🔐 admin)
```

#### Tareas
```
GET    /tareas                     # Listar todas (🔐 auth)
GET    /tareas/{nombre}            # Tarea específica (🔐 auth)
GET    /tareas/usuario/{nombre}    # Tareas de usuario (🔐 auth)
POST   /tareas                     # Crear tarea (🔐 auth)
POST   /tareas/asignar             # Asignar usuario (🔐 auth)
POST   /tareas/desasignar          # Quitar usuario (🔐 admin)
POST   /tareas/finalizar           # Finalizar tarea (🔐 auth)
POST   /tareas/comentario          # Agregar comentario (🔐 auth)
PUT    /tareas/{nombre}/reactivar  # Reactivar (🔐 admin)
DELETE /tareas/{nombre}            # Eliminar (🔐 admin)
```

**Leyenda:**
- 🔐 auth = Token JWT válido requerido
- 🔐 admin = Token JWT de administrador requerido

## 🏗️ Arquitectura

### Flujo de Peticiones

#### Web (Cookies)
```
Browser → POST /login
  ↓
web.py → TestClient.post('/auth/login')
  ↓
api_rest.py → Valida credenciales
  ↓
api_rest.py → Retorna {access_token, refresh_token}
  ↓
web.py → Set-Cookie: access_token (HttpOnly)
  ↓
web.py → Renderiza dashboard.html
  ↓
Browser ← HTML + Cookies
```

#### API (Headers)
```
Client → POST /auth/login
  ↓
api_rest.py → Valida credenciales
  ↓
Client ← {access_token, refresh_token, expires_in}
  
Client → GET /tareas
         Authorization: Bearer <token>
  ↓
api_rest.py → jwt_auth.get_current_user()
  ↓
Client ← [{nombre, descripcion, ...}]
```

### Patron TestClient

`web.py` usa `TestClient` de FastAPI (basado en httpx) para llamar internamente a `api_rest.py`:

```python
# web.py
from fastapi.testclient import TestClient

client = TestClient(app)
token = request.cookies.get("access_token")

# Llamada interna con headers
response = client.get(
    "/tareas",
    headers={"Authorization": f"Bearer {token}"}
)
```

Esto permite:
- ✅ Reutilizar toda la lógica de la API
- ✅ No duplicar código de negocio
- ✅ Tests más fáciles (un solo TestClient)
- ✅ Cookies → Headers conversion centralizada

## 📊 Características Técnicas

### ⚡ FastAPI
- **Validación automática** con Pydantic
- **Documentación interactiva** auto-generada
- **Serialización JSON** optimizada
- **Type hints** completos en todos los endpoints
- **Async/await** support nativo
- **Dependency injection** para gestor y auth

### 🎨 Jinja2
- **Server-side rendering** - HTML generado en servidor
- **Template inheritance** - `{% extends "base.html" %}`
- **Includes** - `{% include "_fragment.html" %}`
- **Filters** - `{{ nombre|upper }}`, `{{ lista|join(', ') }}`
- **Control flow** - `{% if %}`, `{% for %}`
- **Auto-escaping** - Protección XSS por defecto
- **Macros** - Funciones reutilizables

### 🚀 HTMX 1.9.2
- **hx-get/post/put/delete** - Requests AJAX simples
- **hx-target="#element"** - Dónde actualizar DOM
- **hx-swap="innerHTML"** - Estrategia de reemplazo
- **hx-trigger="click"** - Eventos disparadores
- **hx-confirm** - Confirmaciones nativas
- **hx-indicator** - Spinners automáticos
- **No JavaScript** - Todo en atributos HTML

### 🔒 JWT con RS256
- **Algoritmo asimétrico** - Llaves pública/privada
- **Auto-generación** - Llaves creadas si no existen
- **Access tokens** - 30 minutos de vida
- **Refresh tokens** - 7 días de vida
- **Claims personalizados** - tipo_usuario, sub, exp, iat
- **Renovación automática** - Refresh sin re-login

### 🛡️ Seguridad
- **HttpOnly cookies** - JavaScript no puede leer tokens
- **Bcrypt hashing** - Contraseñas nunca en texto plano
- **CORS configurado** - Orígenes permitidos
- **Validación strict** - Pydantic en entrada/salida
- **Error handling** - No expone stack traces

### 📋 Modelos Pydantic

Definidos en `api_models.py`:

- **LoginRequest** / **TokenResponse** (en `jwt_auth.py`)
- **UsuarioCreate** / **UsuarioResponse**
- **TareaCreate** / **TareaResponse** / **TareaListResponse**
- **ComentarioCreate** / **ComentarioResponse**
- **AsignarRequest** / **FinalizarRequest**
- **EstadisticasResponse** / **HealthResponse**
- **BaseResponse** - Respuesta genérica {success, message}
- **PaginationMeta** - Metadatos de paginación

## 🧪 Testing

### Tests Automatizados

```bash
# Ejecutar todos los tests
python api-rest/tests/run_all_tests.py

# Tests específicos
pytest api-rest/tests/test_jwt_integration.py -v
pytest api-rest/tests/test_jwt_unit.py -v
pytest api-rest/tests/test_api_endpoints_unit.py -v

# Con cobertura
pytest api-rest/tests/ --cov=api-rest --cov-report=html
```

### Cliente Python

```python
from api_rest.test_api_client import TaskAPIClient

# Crear cliente
client = TaskAPIClient()

# Login
result = client.login("admin", "password123")

# Crear tarea
result = client.crear_tarea("Nueva tarea", "Descripción")

# Ver estadísticas
stats = client.get_stats()
```

### Notebook Jupyter

Abrir `test_api_endpoints.ipynb` para pruebas interactivas con ejemplos de todos los endpoints.

### Ejemplos con curl

#### Login y uso de token
```bash
# Login
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"admin","contraseña":"admin123"}' \
  | jq -r '.access_token')

# Usar token
curl -X GET "http://localhost:8000/tareas" \
  -H "Authorization: Bearer $TOKEN"
```

#### Crear y gestionar tareas
```bash
# Crear tarea
curl -X POST "http://localhost:8000/tareas" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Tarea 1","descripcion":"Hacer algo"}'

# Agregar comentario
curl -X POST "http://localhost:8000/tareas/comentario" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre_tarea":"Tarea 1","comentario":"Progreso OK"}'

# Finalizar
curl -X POST "http://localhost:8000/tareas/finalizar" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre_tarea":"Tarea 1"}'
```

## � Configuración

### Variables de Entorno (Opcional)

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
```

### Dependencias Requeridas

```bash
# Core
fastapi>=0.104.0
uvicorn[standard]
pydantic

# Auth & Security
PyJWT[crypto]
cryptography
passlib[bcrypt]
bcrypt

# HTTP Client
httpx

# Forms
python-multipart

# Templates
Jinja2>=3.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

## 🌍 CORS y Deployment

### Desarrollo Local
```python
# CORS configurado en api_rest.py
origins = [
    "http://localhost:3000",  # React
    "http://localhost:8080",  # Vue
    "http://localhost:5000",  # Flask
]
```

### Producción

Recomendaciones para deployment:

1. **Variables de entorno** para secretos
2. **HTTPS obligatorio** (Let's Encrypt)
3. **Gunicorn/Uvicorn** como worker
4. **Nginx** como reverse proxy
5. **Rate limiting** (slowapi, nginx)
6. **Logging estructurado** (loguru, python-json-logger)
7. **Monitoring** (Prometheus, Grafana)
8. **Base de datos** externa (PostgreSQL)

```bash
# Ejemplo producción con gunicorn
gunicorn api-rest.api_rest:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

## 📱 Integración con Clientes

### Frontend Web (HTMX)
Ya incluido en `templates/` - listo para usar.

### React / Vue / Angular
```javascript
// Login
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({nombre: 'admin', contraseña: 'admin123'})
});
const {access_token} = await response.json();

// Usar token
const tareas = await fetch('http://localhost:8000/tareas', {
  headers: {'Authorization': `Bearer ${access_token}`}
}).then(r => r.json());
```

### Python Client
```python
import requests

# Login
r = requests.post('http://localhost:8000/auth/login',
    json={'nombre': 'admin', 'contraseña': 'admin123'})
token = r.json()['access_token']

# Requests con token
headers = {'Authorization': f'Bearer {token}'}
tareas = requests.get('http://localhost:8000/tareas', headers=headers).json()
```

### Mobile (Flutter/React Native)
```dart
// Flutter example
final response = await http.post(
  Uri.parse('http://localhost:8000/auth/login'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({'nombre': 'admin', 'contraseña': 'admin123'})
);
final token = jsonDecode(response.body)['access_token'];
```

## 🚀 Próximas Mejoras

- [ ] **Rate limiting** con slowapi
- [ ] **Logging estructurado** con loguru
- [ ] **Métricas** Prometheus + Grafana
- [ ] **WebSockets** para notificaciones en tiempo real
- [ ] **Filtros avanzados** en listados (búsqueda, ordenamiento)
- [ ] **Paginación cursor-based** para grandes datasets
- [ ] **Upload de archivos** adjuntos a tareas
- [ ] **Notificaciones email** con templates
- [ ] **API versionada** (/v1/, /v2/)
- [ ] **GraphQL endpoint** adicional
- [ ] **Cache con Redis** para mejor performance
- [ ] **Background tasks** con Celery

## 📞 Documentación Adicional

### Guías en el Proyecto
- **`JWT_AUTHENTICATION_GUIDE.md`** - Guía completa de autenticación JWT
- **`PAGINACION_GUIDE.md`** - Implementación de paginación
- **`GUIA_DESARROLLADORES.md`** - Guía para desarrolladores
- **`GUIA_JINJA2.md`** - Uso de plantillas Jinja2

### Recursos Externos
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Jinja2 Docs**: https://jinja.palletsprojects.com/
- **HTMX Docs**: https://htmx.org/docs/
- **PyJWT Docs**: https://pyjwt.readthedocs.io/
- **Pydantic Docs**: https://docs.pydantic.dev/

## 💡 Tips y Mejores Prácticas

### Desarrollo
```bash
# Hot reload activado
uvicorn api-rest.api_rest:app --reload

# Ver logs detallados
uvicorn api-rest.api_rest:app --reload --log-level debug

# Cambiar puerto
uvicorn api-rest.api_rest:app --reload --port 8080
```

### Debugging
```python
# En api_rest.py o web.py
import logging
logger = logging.getLogger(__name__)

@app.get("/endpoint")
async def my_endpoint():
    logger.debug("Debug info")
    logger.info("Info message")
    logger.warning("Warning")
    logger.error("Error", exc_info=True)
```

### Seguridad
- ✅ Siempre usar HTTPS en producción
- ✅ Rotar llaves JWT periódicamente
- ✅ Validar y sanitizar inputs del usuario
- ✅ No exponer stack traces en producción
- ✅ Implementar rate limiting
- ✅ Mantener dependencias actualizadas

### Performance
- ✅ Usar `async def` para operaciones I/O
- ✅ Implementar caching para datos frecuentes
- ✅ Paginar resultados grandes
- ✅ Optimizar queries a archivos JSON
- ✅ Comprimir respuestas (gzip)

## 📊 Estadísticas del Proyecto

```
Líneas de código:
- api_rest.py: ~2000 líneas
- web.py: ~1000 líneas  
- jwt_auth.py: ~400 líneas
- api_models.py: ~300 líneas
- templates/: ~800 líneas

Tests:
- Cobertura: >80%
- Tests unitarios: 50+
- Tests integración: 30+

Endpoints:
- Web routes: 19
- API routes: 24
- Total: 43 endpoints
```