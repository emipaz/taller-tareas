# 🌐 API REST del Sistema de Gestión de Tareas

Implementación completa de API REST usando FastAPI con autenticación JWT, documentación automática y todas las funcionalidades del sistema de gestión de tareas.

## 📁 Estructura

```
api-rest/
├── __init__.py              # Módulo API REST
├── api_rest.py             # Aplicación FastAPI principal
├── api_models.py           # Modelos Pydantic de validación
├── jwt_auth.py             # Sistema de autenticación JWT
├── test_api_client.py      # Cliente Python para pruebas
├── test_api_endpoints.ipynb # Notebook Jupyter para tests
└── tests/                  # Tests automatizados
    ├── __init__.py
    └── test_app.py         # Tests de la aplicación
```

## 🚀 Inicio Rápido

### Ejecutar la API

```bash
# Desde el directorio raíz del proyecto
python api.py

# O directamente con uvicorn
uvicorn api-rest.api_rest:app --reload --host 0.0.0.0 --port 8000
```

### Acceder a la Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 Autenticación JWT

La API implementa autenticación JWT con las mejores prácticas de seguridad:

### Flujo de Autenticación

```python
# 1. Login para obtener tokens
POST /auth/login
{
    "nombre": "admin",
    "contraseña": "password123"
}

# Respuesta:
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}

# 2. Usar token en headers
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...

# 3. Renovar token
POST /auth/refresh
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
}
```

### Características de Seguridad

- ✅ **Algoritmo RS256** (RSA + SHA256)
- ✅ **Access tokens** de corta duración (30 min)
- ✅ **Refresh tokens** de larga duración (7 días)
- ✅ **Rotación automática** de tokens
- ✅ **Logout** para invalidar tokens
- ✅ **Validación estricta** de claims JWT

## 📋 Endpoints Disponibles

### 🏥 Sistema
```
GET  /              # Información de la API
GET  /health        # Health check
GET  /stats         # Estadísticas (🔐 auth requerida)
```

### 👥 Usuarios
```
POST   /usuarios           # Crear usuario (🔐 auth)
GET    /usuarios           # Listar usuarios (🔐 auth)  
GET    /usuarios/{nombre}  # Obtener usuario (🔐 auth)
DELETE /usuarios/{nombre}  # Eliminar usuario (🔐 admin)
POST   /usuarios/admin     # Crear admin (público)
```

### 🔐 Autenticación
```
POST /auth/login           # Iniciar sesión
POST /auth/refresh         # Renovar tokens
POST /auth/logout          # Cerrar sesión (🔐 auth)
GET  /auth/me             # Usuario actual (🔐 auth)
POST /auth/set-password   # Establecer contraseña
POST /auth/change-password # Cambiar contraseña
```

### 📝 Tareas
```
POST   /tareas               # Crear tarea (🔐 auth)
GET    /tareas               # Listar tareas (🔐 auth)
GET    /tareas/{nombre}      # Obtener tarea (🔐 auth)
GET    /tareas/usuario/{user} # Tareas de usuario (🔐 auth)
POST   /tareas/asignar       # Asignar usuario (🔐 auth)
POST   /tareas/finalizar     # Finalizar tarea (🔐 auth)
POST   /tareas/comentario    # Agregar comentario (🔐 auth)
```

## 🧪 Testing

### Cliente Python

```python
from api_rest.test_api_client import TaskAPIClient

# Crear cliente
client = TaskAPIClient()

# Login
result = client.login("admin", "password123")

# Crear tarea
result = client.crear_tarea("Nueva tarea", "Descripción de la tarea")

# Ver estadísticas
stats = client.get_stats()
```

### Notebook Jupyter

Abrir `test_api_endpoints.ipynb` para pruebas interactivas completas con ejemplos de todos los endpoints.

### Tests Automatizados

```bash
# Ejecutar todos los tests
python api-rest/tests/run_all_tests.py

# Tests específicos
python api-rest/tests/test_jwt_integration.py   # Tests JWT
python api-rest/tests/test_app.py              # Tests unitarios

# Con pytest (si está instalado)
python -m pytest api-rest/tests/ -v

# Con cobertura
python -m pytest api-rest/tests/ --cov=api-rest --cov-report=html
```

## 📊 Características Técnicas

### ⚡ FastAPI
- **Validación automática** con Pydantic
- **Documentación interactiva** generada automáticamente
- **Serialización JSON** optimizada
- **Type hints** completos
- **Async/await** support

### 🔒 Seguridad
- **JWT con RS256** para tokens seguros
- **Validación de datos** en entrada y salida
- **CORS configurado** para desarrollo
- **Headers de seguridad** implementados
- **Rate limiting** preparado

### 📋 Modelos de Datos

Todos los modelos están definidos en `api_models.py` con validación Pydantic:

- `LoginRequest` / `TokenResponse` (autenticación JWT)
- `UsuarioCreate` / `UsuarioResponse`
- `TareaCreate` / `TareaResponse`
- `EstadisticasResponse` / `PaginationMeta`
- Y muchos más...

**Nota:** `TokenResponse` está definido en `jwt_auth.py` ya que es específico de autenticación JWT.

## 🔧 Configuración

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

### Dependencias

```bash
pip install fastapi uvicorn pydantic pyjwt cryptography passlib bcrypt
```

## 🌍 CORS y Deployment

### Desarrollo Local
```python
# CORS configurado para desarrollo
origins = [
    "http://localhost:3000",  # React
    "http://localhost:8080",  # Vue
    "http://localhost:5000",  # Flask
]
```

### Producción
Para deployment en producción, considera:

- Variables de entorno para secretos
- HTTPS obligatorio
- Rate limiting
- Logging estructurado
- Monitoring de salud
- Base de datos externa

## 📱 Integración con Interfaces

Este módulo API REST está diseñado para:

- **Frontend Web** (React, Vue, Angular)
- **Aplicaciones móviles** (React Native, Flutter)
- **Herramientas CLI** personalizadas
- **Integraciones de terceros**
- **Microservicios** adicionales

## 🚀 Próximas Mejoras

- [ ] Rate limiting avanzado
- [ ] Logging estructurado
- [ ] Métricas y monitoring
- [ ] Websockets para notificaciones
- [ ] Filtros avanzados en listados
- [ ] Paginación mejorada
- [ ] Upload de archivos
- [ ] Notificaciones por email

## 📞 Soporte

Para problemas o preguntas sobre la API:

1. Revisar la documentación interactiva en `/docs`
2. Ejecutar el notebook de pruebas
3. Verificar logs del servidor
4. Consultar tests unitarios para ejemplos