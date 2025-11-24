# 🔐 Guía de Autenticación JWT - API REST

## 📋 Resumen de Endpoints de Autenticación

La API ahora incluye un sistema completo de autenticación JWT (JSON Web Tokens) con los siguientes endpoints:

### 🚀 Endpoints Principales

| Método | Endpoint | Descripción | Requiere Auth |
|--------|----------|-------------|---------------|
| `POST` | `/auth/login` | Iniciar sesión y obtener tokens | ❌ No |
| `POST` | `/auth/refresh` | Renovar access token | ❌ No |
| `POST` | `/auth/logout` | Cerrar sesión | ✅ Sí |
| `GET` | `/auth/me` | Obtener info del usuario actual | ✅ Sí |

## 🔑 Flujo de Autenticación

### 1. Obtener Tokens (Login)
```bash
curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
```

**Respuesta:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

### 2. Usar Access Token
```bash
curl -X GET http://localhost:8000/auth/me \
     -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
```

### 3. Renovar Token (cuando expire)
```bash
curl -X POST http://localhost:8000/auth/refresh \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."}'
```

## 🛡️ Seguridad Implementada

- **Algoritmo RSA256**: Tokens firmados con clave RSA de 2048 bits
- **Expiración**: Access tokens (30 min), Refresh tokens (7 días)
- **Rotación de tokens**: Nuevos tokens en cada refresh
- **Validación estricta**: Verificación de firma, expiración y tipo
- **Manejo de errores**: Respuestas HTTP estándar

## 🔧 Configuración JWT

El sistema genera automáticamente un par de claves RSA que se mantienen en memoria:

```python
# Configuración en jwt_auth.py
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutos
REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 días
ALGORITHM = "RS256"               # RSA con SHA-256
```

## 📚 Endpoints Protegidos

Los siguientes endpoints ahora pueden protegerse con JWT (agregar en futuras versiones):

- `GET /tareas` - Listar tareas del usuario
- `POST /tareas` - Crear nueva tarea
- `PUT /tareas/{id}` - Actualizar tarea
- `DELETE /tareas/{id}` - Eliminar tarea

### Ejemplo de Endpoint Protegido:
```python
@app.get("/tareas")
async def listar_tareas(
    current_user: TokenData = Depends(get_current_user),
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    # Solo usuarios autenticados pueden acceder
    # current_user.username contiene el nombre del usuario
    # current_user.role contiene el rol (admin/user)
```

## 🧪 Testing con Python

```python
import requests

# 1. Login
login_response = requests.post("http://localhost:8000/auth/login", 
    json={"username": "admin", "password": "admin123"})
tokens = login_response.json()

# 2. Usar token para endpoint protegido
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
user_info = requests.get("http://localhost:8000/auth/me", headers=headers)
print(user_info.json())
```

## 🚨 Manejo de Errores

- **401 Unauthorized**: Token inválido, expirado o ausente
- **403 Forbidden**: Token válido pero sin permisos para la acción
- **400 Bad Request**: Datos de login incorrectos
- **404 Not Found**: Usuario no encontrado en el sistema

## 📖 Documentación Interactiva

Una vez ejecutando el servidor con:
```bash
uvicorn api_rest:app --reload
```

Visita: http://localhost:8000/docs para la documentación Swagger interactiva donde podrás:
- Ver todos los endpoints
- Probar directamente desde el navegador  
- Ver esquemas de request/response
- Autorizar tu sesión con JWT

## 🔄 Próximos Pasos

1. **Proteger endpoints existentes**: Agregar `Depends(get_current_user)` a endpoints sensibles
2. **Roles y permisos**: Implementar decorador para verificar roles específicos
3. **Blacklist de tokens**: Invalidación real de tokens en logout
4. **Rate limiting**: Limitar intentos de login por IP
5. **Logs de seguridad**: Registrar todos los eventos de autenticación