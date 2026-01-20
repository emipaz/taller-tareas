"""API REST para el sistema de gestión de tareas.

Este módulo implementa la API REST completa del sistema usando FastAPI,
proporcionando endpoints para gestión de usuarios, tareas, autenticación JWT,
y sirviendo la interfaz web HTML mediante Jinja2.

## Arquitectura Dual

El sistema combina dos interfaces:
1. **API REST JSON** - Endpoints `/api/*`, `/tareas/*`, `/auth/*` para clientes externos
2. **Interfaz Web HTML** - Endpoints `/`, `/dashboard`, `/web/*` usando Jinja2 + HTMX

Ambas interfaces comparten:
- Misma lógica de negocio (GestorSistema)
- Misma autenticación JWT (RS256)
- Mismos modelos de datos (Pydantic)

## Stack Tecnológico

### Backend
- **FastAPI** - Framework ASGI moderno con validación automática
- **Uvicorn** - Servidor ASGI de alto rendimiento
- **Pydantic** - Validación y serialización con type hints
- **httpx** - Cliente HTTP para TestClient

### Autenticación
- **PyJWT** - Tokens JWT con algoritmo RS256 (asimétrico)
- **cryptography** - Generación automática de llaves RSA
- **passlib[bcrypt]** - Hashing seguro de contraseñas
- **HttpOnly cookies** - Almacenamiento seguro en navegador

### Interfaz Web
- **Jinja2** - Templates server-side con herencia
- **HTMX** - Interactividad dinámica sin JavaScript complejo
- **CSS3** - Estilos modernos con variables y flexbox

## Endpoints (45 total)

### API REST - JSON (25 endpoints)

#### Sistema (3)
- GET  /api              # Información de la API
- GET  /api/health       # Health check
- GET  /stats            # Estadísticas (🔐 auth)

#### Usuarios (5)
- GET    /usuarios            # Listar con paginación (🔐 auth)
- GET    /usuarios/{nombre}   # Usuario específico (🔐 auth)
- POST   /usuarios            # Crear usuario (🔐 auth)
- POST   /usuarios/admin      # Crear primer admin (público)
- DELETE /usuarios/{nombre}   # Eliminar usuario (🔐 admin)

#### Autenticación JWT (7)
- POST /auth/login            # Login → access + refresh tokens
- POST /auth/refresh          # Renovar access_token
- POST /auth/logout           # Invalidar tokens (🔐 auth)
- GET  /auth/me               # Usuario actual (🔐 auth)
- POST /auth/set-password     # Primera contraseña
- POST /auth/change-password  # Cambiar contraseña (🔐 auth)
- POST /auth/reset-password   # Resetear contraseña (🔐 admin)

#### Tareas (10)
- GET    /tareas                     # Listar todas (🔐 auth)
- GET    /tareas/{nombre}            # Tarea específica (🔐 auth)
- GET    /tareas/usuario/{nombre}    # Tareas de usuario (🔐 auth)
- POST   /tareas                     # Crear tarea (🔐 auth)
- POST   /tareas/asignar             # Asignar usuario (🔐 auth)
- POST   /tareas/desasignar          # Quitar usuario (🔐 admin)
- POST   /tareas/finalizar           # Finalizar tarea (🔐 auth)
- POST   /tareas/comentario          # Agregar comentario (🔐 auth)
- PUT    /tareas/{nombre}/reactivar  # Reactivar (🔐 admin)
- DELETE /tareas/{nombre}            # Eliminar (🔐 admin)

### Interfaz Web - HTML (20 endpoints)

#### Páginas (6)
- GET /                          # Landing con login
- GET /dashboard                 # Dashboard principal (🔐 auth)
- GET /tareas/lista              # Lista filtrable (🔐 auth)
- GET /tareas/detalle/{nombre}   # Detalle completo (🔐 auth)
- GET /admin/users               # Panel admin usuarios (🔐 admin)
- GET /admin/stats               # Estadísticas (🔐 admin)

#### Autenticación Web (4)
- POST /login                    # Login (cookies HttpOnly)
- POST /set-password             # Primera contraseña
- POST /change-password          # Cambiar contraseña (🔐 auth)
- GET  /logout                   # Cerrar sesión

#### Administración (4)
- POST /admin/create-user        # Crear usuario (🔐 admin)
- POST /admin/reset-password     # Resetear contraseña (🔐 admin)
- POST /admin/delete-user        # Eliminar usuario (🔐 admin)
- POST /admin/create-task        # Crear tarea (🔐 admin)

#### Acciones Tareas HTMX (6) - Prefijo /web/
- POST   /web/tareas/comentario         # Agregar comentario (🔐 auth)
- POST   /web/tareas/asignar            # Asignar usuario (🔐 auth)
- POST   /web/tareas/desasignar         # Quitar usuario (🔐 admin)
- POST   /web/tareas/finalizar          # Finalizar tarea (🔐 auth)
- PUT    /web/tareas/{nombre}/reactivar # Reactivar (🔐 admin)
- DELETE /web/tareas/{nombre}           # Eliminar (🔐 admin)

## Características Principales

### Validación Automática
FastAPI + Pydantic validan automáticamente todos los requests:
- Type hints de Python
- Modelos Pydantic con validadores
- Respuestas 422 automáticas para datos inválidos

### Documentación Interactiva
- **Swagger UI**: http://localhost:8000/docs (modo oscuro)
- **ReDoc**: http://localhost:8000/redoc (alternativa)
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Seguridad
- JWT con RS256 (asimétrico)
- Cookies HttpOnly (protección XSS)
- Bcrypt para contraseñas
- CORS configurado
- Validación estricta de entrada

### CORS Configuration
Orígenes permitidos para desarrollo:
- http://localhost:3000 (React)
- http://localhost:8080 (Vue)
- http://localhost:5173 (Vite)

## Modelos de Datos

Definidos en `api_models.py`:
- BaseResponse, ErrorResponse, HealthResponse
- UsuarioCreate, UsuarioResponse, UsuarioListPaginatedResponse
- TareaCreate, TareaResponse, TareaListResponse
- AsignarUsuarioRequest, ComentarioRequest, FinalizarTareaRequest
- EstadisticasResponse, PaginationMeta, FilterMeta

## Dependencias Inyectables

### get_gestor()
Retorna instancia de GestorSistema para acceder a la lógica de negocio.

### get_current_user()
Valida token JWT, retorna TokenData. Uso: endpoints que requieren auth.

### get_current_admin()
Valida token JWT + rol admin. Uso: endpoints administrativos.

## Logging

Logger: "api_rest"
- INFO: Operaciones normales, requests exitosos
- DEBUG: Detalles de paginación, filtros, validaciones
- WARNING: Intentos fallidos, datos inválidos
- ERROR: Excepciones, errores internos

## Integración con web.py

El módulo `web.py` se registra como router:
```python
from web import router as web_router
app.include_router(web_router)
```

web.py usa TestClient para llamar internamente a estos endpoints,
convirtiendo cookies HttpOnly en Authorization headers.

## Uso

Ejecutar directamente:
```bash
python api.py
# o
python api-rest/api_rest.py
```

Importar como módulo:
```python
from api_rest import app
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Estructura de Respuestas

### Éxito
```json
{
  "success": true,
  "message": "Operación exitosa",
  "data": {...}
}
```

### Error
```json
{
  "detail": "Mensaje de error",
  "error_code": "HTTP_400"
}
```

### Paginación
```json
{
  "usuarios": [...],
  "pagination": {
    "current_page": 1,
    "per_page": 10,
    "total_items": 50,
    "total_pages": 5
  }
}
```

## Testing

Ver `tests/` para:
- test_jwt_integration.py (tests JWT)
- test_jwt_unit.py (tests unitarios)
- test_api_endpoints_unit.py (tests API)
- test_api_client.py (cliente de pruebas)
- test_api_endpoints.ipynb (notebook interactivo)
"""

import os
import sys

# Asegurar que el directorio padre esté en el path para imports relativos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importaciones estándar
from datetime import datetime
from typing import List, Optional
import uvicorn

# Importaciones de FastAPI y dependencias relacionadas
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer
import logging

# Logging básico para depuración
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger("api_rest")


# Importaciones de módulos internos 
from jwt_auth import (
    create_token_response, get_current_user, get_current_admin, 
    verify_token, TokenData, TokenResponse
)

# Importación del gestor del sistema (lógica de negocio)
from core import GestorSistema
# Importación de utilidades del core
from core.utils import buscar_usuario_por_nombre
from core.utils import buscar_tarea_por_nombre

# Importación de modelos Pydantic para validación y serialización
from api_models import (
    # Respuestas base
    BaseResponse, ErrorResponse, HealthResponse,
    
    # Usuario models
    UsuarioCreate, UsuarioCreateAdmin, UsuarioResponse, UsuarioListResponse,
    UsuarioListPaginatedResponse, PaginationMeta, FilterMeta,
    LoginRequest, PasswordSetRequest, PasswordChangeRequest, PasswordResetRequest,
    
    # Tarea models  
    TareaCreate, TareaResponse, TareaListResponse, TareaResumenResponse,
    AsignarUsuarioRequest, ComentarioRequest, FinalizarTareaRequest,
    
    # Estadísticas y filtros
    EstadisticasResponse, EstadisticasUsuarios, EstadisticasTareas,
    FiltroTareasRequest, BusquedaRequest
)


# ================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ================================

# Crear instancia principal de FastAPI
app = FastAPI(
    title="Sistema de Gestión de Tareas",
    version="1.0.0"
)

# Configurar CORS (Cross-Origin Resource Sharing)
# Permite que aplicaciones web desde otros dominios consuman la API
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],        # En producción: especificar dominios exactos
    allow_credentials = True,         # Permite cookies y headers de autenticación
    allow_methods     = ["*"],        # Permite todos los métodos HTTP
    allow_headers     = ["*"],        # Permite todos los headers
)

# Instancia del gestor del sistema (lógica de negocio)
# Esta es la única instancia que maneja el estado del sistema
gestor = GestorSistema()


# ================================
# ARCHIVOS ESTÁTICOS Y RUTAS WEB
# ================================

# Montar carpeta static (si existe) y registrar rutas web separadas
try:
    from fastapi.staticfiles import StaticFiles
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
except Exception:
    pass

# Registrar router de páginas web (htmx/Jinja2)
try:
    from web import router as web_router
    app.include_router(web_router)
except Exception as e:
    print(f"⚠️ Error al cargar módulo web: {e}")
    # Si el módulo web aún no existe (durante cambios), ignorar
    print("⚠️ Módulo web no disponible, ignorando rutas web")
    pass


def get_gestor() -> GestorSistema:
    """Dependency injection para obtener la instancia del gestor.
    
    FastAPI usa este patrón para inyectar dependencias en los endpoints.
    Esto facilita testing (se puede mockear) y gestión del estado.
    
    **Retorna:**
        GestorSistema: Instancia única del gestor del sistema.
        
    **Nota:**
        Esta función se ejecuta automáticamente por FastAPI cada vez
        que un endpoint declara `gestor_sistema: GestorSistema = Depends(get_gestor)`.
        Es una forma elegante de compartir el mismo objeto entre todos los endpoints.
    """
    return gestor


# ================================
# MANEJO DE ERRORES PERSONALIZADO
# ================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Maneja excepciones HTTP para respuestas consistentes.
    
    FastAPI permite personalizar el manejo de errores para mantener
    consistencia en el formato de respuestas de error.
    
    **Parámetros:**
        request             : Request HTTP que causó la excepción.
        exc (HTTPException) : Excepción HTTP capturada.
        
    **Retorna:**
        JSONResponse: Respuesta JSON con formato estándar de error.
        
    **Nota:**
        Este handler se ejecuta automáticamente cuando cualquier endpoint
        lanza una HTTPException. Garantiza formato consistente de errores.
    """
    return JSONResponse(
        status_code = exc.status_code,
        content     = {
                        "success"    : False,
                        "message"    : exc.detail,
                        "error_code" : f"HTTP_{exc.status_code}"
                    }
                        )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Maneja excepciones generales no controladas.
    
    Captura cualquier excepción que no sea HTTPException para evitar
    que el servidor devuelva errores internos al cliente.
    
    **Parámetros:**
        request          : Request HTTP que causó la excepción.
        exc (Exception)  : Excepción general capturada.
        
    **Retorna:**
        JSONResponse: Respuesta JSON genérica de error interno.
        
    **Nota:**
        En producción, también debería loggearse la excepción real
        para debugging sin exponer detalles internos al cliente.
    """
    return JSONResponse(
        status_code = 500,
        content     = {
                        "success"    : False,
                        "message"    : "Error interno del servidor",
                        "error_code" : "INTERNAL_ERROR"
                    }
                    )

# ================================
# ENDPOINTS DE SISTEMA
# ================================

@app.get("/api", response_model=HealthResponse)
async def root():
    """Endpoint raíz que devuelve el estado básico de la API.
    
    Primer punto de contacto con la API. Útil para verificación rápida
    de conectividad y estado operativo.
    
    **Retorna:**
        HealthResponse: Estado actual y timestamp de la API.
        
    **Ejemplo de uso:**
    ```bash
    curl http://localhost:8000/
    ```
    
    **Respuesta:**
    ```json
    {
        "status": "online",
        "timestamp": "2025-11-21T14:30:00.123456",
        "version": "1.0.0"
    }
    ```
    
    **Nota:**
        Este endpoint no requiere autenticación y siempre debe responder rápidamente.
    """
    return HealthResponse(
        status    = "online",
        timestamp = datetime.now(),
        version   = "1.0.0"
    )


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint para monitoreo del sistema.
    
    Endpoint estándar para verificación de estado por parte de:
    - Load balancers
    - Sistemas de monitoreo
    - Herramientas de orchestration (Docker, Kubernetes)
    - Scripts de verificación automatizada
    
    **Retorna:**
        HealthResponse: Estado detallado del sistema.
        
    **Ejemplo de uso:**
    ```bash
    curl http://localhost:8000/health
    ```
    
    **Nota:**
        En un sistema más complejo, aquí se verificarían:
        - Conectividad a base de datos
        - Estado de servicios externos
        - Uso de memoria y CPU
        - Espacio en disco
    """
    return HealthResponse(
        status    = "healthy",
        timestamp = datetime.now(),
        version   = "1.0.0"
    )


@app.get("/stats", response_model=EstadisticasResponse)
async def get_estadisticas(
    current_user: TokenData = Depends(get_current_user),
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Obtiene estadísticas completas del sistema.
    
    Proporciona métricas actualizadas del estado del sistema, útiles para:
    - Dashboards administrativos
    - Reportes de gestión
    - Monitoreo de carga de trabajo
    - Análisis de utilización
    
    **Autenticación requerida:** Token JWT válido en header Authorization.
    
    **Parámetros:**
        current_user: Usuario autenticado obtenido del token JWT.
        gestor_sistema: Instancia del gestor inyectada automáticamente.
        
    **Retorna:**
        EstadisticasResponse: Métricas completas de usuarios y tareas.
        
    **Errores:**
        HTTPException: 500 si no se pueden obtener las estadísticas.
        
    **Ejemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/stats" \
         -H "Authorization: Bearer tu_access_token_aqui"
    ```
    
    **Respuesta:**
    ```json
    {
        "usuarios": {
            "total": 15,
            "admins": 2,
            "users": 13,
            "sin_password": 3
        },
        "tareas": {
            "total": 25,
            "pendientes": 18,
            "finalizadas": 7,
            "sin_asignar": 4
        }
    }
    ```
    """
    try:
        logger.debug("get_estadisticas called by %s", getattr(current_user, 'username', None))
        stats = gestor_sistema.obtener_estadisticas_sistema()
        
        # Verificar si hubo error en la obtención de estadísticas
        if "error" in stats:
            raise HTTPException(
                status_code = 500,
                detail      = "No se pudieron obtener las estadísticas"
            )
        
        return EstadisticasResponse(
            usuarios = EstadisticasUsuarios(**stats["usuarios"]),
            tareas   = EstadisticasTareas  (**stats["tareas"])
        )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))
    


# ================================
# ENDPOINTS DE USUARIOS
# ================================

@app.get("/usuarios", response_model = UsuarioListPaginatedResponse)
async def listar_usuarios(
    page           : int = 1,
    limit          : int = 10,
    search         : Optional[str] = None,
    rol            : Optional[str] = None,
    current_user   : TokenData = Depends(get_current_admin),  # Solo admins pueden listar usuarios
    gestor_sistema : GestorSistema = Depends(get_gestor)
):
    """Lista usuarios con paginación, filtros y búsqueda.
    
    Endpoint para obtener usuarios con soporte completo de paginación,
    filtrado por rol y búsqueda por nombre. Optimizado para sistemas
    con muchos usuarios.
    
    **Parámetros:**
        page: Número de página (empezando desde 1, default: 1).
        limit: Usuarios por página (rango: 1-100, default: 10).
        search: Filtro de búsqueda por nombre (opcional).
        rol: Filtro por rol específico: 'admin' o 'user' (opcional).
        gestor_sistema: Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        UsuarioListResponse: Lista paginada de usuarios con metadatos.
        
    **Errores:**
        HTTPException: 400 si los parámetros de paginación son inválidos.
        HTTPException: 500 si hay error al acceder a los datos.
        
    **Ejemplo de uso:**
        ```bash
        # Página básica
        curl "http://localhost:8000/usuarios?page=1&limit=5"
        
        # Con filtros
        curl "http://localhost:8000/usuarios?page=2&limit=10&rol=admin"
        
        # Con búsqueda
        curl "http://localhost:8000/usuarios?search=juan&limit=20"
        ```
        
        
        **Respuesta:**
        ```json
        {
            "usuarios": [
                {
                    "nombre": "admin",
                    "rol": "admin", 
                    "tiene_password": true
                }
            ],
            "pagination": {
                "current_page": 1,
                "per_page": 10,
                "total_items": 25,
                "total_pages": 3,
                "has_next": true,
                "has_prev": false,
                "next_page": 2,
                "prev_page": null
            }
        }
        ```
        
    **🔍 Filtros disponibles:**
        - **search**: Busca en nombres de usuario (case-insensitive)
        - **rol**: Filtra por 'admin' o 'user'
        - **page**: Número de página (mínimo 1)
        - **limit**: Items por página (1-100, recomendado: 10-50)
        
    **🚀 Rendimiento:**
        Para sistemas grandes, considere implementar:
        - Índices de base de datos en campos de filtro
        - Cache de resultados frecuentes
        - Paginación cursor-based para datasets muy grandes
    """
    try:
        logger.debug("listar_usuarios called by %s page=%s limit=%s search=%s rol=%s", getattr(current_user, 'username', None), page, limit, search, rol)
        # Validar parámetros de paginación
        if page < 1:
            raise HTTPException(
                status_code=400, 
                detail="El número de página debe ser mayor o igual a 1"
            )
        
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=400,
                detail="El límite debe estar entre 1 y 100"
            )
        
        # Validar filtro de rol
        if rol and rol not in ["admin", "user"]:
            raise HTTPException(
                status_code=400,
                detail="El rol debe ser 'admin' o 'user'"
            )
        
        # Cargar todos los usuarios
        usuarios = gestor_sistema.cargar_usuarios()
        
        # Aplicar filtros
        usuarios_filtrados = usuarios
        
        # Filtro por búsqueda de nombre
        if search:
            search_lower = search.lower()
            usuarios_filtrados = [
                u for u in usuarios_filtrados 
                if search_lower in u.nombre.lower()
            ]
        
        # Filtro por rol
        if rol:
            usuarios_filtrados = [
                u for u in usuarios_filtrados 
                if u.rol == rol
            ]
        
        # Calcular metadatos de paginación
        total_items = len(usuarios_filtrados)
        total_pages = (total_items + limit - 1) // limit  # Ceiling division
        
        # Validar que la página solicitada existe
        if page > total_pages and total_items > 0:
            raise HTTPException(
                status_code=404,
                detail=f"Página {page} no existe. Total de páginas: {total_pages}"
            )
        
        # Calcular índices para slicing
        start_index = (page - 1) * limit
        end_index = start_index + limit
        
        # Aplicar paginación
        usuarios_pagina = usuarios_filtrados[start_index:end_index]
        
        # Convertir a response format
        usuarios_response = [
            UsuarioResponse(
                nombre         = usuario.nombre,
                rol            = usuario.rol,
                tiene_password = usuario.tiene_password()
            )
            for usuario in usuarios_pagina
        ]
        
        # Crear metadatos de paginación
        pagination_meta = PaginationMeta(
            current_page=page,
            per_page=limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
            next_page=page + 1 if page < total_pages else None,
            prev_page=page - 1 if page > 1 else None
        )
        
        # Crear metadatos de filtros
        filters_meta = FilterMeta(
            search=search,
            rol=rol
        )
        
        # Crear respuesta paginada
        return UsuarioListPaginatedResponse(
            usuarios=usuarios_response,
            pagination=pagination_meta,
            filters_applied=filters_meta
        )
    
    except HTTPException:
        raise  # Re-lanzar HTTPExceptions
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@app.get("/usuarios/{nombre}", response_model = UsuarioResponse)
async def obtener_usuario(
    nombre: str, 
    current_user: TokenData = Depends(get_current_user),  # Usuario autenticado requerido
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Obtiene información detallada de un usuario específico.
    
    Busca un usuario por su nombre único y devuelve su información completa.
    Útil para verificar detalles antes de operaciones como asignaciones.
    
    **Parámetros:**
        nombre         : Nombre exacto del usuario a buscar (path parameter).
        gestor_sistema : Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        UsuarioResponse: Información completa del usuario encontrado.
        
    **Errores:**
        HTTPException: 404 si el usuario no existe.
        HTTPException: 500 si hay error interno.
        
    **Ejemplo de uso:**
        ```bash
        curl http://localhost:8000/usuarios/juan_perez
        ```
        
        
        **Respuesta:**
        ```json
        {
            "nombre": "juan_perez",
            "rol": "user",
            "tiene_password": true
        }
        ```
        
    **Nota:**
        Los path parameters en FastAPI se definen con {nombre} en la ruta
        y automáticamente se pasan como argumentos a la función.
    """
    try:
        usuarios = gestor_sistema.cargar_usuarios()
        usuario  = buscar_usuario_por_nombre(usuarios, nombre)
        
        if not usuario:
            raise HTTPException(
                status_code = 404,
                detail      = f"Usuario '{nombre}' no encontrado"
            )
        
        return UsuarioResponse(
            nombre         = usuario.nombre,
            rol            = usuario.rol,
            tiene_password = usuario.tiene_password()
        )
    except HTTPException:
        raise  # Re-lanzar HTTPExceptions sin modificar
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@app.post("/usuarios", response_model=BaseResponse)
async def crear_usuario(
    usuario_data: UsuarioCreate,
    current_user: TokenData = Depends(get_current_admin),  # Solo admins pueden crear usuarios
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Crea un nuevo usuario estándar en el sistema.
    
    Los usuarios estándar se crean sin contraseña inicial y deben
    establecerla en su primer login usando /auth/set-password.
    
    **Parámetros:**
        usuario_data   : Datos del usuario a crear (body del request).
        gestor_sistema : Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        BaseResponse: Confirmación de creación exitosa.
        
    **Errores:**
        HTTPException: 400 si el usuario ya existe o datos inválidos.
        HTTPException: 500 si hay error interno.
        
    **Ejemplo de uso:**
        ```bash
        curl -X POST http://localhost:8000/usuarios \\
             -H "Content-Type: application/json" \\
             -d '{"nombre": "maria_garcia"}'
        ```
        
        
        **Respuesta:**
        ```json
        {
            "success": true,
            "message": "Usuario 'maria_garcia' creado exitosamente"
        }
        ```
        
    **Nota:**
        FastAPI automáticamente valida el JSON del request body contra
        el esquema UsuarioCreate y lo convierte en objeto Python.
        Si la validación falla, devuelve 422 con detalles del error.
    """
    try:
        exito, mensaje = gestor_sistema.crear_usuario(usuario_data.nombre)
        
        if not exito:
            raise HTTPException(status_code=400, detail=mensaje)
        
        return BaseResponse(success=True, message=mensaje)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/usuarios/admin", response_model=BaseResponse)
async def crear_admin(
    admin_data: UsuarioCreateAdmin,
    current_user: TokenData = Depends(get_current_admin),
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Crea un nuevo usuario administrador en el sistema.
    
    Los administradores tienen privilegios especiales como crear usuarios,
    resetear contraseñas y acceso completo a todas las funcionalidades.
    A diferencia de los usuarios estándar, los admins requieren contraseña
    desde el momento de creación.
    
    **Autenticación requerida:** Token JWT válido de administrador.
    
    **Parámetros:**
        admin_data: Datos del administrador (nombre y contraseña).
        current_user: Usuario administrador autenticado obtenido del token JWT.
        gestor_sistema: Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        BaseResponse: Confirmación de creación exitosa.
        
    **Errores:**
        HTTPException: 400 si el usuario ya existe o datos inválidos.
        HTTPException: 500 si hay error interno.
        
    **Ejemplo de uso:**
        ```bash
        curl -X POST http://localhost:8000/usuarios/admin \\
             -H "Content-Type: application/json" \\
             -d '{"nombre": "admin", "contraseña": "admin123"}'
        ```
        
        
        **Respuesta:**
        ```json
        {
            "success": true,
            "message": "Administrador 'admin' creado exitosamente"
        }
        ```
        
    **Nota:**
        Solo debe existir un número limitado de administradores.
        La contraseña debe cumplir con políticas de seguridad mínimas.
        Los administradores no pueden ser eliminados del sistema.
    """
    try:
        exito, mensaje = gestor_sistema.crear_admin(admin_data.nombre, 
                                                    admin_data.contraseña)
        
        if not exito:
            raise HTTPException(status_code = 400, detail = mensaje)
        
        return BaseResponse(success = True, message = mensaje)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/usuarios/{nombre}", response_model=BaseResponse)
async def eliminar_usuario(
    nombre: str, 
    current_user: TokenData = Depends(get_current_admin),  # Solo admins pueden eliminar usuarios
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Elimina permanentemente un usuario del sistema.
    
    Operación destructiva que remueve un usuario y toda su información
    asociada. Los administradores no pueden ser eliminados por seguridad.
    Las tareas asignadas al usuario no se eliminan automáticamente.
    
    **Parámetros:**
        nombre: Nombre exacto del usuario a eliminar (path parameter).
        gestor_sistema: Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        BaseResponse: Confirmación de eliminación exitosa.
        
    **Errores:**
        HTTPException: 400 si es admin o usuario no encontrado.
        HTTPException: 500 si hay error interno.
        
    **Ejemplo de uso:**
        ```bash
        curl -X DELETE http://localhost:8000/usuarios/juan_perez
        ```
        
        
        **Respuesta:**
        ```json
        {
            "success": true,
            "message": "Usuario 'juan_perez' eliminado exitosamente"
        }
        ```
        
        Error si es admin:
        ```json
        {
            "success": false,
            "message": "No se puede eliminar un administrador"
        }
        ```
        
    **⚠️ Advertencia:**
        Esta operación es irreversible. Considerar desactivar
        en lugar de eliminar si se necesita mantener historial.
        
    **Nota:**
        Las tareas asignadas al usuario eliminado permanecen en el sistema
        pero aparecerán como asignadas a un usuario inexistente.
    """
    try:
        exito, mensaje = gestor_sistema.eliminar_usuario(nombre)
        
        if not exito:
            raise HTTPException(status_code=400, detail=mensaje)
        
        return BaseResponse(success=True, message=mensaje)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# ENDPOINTS DE AUTENTICACIÓN
# ================================

@app.post("/auth/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Autentica un usuario y devuelve tokens JWT (estándar OAuth2/JWT).
    
    Valida las credenciales del usuario (nombre + contraseña) y, si son correctas,
    genera un par de tokens JWT según el estándar RFC 6749 (OAuth2) y RFC 7519 (JWT):
    - **Access Token**: Token de corta duración para autenticar requests (30 min)
    - **Refresh Token**: Token de larga duración para renovar el access token (7 días)
    
    Flujos posibles:
    1. Login exitoso: Usuario y contraseña correctos - devuelve TokenResponse con JWT
    2. Usuario sin contraseña: Error 401 - debe establecer contraseña inicial vía /auth/set-password
    3. Credenciales inválidas: Error 401 - usuario no existe o contraseña incorrecta
    
    **Parámetros:**
        login_data     : Credenciales del usuario (nombre y contraseña).
        gestor_sistema : Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        TokenResponse: Access token y refresh token JWT.
        
    **Errores:**
        HTTPException: 401 para credenciales inválidas o usuario sin contraseña.
        HTTPException: 500 para errores internos.
        
    **Ejemplo de uso:**
        Login exitoso:
        ```bash
        curl -X POST http://localhost:8000/auth/login \\
             -H "Content-Type: application/json" \\
             -d '{"nombre": "admin", "contraseña": "1234"}'
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
        
    **Nota:**
        Para obtener información del usuario actual después del login,
        use el endpoint /auth/me con el access_token obtenido.
    """
    try:
        logger.debug("/auth/login called for user %s", login_data.nombre)
        usuario, mensaje = gestor_sistema.autenticar_usuario(
            login_data.nombre, 
            login_data.contraseña
        )
        
        if usuario is None:
            # Caso especial: usuario existe pero sin contraseña
            if mensaje == "sin_password":
                raise HTTPException(
                    status_code=401, 
                    detail="Usuario sin contraseña establecida. Use /auth/set-password primero."
                )
            else:
                # Credenciales inválidas
                raise HTTPException(status_code=401, detail=mensaje)
        
        # Login exitoso - Generar tokens JWT reales
        tokens = create_token_response(usuario.nombre, usuario.rol)
        
        return tokens  # Devuelve TokenResponse completo con access_token y refresh_token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@app.post("/auth/set-password", response_model=BaseResponse)
async def establecer_password(
    password_data: PasswordSetRequest,
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Establece la contraseña inicial de un usuario que no tiene contraseña configurada.
    
    Permite a un usuario sin contraseña establecer su primera contraseña
    para poder acceder al sistema de autenticación posteriormente.
    
    **Parámetros:**
        password_data: Datos para establecer contraseña (nombre y contraseña nueva).
        gestor_sistema: Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        BaseResponse: Confirmación de contraseña establecida exitosamente.
        
    **Errores:**
        HTTPException: 400 si el usuario no existe.
        HTTPException: 400 si el usuario ya tiene contraseña establecida.
        HTTPException: 400 si la contraseña no cumple requisitos mínimos.
        HTTPException: 500 para errores internos del servidor.
        
    **Ejemplo de uso:**
        ```bash
        curl -X POST http://localhost:8000/auth/set-password \\
             -H "Content-Type: application/json" \\
             -d '{
                   "nombre": "nuevo_usuario",
                   "contraseña": "mi_password_segura123"
                 }'
        ```
        
        
        **Respuesta:**
        ```json
        {
            "success": true,
            "message": "Contraseña establecida exitosamente para usuario 'nuevo_usuario'"
        }
        ```
        
    **📋 Flujo de trabajo:**
        1. Verificar que el usuario existe en el sistema
        2. Confirmar que NO tiene contraseña previa
        3. Validar requisitos de seguridad de la contraseña
        4. Hashear y guardar la contraseña de forma segura
        
    **🔒 Seguridad:**
        - La contraseña se hashea usando bcrypt antes del almacenamiento
        - Solo usuarios sin contraseña previa pueden usar este endpoint
        - Validaciones de complejidad aplicadas automáticamente
        
    **Nota:**
        Este endpoint es típicamente usado después de la creación de usuario.
        Para cambiar una contraseña existente, use /auth/change-password.
    """
    try:
        exito, mensaje = gestor_sistema.establecer_password_inicial(
            password_data.nombre,
            password_data.contraseña
        )
        
        if not exito:
            raise HTTPException(status_code=400, detail=mensaje)
        
        return BaseResponse(success=True, message=mensaje)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/change-password", response_model=BaseResponse)
async def cambiar_password(
    password_data: PasswordChangeRequest,
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Cambia la contraseña actual de un usuario por una nueva.
    
    Permite a un usuario cambiar su contraseña proporcionando
    la contraseña actual y la nueva contraseña deseada.
    
    **Parámetros:**
        password_data: Datos del cambio de contraseña (usuario, contraseña actual, nueva).
        gestor_sistema: Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        BaseResponse: Confirmación del cambio exitoso.
        
    **Errores:**
        HTTPException: 400 si la contraseña actual es incorrecta.
        HTTPException: 400 si el usuario no existe.
        HTTPException: 400 si las contraseñas no cumplen requisitos.
        HTTPException: 500 para errores internos del servidor.
        
    **Ejemplo de uso:**
        ```bash
        curl -X POST http://localhost:8000/auth/change-password \\
             -H "Content-Type: application/json" \\
             -d '{
                   "nombre": "juan_perez",
                   "contraseña_actual": "password123",
                   "contraseña_nueva": "new_secure_pass456"
                 }'
        ```
        
        
        **Respuesta:**
        ```json
        {
            "success": true,
            "message": "Contraseña cambiada exitosamente"
        }
        ```
        
    **Nota:**
        Requiere que el usuario tenga una contraseña establecida previamente.
        La contraseña actual debe coincidir exactamente para autorizar el cambio.
    """
    try:
        exito, mensaje = gestor_sistema.cambiar_password(
            password_data.nombre,
            password_data.contraseña_actual,
            password_data.contraseña_nueva
        )
        
        if not exito:
            raise HTTPException(status_code=400, detail=mensaje)
        
        return BaseResponse(success=True, message=mensaje)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/reset-password", response_model=BaseResponse)
async def resetear_password(
    reset_data: PasswordResetRequest,
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Resetea la contraseña de un usuario a un valor por defecto (solo administradores).
    
    Permite a un administrador resetear la contraseña de cualquier usuario
    del sistema, estableciendo una contraseña temporal que debe ser cambiada.
    
    **Parámetros:**
        reset_data: Datos del reset (nombre del admin y usuario objetivo).
        gestor_sistema: Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        BaseResponse: Confirmación del reset exitoso con nueva contraseña temporal.
        
    **Errores:**
        HTTPException: 400 si el admin no tiene permisos.
        HTTPException: 400 si el usuario objetivo no existe.
        HTTPException: 400 si el admin no existe o no es administrador.
        HTTPException: 500 para errores internos del servidor.
        
    **Ejemplo de uso:**
        ```bash
        curl -X POST http://localhost:8000/auth/reset-password \\
             -H "Content-Type: application/json" \\
             -d '{
                   "nombre_admin": "admin",
                   "nombre_usuario": "juan_perez"
                 }'
        ```
        
        
        **Respuesta:**
        ```json
        {
            "success": true,
            "message": "Contraseña reseteada. Nueva contraseña temporal: abc123"
        }
        ```
        
    **🔒 Seguridad:**
        - Solo usuarios con rol 'admin' pueden usar este endpoint
        - Se genera una contraseña temporal aleatoria
        - El usuario debe cambiar la contraseña en su próximo login
        
    **⚠️ Advertencia:**
        Operación sensible que debe ser usada con precaución.
        Considere notificar al usuario por medios seguros sobre el reset.
    """
    try:
        exito, mensaje = gestor_sistema.resetear_password_usuario(
            reset_data.nombre_admin,
            reset_data.nombre_usuario
        )
        
        if not exito:
            raise HTTPException(status_code=400, detail=mensaje)
        
        return BaseResponse(success=True, message=mensaje)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: dict,  # {"refresh_token": "..."}
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Renueva el access token usando un refresh token válido.
    
    Permite obtener un nuevo access token sin requerir credenciales,
    usando un refresh token de larga duración previamente obtenido.
    
    **Parámetros:**
        refresh_data: Diccionario con el refresh_token
        gestor_sistema: Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        TokenResponse: Nuevos tokens JWT (access + refresh)
        
    **Errores:**
        HTTPException: 401 si el refresh token es inválido o expirado.
        HTTPException: 400 si falta el refresh_token en el request.
        
    **Ejemplo de uso:**
        ```bash
        curl -X POST http://localhost:8000/auth/refresh \\
             -H "Content-Type: application/json" \\
             -d '{"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."}'
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
        
    **Nota:**
        El refresh token debe ser del tipo 'refresh' y estar firmado correctamente.
        Se generan nuevos access y refresh tokens para rotación de seguridad.
    """
    try:
        refresh_token_str = refresh_data.get("refresh_token")
        if not refresh_token_str:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail      = "Refresh token is required"
            )
        
        # Verificar refresh token (tipo='refresh')
        token_data = verify_token(refresh_token_str, expected_type="refresh")
        
        # Verificar que el usuario aún existe
        usuarios = gestor_sistema.cargar_usuarios()
        usuario  = buscar_usuario_por_nombre(usuarios, token_data.username)
        
        if not usuario:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail      ="User no longer exists"
            )
        
        # Generar nuevos tokens
        new_tokens = create_token_response(usuario.nombre, usuario.rol)
        return new_tokens
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.post("/auth/logout", response_model=BaseResponse)
async def logout(current_user: TokenData = Depends(get_current_user)):
    """Cierra sesión del usuario autenticado.
    
    Endpoint para logout que invalida el token actual.
    En esta implementación básica, simplemente confirma el logout
    ya que los tokens JWT son stateless.
    
    **Parámetros:**
        current_user: Usuario autenticado (inyectado automáticamente).
        
    **Retorna:**
        BaseResponse: Confirmación de logout exitoso.
        
    **Ejemplo de uso:**
        ```bash
        curl -X POST http://localhost:8000/auth/logout \\
             -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
        ```
        
        
        **Respuesta:**
        ```json
        {
            "success": true,
            "message": "Logout successful"
        }
        ```
        
    **Nota:**
        Para logout real con invalidación de tokens, se requeriría
        una blacklist de tokens en base de datos o cache (Redis).
        En esta implementación, el cliente debe descartar el token.
    """
    return BaseResponse(
        success = True,
        message = f"User '{current_user.username}' logged out successfully"
    )


@app.get("/auth/me", response_model=UsuarioResponse)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user)
):
    """Obtiene información del usuario autenticado actual.
    
    Endpoint protegido que devuelve los datos del usuario
    basándose en el token JWT proporcionado.
    
    **Parámetros:**
        current_user: Usuario autenticado (inyectado automáticamente).
        
    **Retorna:**
        UsuarioResponse: Información completa del usuario autenticado.
        
    **Errores:**
        HTTPException: 401 si el token es inválido.
        HTTPException: 404 si el usuario ya no existe en el sistema.
        
    **Ejemplo de uso:**
        ```bash
        curl -X GET http://localhost:8000/auth/me \\
             -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
        ```
        
        
        **Respuesta:**
        ```json
        {
            "nombre": "juan_perez",
            "rol": "user",
            "tiene_password": true
        }
        ```
        
    **Nota:**
        Útil para que aplicaciones frontend verifiquen el estado
        del usuario autenticado y obtengan información actualizada.
    """
    # Obtener información completa del usuario desde el sistema
    try:
        gestor_sistema = get_gestor()
        usuarios       = gestor_sistema.cargar_usuarios()
        usuario        = buscar_usuario_por_nombre(usuarios, current_user.username)
        
        if not usuario:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail      = "User not found in system"
            )
        
        return UsuarioResponse(
            nombre         = usuario.nombre,
            rol            = usuario.rol,
            tiene_password = usuario.tiene_password()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


# ================================
# ENDPOINTS DE TAREAS
# ================================

@app.get("/tareas", response_model=TareaListResponse)
async def listar_tareas(
    current_user: TokenData = Depends(get_current_user),
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Lista todas las tareas del sistema con información completa.
    
    Obtiene una lista de todas las tareas registradas en el sistema,
    incluyendo su estado, usuarios asignados, comentarios y fechas.
    
    **Autenticación requerida:** Token JWT válido en header Authorization.
    
    **Parámetros:**
        current_user: Usuario autenticado obtenido del token JWT.
        gestor_sistema: Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        TareaListResponse: Lista completa de tareas con sus detalles.
        
    **Errores:**
        HTTPException: 401 si el token JWT es inválido o está ausente.
        HTTPException: 500 para errores internos del servidor.
        
    **Ejemplo de uso:**
        ```bash
        curl -X GET "http://localhost:8000/tareas" \
             -H "Authorization: Bearer tu_access_token_aqui"
        ```
        
        
        **Respuesta:**
        ```json
        {
            "tareas": [
                {
                    "nombre": "Implementar login",
                    "descripcion": "Crear sistema de autenticación",
                    "estado": "en_progreso",
                    "fecha_creacion": "2024-01-15",
                    "usuarios_asignados": ["desarrollador1"],
                    "comentarios": [
                        {
                            "comentario": "Iniciando desarrollo",
                            "usuario": "admin",
                            "fecha": "2024-01-15 10:30"
                        }
                    ],
                    "esta_finalizada": false
                }
            ]
        }
        ```
        
    **Nota:**
        Incluye tanto tareas activas como finalizadas.
        Para filtrar por usuario específico, use /tareas/usuario/{nombre}.
    """
    try:
        logger.debug("/tareas called by %s", getattr(current_user, 'username', None))
        tareas = gestor_sistema.cargar_tareas()
        tareas_response = []
        
        for tarea in tareas:
            comentarios_response = [
                {
                    "comentario" : comentario[0],
                    "usuario"    : comentario[1],
                    "fecha"      : comentario[2]
                }
                for comentario in tarea.comentarios
            ]
            
            tareas_response.append(TareaResponse(
                nombre             = tarea.nombre,
                descripcion        = tarea.descripcion,
                estado             = tarea.estado,
                fecha_creacion     = tarea.fecha_creacion,
                usuarios_asignados = tarea.usuarios_asignados,
                comentarios        = comentarios_response,
                esta_finalizada    = tarea.esta_finalizada()
            ))
        
        logger.debug("/tareas returning %s tareas", len(tareas_response))
        return TareaListResponse(tareas = tareas_response)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@app.get("/tareas/{nombre}", response_model=TareaResponse)
async def obtener_tarea(
    nombre: str, 
    current_user: TokenData = Depends(get_current_user),
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Obtiene información detallada de una tarea específica por su nombre.
    
    Recupera todos los detalles de una tarea individual, incluyendo
    descripción, estado, usuarios asignados, comentarios e historial.
    
    **Autenticación requerida:** Token JWT válido en header Authorization.
    
    **Parámetros:**
        nombre         : Nombre único de la tarea a buscar.
        current_user   : Usuario autenticado obtenido del token JWT.
        gestor_sistema : Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        TareaResponse: Información completa de la tarea solicitada.
        
    **Errores:**
        HTTPException: 404 si la tarea no existe.
        HTTPException: 500 para errores internos del servidor.
        
    **Ejemplo de uso:**
        ```bash
        curl -X GET http://localhost:8000/tareas/implementar-login
        ```
        
        
        **Respuesta:**
        ```json
        {
            "nombre": "implementar-login",
            "descripcion": "Crear sistema de autenticación JWT",
            "estado": "completada",
            "fecha_creacion": "2024-01-15",
            "usuarios_asignados": ["desarrollador1", "qa_tester"],
            "comentarios": [
                {
                    "comentario": "JWT implementado correctamente",
                    "usuario": "desarrollador1",
                    "fecha": "2024-01-20 15:45"
                }
            ],
            "esta_finalizada": true
        }
        ```
        
    **Nota:**
        El nombre de la tarea es case-sensitive y debe coincidir exactamente.
    """
    try:
        tareas = gestor_sistema.cargar_tareas()
        tarea  = buscar_tarea_por_nombre(tareas, nombre)
        
        if not tarea:
            raise HTTPException(
                status_code = 404,
                detail      = f"Tarea '{nombre}' no encontrada"
            )
        
        comentarios_response = [
            {
                "comentario" : comentario[0],
                "usuario"    : comentario[1],
                "fecha": comentario[2]
            }
            for comentario in tarea.comentarios
        ]
        
        return TareaResponse(
            nombre             = tarea.nombre,
            descripcion        = tarea.descripcion,
            estado             = tarea.estado,
            fecha_creacion     = tarea.fecha_creacion,
            usuarios_asignados = tarea.usuarios_asignados,
            comentarios        = comentarios_response,
            esta_finalizada    = tarea.esta_finalizada()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@app.get("/tareas/usuario/{nombre_usuario}", response_model=TareaListResponse)
async def obtener_tareas_usuario(
    nombre_usuario: str,
    incluir_finalizadas: bool = True,
    current_user: TokenData = Depends(get_current_user),
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Obtiene todas las tareas asignadas a un usuario específico.
    
    Filtra y devuelve únicamente las tareas donde el usuario especificado
    está asignado, con opción de incluir o excluir tareas finalizadas.
    
    **Autenticación requerida:** Token JWT válido en header Authorization.
    
    **Parámetros:**
        nombre_usuario      : Nombre del usuario para filtrar tareas.
        incluir_finalizadas : Si incluir tareas completadas (default: True).
        current_user        : Usuario autenticado obtenido del token JWT.
        gestor_sistema      : Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        TareaListResponse: Lista de tareas asignadas al usuario.
        
    **Errores:**
        HTTPException: 500 para errores internos del servidor.
        
    **Ejemplo de uso:**
        ```bash
        # Incluir todas las tareas
        curl -X GET http://localhost:8000/tareas/usuario/juan_perez
        
        # Solo tareas activas
        curl -X GET http://localhost:8000/tareas/usuario/juan_perez?incluir_finalizadas=false
        ```
        
        
        **Respuesta:**
        ```json
        {
            "tareas": [
                {
                    "nombre": "revisar-codigo",
                    "descripcion": "Code review del módulo auth",
                    "estado": "pendiente",
                    "fecha_creacion": "2024-01-18",
                    "usuarios_asignados": ["juan_perez"],
                    "comentarios": [],
                    "esta_finalizada": false
                }
            ]
        }
        ```
        
    **Nota:**
        Si el usuario no tiene tareas asignadas, devuelve una lista vacía.
        Útil para dashboards personalizados y vistas de usuario.
    """
    try:
        logger.debug("/tareas/usuario/%s called by %s include_finalizadas=%s", nombre_usuario, getattr(current_user, 'username', None), incluir_finalizadas)
        tareas          = gestor_sistema.obtener_tareas_usuario(nombre_usuario, incluir_finalizadas)
        tareas_response = []
        
        for tarea in tareas:
            comentarios_response = [
                {
                    "comentario" : comentario[0],
                    "usuario"    : comentario[1],
                    "fecha"      : comentario[2]
                }
                for comentario in tarea.comentarios
            ]
            
            tareas_response.append(TareaResponse(
                nombre             = tarea.nombre,
                descripcion        = tarea.descripcion,
                estado             = tarea.estado,
                fecha_creacion     = tarea.fecha_creacion,
                usuarios_asignados = tarea.usuarios_asignados,
                comentarios        = comentarios_response,
                esta_finalizada    = tarea.esta_finalizada()
            ))
        
        return TareaListResponse(tareas=tareas_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tareas", response_model=BaseResponse)
async def crear_tarea(
    tarea_data: TareaCreate,
    current_user: TokenData = Depends(get_current_user),
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Crea una nueva tarea en el sistema con nombre y descripción.
    
    Registra una nueva tarea con estado inicial 'pendiente' y sin
    usuarios asignados. La fecha de creación se asigna automáticamente.
    
    **Autenticación requerida:** Token JWT válido en header Authorization.
    
    **Parámetros:**
        tarea_data      : Datos de la nueva tarea (nombre y descripción).
        current_user    : Usuario autenticado obtenido del token JWT.
        gestor_sistema  : Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        BaseResponse: Confirmación de creación exitosa.
        
    **Errores:**
        HTTPException: 400 si ya existe una tarea con el mismo nombre.
        HTTPException: 400 si los datos de entrada son inválidos.
        HTTPException: 500 para errores internos del servidor.
        
    **Ejemplo de uso:**
        ```bash
        curl -X POST "http://localhost:8000/tareas" \
             -H "Content-Type: application/json" \
             -H "Authorization: Bearer tu_access_token_aqui" \
             -d '{
                   "nombre": "implementar-api-rest",
                   "descripcion": "Crear endpoints REST para gestión de usuarios"
                 }'
        ```
        
        
        **Respuesta:**
        ```json
        {
            "success": true,
            "message": "Tarea 'implementar-api-rest' creada exitosamente"
        }
        ```
        
    **✅ Validaciones:**
        - El nombre debe ser único en el sistema
        - Nombre y descripción no pueden estar vacíos
        - El nombre se normaliza automáticamente
        
    **Nota:**
        Después de crear la tarea, use /tareas/asignar para asignar usuarios.
    """
    try:
        exito, mensaje = gestor_sistema.crear_tarea(tarea_data.nombre, tarea_data.descripcion)
        
        if not exito:
            raise HTTPException(status_code=400, detail=mensaje)
        
        return BaseResponse(success=True, message=mensaje)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tareas/asignar", response_model=BaseResponse)
async def asignar_usuario_tarea(
    asignacion_data: AsignarUsuarioRequest,
    current_user: TokenData = Depends(get_current_user),
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Asigna un usuario específico a una tarea existente.
    
    Añade un usuario a la lista de asignados de una tarea, permitiendo
    múltiples usuarios por tarea. No duplica asignaciones existentes.
    
    **Autenticación requerida:** Token JWT válido en header Authorization.
    
    **Parámetros:**
        asignacion_data : Datos de la asignación (nombre de tarea y usuario).
        current_user    : Usuario autenticado obtenido del token JWT.
        gestor_sistema  : Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        BaseResponse: Confirmación de asignación exitosa.
        
    **Errores:**
        HTTPException: 400 si la tarea no existe.
        HTTPException: 400 si el usuario no existe.
        HTTPException: 400 si el usuario ya está asignado a la tarea.
        HTTPException: 500 para errores internos del servidor.
        
    **Ejemplo de uso:**
        ```bash
        curl -X POST http://localhost:8000/tareas/asignar \\
             -H "Content-Type: application/json" \\
             -d '{
                   "nombre_tarea": "implementar-api-rest",
                   "nombre_usuario": "desarrollador1"
                 }'
        ```
        
        
        **Respuesta:**
        ```json
        {
            "success": true,
            "message": "Usuario 'desarrollador1' asignado a tarea 'implementar-api-rest'"
        }
        ```
        
    **📋 Flujo de trabajo:**
        1. Verificar que la tarea existe
        2. Verificar que el usuario existe
        3. Comprobar que no está ya asignado
        4. Añadir usuario a la lista de asignados
        
    **Nota:**
        Una tarea puede tener múltiples usuarios asignados.
        Use GET /tareas/{nombre} para ver todas las asignaciones actuales.
    """
    try:
        exito, mensaje = gestor_sistema.asignar_usuario_tarea(
            asignacion_data.nombre_tarea,
            asignacion_data.nombre_usuario
        )
        
        if not exito:
            raise HTTPException(status_code=400, detail=mensaje)
        
        return BaseResponse(success=True, message=mensaje)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tareas/desasignar", response_model=BaseResponse)
async def desasignar_usuario_tarea(
    asignacion_data: AsignarUsuarioRequest,
    current_user: TokenData = Depends(get_current_admin),
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Desasigna (quita) un usuario de una tarea existente (solo administradores).
    
    Remueve un usuario de la lista de asignados de una tarea. Solo los
    administradores pueden desasignar usuarios de las tareas.
    
    **Autenticación requerida:** Token JWT válido de administrador.
    
    **Parámetros:**
        asignacion_data : Datos de la desasignación (nombre de tarea y usuario).
        current_user    : Usuario administrador autenticado.
        gestor_sistema  : Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        BaseResponse: Confirmación de desasignación exitosa.
        
    **Errores:**
        HTTPException: 400 si la tarea no existe.
        HTTPException: 400 si el usuario no está asignado a la tarea.
        HTTPException: 403 si el usuario no es administrador.
        HTTPException: 500 para errores internos del servidor.
        
    **Ejemplo de uso:**
        ```bash
        curl -X POST http://localhost:8000/tareas/desasignar \\
             -H "Authorization: Bearer tu_token_admin" \\
             -H "Content-Type: application/json" \\
             -d '{
                   "nombre_tarea": "implementar-api-rest",
                   "nombre_usuario": "desarrollador1"
                 }'
        ```
        
    **Respuesta:**
        ```json
        {
            "success": true,
            "message": "Usuario 'desarrollador1' desasignado de tarea 'implementar-api-rest'"
        }
        ```
    """
    try:
        # Buscar tarea
        tareas = gestor_sistema.cargar_tareas()
        from core.utils import buscar_tarea_por_nombre
        tarea = buscar_tarea_por_nombre(tareas, asignacion_data.nombre_tarea)
        
        if not tarea:
            raise HTTPException(
                status_code=400,
                detail=f"Tarea '{asignacion_data.nombre_tarea}' no encontrada"
            )
        
        # Quitar usuario
        exito = tarea.quitar_usuario(asignacion_data.nombre_usuario)
        
        if not exito:
            raise HTTPException(
                status_code=400,
                detail=f"Usuario '{asignacion_data.nombre_usuario}' no está asignado a la tarea"
            )
        
        # Guardar cambios
        gestor_sistema.guardar_tareas(tareas)
        
        return BaseResponse(
            success=True,
            message=f"Usuario '{asignacion_data.nombre_usuario}' desasignado de tarea '{asignacion_data.nombre_tarea}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tareas/finalizar", response_model=BaseResponse)
async def finalizar_tarea(
    finalizar_data: FinalizarTareaRequest,
    current_user: TokenData = Depends(get_current_user),
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Marca una tarea como finalizada y la mueve al archivo de completadas.
    
    Cambia el estado de una tarea a 'completada' y la transfiere
    al archivo de tareas finalizadas para mantenimiento del historial.
    
    **Autenticación requerida:** Token JWT válido en header Authorization.
    
    **Parámetros:**
        finalizar_data: Datos de finalización (nombre de la tarea).
        current_user: Usuario autenticado obtenido del token JWT.
        gestor_sistema: Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        BaseResponse: Confirmación de finalización exitosa.
        
    **Errores:**
        HTTPException: 400 si la tarea no existe.
        HTTPException: 400 si la tarea ya está finalizada.
        HTTPException: 500 para errores internos del servidor.
        
    **Ejemplo de uso:**
        ```bash
        curl -X POST http://localhost:8000/tareas/finalizar \\
             -H "Content-Type: application/json" \\
             -d '{
                   "nombre_tarea": "implementar-api-rest"
                 }'
        ```
        
        
        **Respuesta:**
        ```json
        {
            "success": true,
            "message": "Tarea 'implementar-api-rest' finalizada exitosamente"
        }
        ```
        
    **⚙️ Proceso:**
        1. Verificar que la tarea existe y está activa
        2. Cambiar estado a 'completada'
        3. Mover tarea a archivo de finalizadas
        4. Remover de archivo de tareas activas
        
    **⚠️ Advertencia:**
        Esta acción no es reversible desde la API.
        La tarea se archiva permanentemente en tareas_finalizadas.json.
        
    **Nota:**
        Las tareas finalizadas se pueden consultar pero no modificar.
    """
    try:
        exito, mensaje = gestor_sistema.finalizar_tarea(finalizar_data.nombre_tarea)
        
        if not exito:
            raise HTTPException(status_code=400, detail=mensaje)
        
        return BaseResponse(success=True, message=mensaje)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tareas/comentario", response_model=BaseResponse)
async def agregar_comentario(
    comentario_data: ComentarioRequest,
    current_user: TokenData = Depends(get_current_user),
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Agrega un comentario con timestamp a una tarea específica.
    
    Permite a los usuarios documentar el progreso, problemas o actualizaciones
    en una tarea mediante comentarios que incluyen autor y fecha automática.
    
    **Autenticación requerida:** Token JWT válido en header Authorization.
    
    **Parámetros:**
        comentario_data: Datos del comentario (tarea, texto, usuario autor).
        current_user: Usuario autenticado obtenido del token JWT.
        gestor_sistema: Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        BaseResponse: Confirmación de comentario agregado exitosamente.
        
    **Errores:**
        HTTPException: 400 si la tarea no existe.
        HTTPException: 400 si el usuario no existe.
        HTTPException: 400 si el comentario está vacío.
        HTTPException: 500 para errores internos del servidor.
        
    **Ejemplo de uso:**
        ```bash
        curl -X POST http://localhost:8000/tareas/comentario \\
             -H "Content-Type: application/json" \\
             -d '{
                   "nombre_tarea": "implementar-api-rest",
                   "comentario": "Endpoints básicos completados, falta documentación",
                   "nombre_usuario": "desarrollador1"
                 }'
        ```
        
        
        **Respuesta:**
        ```json
        {
            "success": true,
            "message": "Comentario agregado a la tarea 'implementar-api-rest'"
        }
        ```
        
    **🎯 Características:**
        - Timestamp automático con fecha y hora actual
        - Historial completo de comentarios por tarea
        - Identificación del autor de cada comentario
        - Soporte para markdown y texto largo
        
    **Nota:**
        Los comentarios se muestran en orden cronológico.
        Use GET /tareas/{nombre} para ver el historial completo.
    """
    try:
        # Log para debugging
        logging.info(f"Agregar comentario - Tarea: {comentario_data.nombre_tarea}, Usuario: {comentario_data.nombre_usuario}, Autenticado como: {current_user.username}")
        
        exito, mensaje = gestor_sistema.agregar_comentario_tarea(
            comentario_data.nombre_tarea,
            comentario_data.comentario,
            comentario_data.nombre_usuario
        )
        
        if not exito:
            logging.warning(f"Fallo al agregar comentario: {mensaje}")
            raise HTTPException(status_code=400, detail=mensaje)
        
        logging.info(f"Comentario agregado exitosamente por {comentario_data.nombre_usuario}")
        return BaseResponse(success=True, message=mensaje)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error inesperado al agregar comentario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/tareas/{nombre}", response_model=BaseResponse)
async def eliminar_tarea(
    nombre: str,
    current_user: TokenData = Depends(get_current_admin),  # Solo administradores pueden eliminar
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Elimina permanentemente una tarea finalizada del sistema (solo administradores).
    
    Permite a los administradores eliminar completamente una tarea finalizada
    del archivo de tareas completadas. Esta operación es irreversible.
    
    **Autenticación requerida:** Token JWT válido de administrador.
    
    **Parámetros:**
        nombre: Nombre exacto de la tarea finalizada a eliminar.
        current_user: Usuario administrador autenticado obtenido del token JWT.
        gestor_sistema: Instancia del gestor inyectada por FastAPI.
        
    **Retorna:**
        BaseResponse: Confirmación de eliminación exitosa.
        
    **Errores:**
        HTTPException: 400 si la tarea no existe.
        HTTPException: 400 si la tarea no está finalizada.
        HTTPException: 403 si el usuario no es administrador.
        HTTPException: 500 para errores internos del servidor.
        
    **Ejemplo de uso:**
        ```bash
        curl -X DELETE http://localhost:8000/tareas/tarea-antigua \\
             -H "Authorization: Bearer tu_access_token_de_admin"
        ```
        
    **⚠️ Advertencia:**
        Esta operación es IRREVERSIBLE. La tarea se elimina permanentemente.
        Solo se pueden eliminar tareas que ya estén finalizadas.
    """
    try:
        logger.info(f"Intentando eliminar tarea finalizada: {nombre}")
        # Buscar la tarea
        tareas = gestor_sistema.cargar_tareas()
        tarea = buscar_tarea_por_nombre(tareas, nombre)
        
        if not tarea:
            logger.warning(f"Tarea no encontrada: {nombre}")
            raise HTTPException(status_code=400, detail=f"Tarea '{nombre}' no encontrada")
        
        # Verificar que esté finalizada
        logger.debug(f"Verificando si tarea está finalizada: esta_finalizada={tarea.esta_finalizada()}")
        if not tarea.esta_finalizada():
            logger.warning(f"Tarea '{nombre}' no está finalizada, no se puede eliminar")
            raise HTTPException(
                status_code=400,
                detail=f"La tarea '{nombre}' debe estar finalizada para poder eliminarse"
            )
        
        # Eliminar la tarea
        logger.info(f"Eliminando tarea: {nombre}")
        exito, mensaje = gestor_sistema.eliminar_tarea(nombre)
        
        if not exito:
            logger.error(f"No se pudo eliminar la tarea '{nombre}': {mensaje}")
            raise HTTPException(
                status_code=400,
                detail=mensaje
            )
        
        logger.info(f"Tarea '{nombre}' eliminada exitosamente")
        return BaseResponse(
            success=True,
            message=mensaje
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar tarea '{nombre}': {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/tareas/{nombre}/reactivar", response_model=BaseResponse)
async def reactivar_tarea(
    nombre: str,
    current_user: TokenData = Depends(get_current_admin),
    gestor_sistema: GestorSistema = Depends(get_gestor)
):
    """Reactiva una tarea finalizada (solo administradores).
    
    Permite a los administradores reactivar una tarea que fue finalizada
    previamente, devolviéndola al estado activo.
    
    **Autenticación requerida:** Token JWT válido de administrador.
    
    **Parámetros:**
        nombre: Nombre exacto de la tarea finalizada a reactivar.
        current_user: Usuario administrador autenticado.
        gestor_sistema: Instancia del gestor.
        
    **Retorna:**
        BaseResponse: Confirmación de reactivación exitosa.
        
    **Errores:**
        HTTPException: 400 si la tarea no existe o no está finalizada.
        HTTPException: 403 si el usuario no es administrador.
        HTTPException: 500 para errores internos.
    """
    try:
        logger.info(f"Intentando reactivar tarea: {nombre}")
        tareas = gestor_sistema.cargar_tareas()
        tarea = buscar_tarea_por_nombre(tareas, nombre)
        
        if not tarea:
            logger.warning(f"Tarea no encontrada: {nombre}")
            raise HTTPException(status_code=400, detail=f"Tarea '{nombre}' no encontrada")
        
        logger.debug(f"Tarea encontrada, verificando estado: esta_finalizada={tarea.esta_finalizada()}")
        if not tarea.esta_finalizada():
            logger.warning(f"Tarea '{nombre}' no está finalizada, no se puede reactivar")
            raise HTTPException(
                status_code=400,
                detail=f"La tarea '{nombre}' no está finalizada"
            )
        
        # Reactivar la tarea
        logger.info(f"Reactivando tarea: {nombre}")
        tarea.activar_tarea()
        gestor_sistema.guardar_tareas(tareas)
        logger.info(f"Tarea '{nombre}' reactivada exitosamente")
        
        return BaseResponse(
            success=True,
            message=f"Tarea '{nombre}' reactivada exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al reactivar tarea '{nombre}': {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# FUNCIÓN PARA EJECUTAR EL SERVIDOR
# ================================

def main():
    """Función principal para ejecutar el servidor de desarrollo.
    
    Configura e inicia el servidor Uvicorn con la aplicación FastAPI.
    Uvicorn es un servidor ASGI de alto rendimiento para aplicaciones async.
    
    Configuración:
        - Host: 0.0.0.0 (acepta conexiones desde cualquier IP)
        - Puerto: 8000 (puerto estándar para desarrollo)
        - Reload: True (recarga automática al detectar cambios)
        - Log level: info (información detallada de requests)
        
    **Nota:**
        Para producción se recomienda:
        - Usar un servidor WSGI como Gunicorn con workers Uvicorn
        - Configurar HTTPS con certificados SSL
        - Establecer host específico en lugar de 0.0.0.0
        - Desactivar reload (reload=False)
        - Configurar logging estructurado
        - Variables de entorno para configuración
        
    **Ejemplo de uso:**
        ```bash
        python api_rest.py
        ```
        
        Salida esperada:
        ```
        🚀 Iniciando API del Sistema de Gestión de Tareas...
        📚 Documentación disponible en: http://localhost:8000/docs
        🔄 API alternativa en: http://localhost:8000/redoc
        ⚡ Health check: http://localhost:8000/health
        INFO: Uvicorn running on http://0.0.0.0:8000
        ```
    """
    print("🚀 Iniciando API del Sistema de Gestión de Tareas...")
    print()
    print("🌐 INTERFAZ WEB:")
    print("   👉 http://localhost:8000/          - Landing page con login")
    print("   📊 http://localhost:8000/dashboard - Dashboard principal")
    print("   👥 http://localhost:8000/admin/users - Panel de administración")
    print()
    print("📚 DOCUMENTACIÓN API:")
    print("   📖 http://localhost:8000/docs   - Swagger UI (modo oscuro)")
    print("   📘 http://localhost:8000/redoc  - ReDoc (alternativa)")
    print("   ⚡ http://localhost:8000/api/health - Health check")
    print()
    print("💡 Para parar el servidor: Ctrl+C")
    print()
    print("🔧 Configuración del servidor:")
    print("   - Host: 0.0.0.0 (todas las interfaces)")
    print("   - Puerto: 8000")
    print("   - Modo: Desarrollo (reload automático)")
    print()
    
    uvicorn.run(
        "api_rest:app",          # Módulo:aplicación
        host="0.0.0.0",          # Bind a todas las interfaces
        port=8000,               # Puerto estándar para desarrollo  
        reload=True,             # Recarga automática en desarrollo
        log_level="info"         # Nivel de logging detallado
    )


if __name__ == "__main__":
    main()