"""Módulo web para la capa HTML de la API REST.

Este módulo implementa la interfaz web completa del sistema de gestión de tareas
usando Jinja2 para renderizado server-side y HTMX para interactividad dinámica.
Actúa como capa proxy entre el navegador y la API REST interna.

## Arquitectura

El módulo usa el patrón proxy:
1. Navegador envía request con cookies HttpOnly (access_token, refresh_token)
2. web.py extrae tokens de cookies
3. web.py llama a api_rest.py vía TestClient con Authorization headers
4. api_rest.py valida JWT y procesa request
5. web.py recibe respuesta JSON
6. web.py renderiza Jinja2 → retorna HTML al navegador

## Tecnologías

- FastAPI            : Framework ASGI para routing y manejo de requests
- Jinja2             : or de plantillas server-side con herencia y filtros
- HTMX 1.9.2         : Interactividad HTML sin JavaScript complejo
- httpx (TestClient) : Cliente HTTP para llamadas internas
- Cookies HttpOnly   : Almacenamiento seguro de tokens JWT

## Estructura de Endpoints (20 total)

### Landing y Autenticación (4)
- GET  /                    # Landing page con formulario login
- POST /login               # Procesa login, establece cookies HttpOnly
- POST /set-password        # Primera contraseña para usuarios nuevos
- GET  /logout              # Cierra sesión, invalida tokens

### Dashboard y Vistas (4)
- GET /dashboard               # Dashboard principal con tareas del usuario
- GET /tareas/lista            # Lista filtrable de tareas (HTMX)
- GET /tareas/detalle/{nombre} # Vista detallada de tarea con comentarios
- POST /change-password        # Cambiar contraseña desde dashboard

### Panel de Administración (6)
- GET  /admin/users           # Panel gestión de usuarios
- GET  /admin/stats           # Estadísticas del sistema
- POST /admin/create-user     # Crear nuevo usuario
- POST /admin/reset-password  # Resetear contraseña de usuario
- POST /admin/delete-user     # Eliminar usuario
- POST /admin/create-task    # Crear tarea desde admin

### Acciones sobre Tareas (6) - Prefijo /web/
- POST   /web/tareas/comentario         # Agregar comentario (HTMX)
- POST   /web/tareas/asignar            # Asignar usuario a tarea (HTMX)
- POST   /web/tareas/desasignar_usuario  # Quitar usuario de tarea (HTMX)
- POST   /web/tareas/desasignar         # Quitar usuario de tarea (admin, HTMX)
- POST   /web/tareas/finalizar          # Finalizar tarea (admin)
- PUT    /web/tareas/{nombre}/reactivar # Reactivar tarea (admin, HTMX)
- DELETE /web/tareas/{nombre}           # Eliminar tarea finalizada (admin, HTMX)

## Funciones Clave

### Decorador `@token_required`
Valida access_token de cookies, renueva automáticamente si expiró usando
refresh_token, y expone `request.state.user` y `request.state.access_token_current`.
Redirige a / si no puede autenticar.

### Helper `_get_api_client_headers_user(request)`
Extrae token de request.state, crea TestClient, y retorna tupla
(client, headers, user_dict) para hacer llamadas a la API interna.

## Plantillas Jinja2

Ubicadas en `templates/`:
- index.html              # Landing con login
- dashboard.html          # Dashboard principal
- admin_users.html        # Panel administración usuarios
- set_password.html       # Establecer contraseña
- _tareas_fragment.html   # Fragmento HTMX de lista de tareas
- admin_stats.html        # Estadísticas del sistema
- tarea_detalle.html      # Vista detallada de tarea

## Cookies Utilizadas

- access_token  : JWT de corta duración (30 min), HttpOnly, SameSite=Lax
- refresh_token : JWT de larga duración (7 días), HttpOnly, SameSite=Lax

JavaScript no puede leer estas cookies (protección XSS). El navegador las envía
automáticamente en cada request.

## Logging

Usa logger "web" para registrar:
- Intentos de autenticación
- Renovación de tokens
- Errores de validación
- Llamadas a API interna

Nivel: INFO para operaciones normales, DEBUG para detalles, WARNING/ERROR para problemas.

## Dependencias

- fastapi: Framework web
- jinja2: Motor de plantillas
- httpx: Cliente HTTP (vía TestClient)
- jwt_auth: Verificación de tokens JWT

## Uso

Este módulo se registra como router en api_rest.py:
```python
from api-rest.web import router as web_router
app.include_router(web_router)
```

No se ejecuta standalone, sino como parte de la aplicación FastAPI principal.
"""

from fastapi import APIRouter, Request, Form 
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates  # depende de jinja2 pip install jinja2
import os

from jwt_auth import verify_token
import logging
import functools
import asyncio

logger = logging.getLogger("web")
from fastapi.testclient import TestClient

router = APIRouter()

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

#####################
# Funciones helpers #
#####################

# Decorador token_required
def token_required(func):
    """Decorador que asegura la presencia de un token válido para la ruta.

    Args:
        func (callable): Función de ruta FastAPI a decorar.

    Returns:
        callable: Wrapper que valida `access_token`, intenta renovación con
            `refresh_token` si es necesario, y expone `request.state.user`
            y `request.state.access_token_current`. Redirige a `/` si no se
            puede autenticar.
    """

    is_coroutine = asyncio.iscoroutinefunction(func)

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        """Wrapper asíncrono que valida tokens y ejecuta la ruta.

        Busca el objeto `Request` en `args` o `kwargs`, valida el
        `access_token` de las cookies y, si está expirado, intenta renovar
        usando el `refresh_token` llamando a `/auth/refresh` mediante
        `TestClient`. Si la renovación tiene éxito actualiza
        `request.state.user` y `request.state.access_token_current`, setea
        cookies nuevas en la respuesta y devuelve la respuesta de la
        ruta decorada. Si no es posible autenticar redirige a `/`.

        Args:
            *args: Argumentos posicionales de la función decorada.
            **kwargs: Argumentos nombrados de la función decorada.

        Returns:
            Response: Objeto de respuesta de FastAPI (TemplateResponse o RedirectResponse).
        """
        # localizar Request en args o kwargs
        request = None
        for a in args:
            if isinstance(a, Request):
                request = a
                break
        if not request:
            request = kwargs.get("request")

        if not request:
            return RedirectResponse(url='/', status_code=303)

        # si la ruta es pública (landing) permitir ejecutar la vista cuando no hay token
        is_public = str(request.url.path) == "/" or getattr(func, "__name__", "") == "index"
        
        # obtener tokens de cookies
        access = request.cookies.get("access_token")
        
        # obtener refresh token de cookies
        refresh = request.cookies.get("refresh_token")
        
        # crear TestClient para llamadas internas
        client = TestClient(request.app)

        # intentar verificar access token
        if access:
            try:
                # validar access token
                user = verify_token(access)
                # establecer user en request.state
                request.state.user = user
                # establecer access token actual en request.state
                request.state.access_token_current = access
                # llamar a la función decorada
                resp = await func(*args, **kwargs) if is_coroutine else func(*args, **kwargs)
                return resp
            
            except Exception:
                # intentar refresh
                if refresh:
                    try:
                        # llamar a /auth/refresh vía TestClient
                        r = client.post("/auth/refresh", json={"refresh_token": refresh})
                        
                        if r.status_code == 200:
                            tokens = r.json()
                            # obtener nuevos tokens
                            new_access = tokens.get("access_token")
                            new_refresh = tokens.get("refresh_token")
                            # validar nuevo access
                            user = verify_token(new_access)
                            request.state.user = user
                            request.state.access_token_current = new_access
                            resp = await func(*args, **kwargs) if is_coroutine else func(*args, **kwargs)
                            # setear cookies nuevas en la respuesta
                            try:
                                # Si la respuesta es un Response válido, setear cookies
                                resp.set_cookie("access_token", new_access, httponly=True)
                                if new_refresh:
                                    # Actualizar refresh token si se proporcionó uno nuevo
                                    resp.set_cookie("refresh_token", new_refresh, httponly=True)
                            except Exception:
                                # Si la respuesta no es un Response válido, devolverla tal cual
                                return resp
                            return resp
                        # no se pudo renovar: si la ruta es pública ejecutarla, si no redirigir al login
                        else:
                            if is_public:
                                return await func(*args, **kwargs) if is_coroutine else func(*args, **kwargs)
                            return RedirectResponse(url='/', status_code=303)
                    # error en refresh
                    except Exception:
                        if is_public:
                            return await func(*args, **kwargs) if is_coroutine else func(*args, **kwargs)
                        return RedirectResponse(url='/', status_code=303)
                # no hay refresh token o no se pudo renovar: si pública, ejecutar la vista; si no redirigir
                else:
                    if is_public:
                        return await func(*args, **kwargs) if is_coroutine else func(*args, **kwargs)
                    return RedirectResponse(url='/', status_code=303)

        # no hay access token: si la ruta es pública ejecutar la vista, si no redirigir al login
        if is_public:
            return await func(*args, **kwargs) if is_coroutine else func(*args, **kwargs)
        return RedirectResponse(url='/', status_code=303)

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        """Wrapper síncrono que ejecuta `async_wrapper` en el loop.

        Permite decorar funciones síncronas llamando a la versión
        asíncrona (`async_wrapper`) y esperando su resultado en el
        event loop actual.
        """
        return asyncio.run(async_wrapper(*args, **kwargs))

    # devolver el wrapper adecuado según si la función es asíncrona o no
    return async_wrapper if is_coroutine else sync_wrapper

def _get_api_client_headers_user(request: Request):
    """Obtiene `TestClient`, headers de autorización y el usuario actual.

    Esta función encapsula la lógica repetida de construir un
    `TestClient`, armar el header `Authorization` con el token actual
    (considera `request.state.access_token_current` si existe) y
    obtener la información del usuario mediante `/auth/me`.

    Args:
        request (Request): Petición FastAPI que contiene cookies o
            `request.state` con el token renovado.

    Returns:
        tuple(TestClient, dict, dict) | None: Devuelve `(client, headers, user)`
            cuando la autenticación es válida, o `None` si no hay token
            válido o la llamada a `/auth/me` falla.
    """
    token = getattr(request.state, "access_token_current", None) or request.cookies.get("access_token")
    if not token:
        return None

    client = TestClient(request.app)
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/auth/me", headers=headers)
    if me.status_code != 200:
        return None
    user = me.json()
    return client, headers, user

def _get_tareas_for_user(client: TestClient, headers: dict, user: dict):
    """Obtiene la lista de tareas apropiada para el usuario según su rol.

    Para administradores solicita todas las tareas (`/tareas`). Para
    usuarios regulares solicita las tareas del usuario mediante
    `/tareas/usuario/{nombre}`.

    Args:
        client (TestClient): Cliente de prueba usado para llamar a la API interna.
        headers (dict): Headers a incluir en las peticiones (Authorization).
        user (dict): Información del usuario devuelta por `/auth/me`.

    Returns:
        list: Lista de tareas (posible lista vacía si ocurre un error).
    """
    try:
        if user.get("rol") == "admin":
            tareas_resp = client.get("/tareas", headers=headers)
        else:
            nombre = user.get("nombre")
            tareas_resp = client.get(f"/tareas/usuario/{nombre}", headers=headers)

        if tareas_resp.status_code == 200:
            return tareas_resp.json().get("tareas", [])
        return []
    except Exception:
        return []

#############################
# Endpoints administrativos general #
############################

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handler para el formulario de login.

    Envía las credenciales al endpoint interno `/auth/login`. Si el login
    es exitoso guarda `access_token` y `refresh_token` (si existe) en
    cookies HTTP-only y redirige al dashboard usando código 303 (See Other)
    que fuerza una petición GET al destino, evitando reenvío del formulario.
    En caso de error renderiza la plantilla de login con el mensaje apropiado.

    Args:
        request (Request): Petición entrante.
        username (str): Nombre de usuario desde el formulario.
        password (str): Contraseña desde el formulario.

    Returns:
        TemplateResponse | RedirectResponse: Respuesta que renderiza una
            plantilla o redirige al dashboard con código 303.
    """
    # Usar el endpoint interno /auth/login vía TestClient del mismo app
    client = TestClient(request.app)
    resp_api = client.post(
        "/auth/login",
        json={"nombre": username, "contraseña": password}
    )
    logger.debug(f"web: /auth/login resp status={resp_api.status_code} body={resp_api.text[:200]}")
    
    # manejar respuestas
    
    # caso de credenciales inválidas
    if resp_api.status_code == 401:
        resp_json = resp_api.json()
        # Buscar el mensaje en 'detail' o 'message' (depende del formato de respuesta)
        detail = resp_json.get("detail", "") or resp_json.get("message", "")
        # si el error indica que el usuario no tiene contraseña, redirigir a set-password
        if "sin contraseña" in detail or "sin_password" in detail:
            return templates.TemplateResponse("set_password.html", {"request": request, "username": username})
        # otro tipo de error de credenciales
        else:
            return templates.TemplateResponse("index.html", {"request": request, "error": "Credenciales inválidas"})

    # otros errores
    if resp_api.status_code != 200:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Error de autenticación"})
    
    # caso de éxito: obtener tokens y setear cookies
    tokens = resp_api.json()
    access = tokens.get("access_token")
    refresh = tokens.get("refresh_token")
    # asegurar que hay access token
    if not access:
        return templates.TemplateResponse("index.html", {"request": request, "error": "No se obtuvo token"})
    
    # redirigir al dashboard con cookies
    resp = RedirectResponse(url='/', status_code=303)
    resp.set_cookie("access_token", access, httponly=True)
    
    # setear refresh token si existe
    if refresh:
        resp.set_cookie("refresh_token", refresh, httponly=True)
    
    return resp

@router.post("/set-password")
async def set_password(request: Request, username: str = Form(...), password: str = Form(...)):
    """Establece la contraseña para un usuario que no la tiene.

    Llama al endpoint interno `/auth/set-password` y, si tiene éxito,
    realiza un login automático para obtener los tokens y guardarlos en
    cookies HTTP-only.

    Args:
        request (Request): Petición entrante.
        username (str): Nombre de usuario.
        password (str): Nueva contraseña.

    Returns:
        TemplateResponse | RedirectResponse: Renderiza la plantilla de
            set-password en caso de error o redirige al dashboard si todo
            salió bien.
    """
    # Usar endpoint interno /auth/set-password
    client = TestClient(request.app)
    resp_api = client.post(
        "/auth/set-password",
        json={"nombre": username, "contraseña": password}
    )
    logger.debug(f"web: /auth/set-password status={resp_api.status_code} body={resp_api.text[:200]}")
    if resp_api.status_code != 200:
        detail = resp_api.json().get("detail") if resp_api.content else ""
        return templates.TemplateResponse("set_password.html", {"request": request, "username": username, "error": detail or "No se pudo establecer la contraseña"})

    # después de set-password, invocar login para obtener tokens
    resp_login = client.post(
        "/auth/login",
        json={"nombre": username, "contraseña": password}
    )
    if resp_login.status_code != 200:
        return templates.TemplateResponse("set_password.html", {"request": request, "username": username, "error": "Error al iniciar sesión después de establecer la contraseña"})

    tokens = resp_login.json()
    access = tokens.get("access_token")
    refresh = tokens.get("refresh_token")
    resp = RedirectResponse(url='/', status_code=303)
    resp.set_cookie("access_token", access, httponly=True)
    if refresh:
        resp.set_cookie("refresh_token", refresh, httponly=True)
    return resp

@router.post("/change-password")
@token_required
async def change_password_web(request: Request, current_password: str = Form(...), new_password: str = Form(...)):
    """Cambia la contraseña del usuario autenticado.

    Llama al endpoint interno `/auth/change-password` para cambiar la
    contraseña del usuario actual.

    Args:
        request (Request): Petición entrante.
        current_password (str): Contraseña actual.
        new_password (str): Nueva contraseña.

    Returns:
        TemplateResponse | RedirectResponse: Renderiza el dashboard con
            mensaje de éxito o error.
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return RedirectResponse(url='/', status_code=303)

    client, headers, user = res
    
    # Llamar al endpoint de cambio de contraseña
    resp_api = client.post(
        "/auth/change-password",
        json={
            "nombre": user["nombre"],
            "contraseña_actual": current_password,
            "contraseña_nueva": new_password
        }
    )
    
    tareas = _get_tareas_for_user(client, headers, user)
    
    if resp_api.status_code == 200:
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "tareas": tareas,
                "success": "Contraseña cambiada exitosamente"
            }
        )
    else:
        error_detail = resp_api.json().get("detail", "Error al cambiar contraseña")
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "tareas": tareas,
                "error": error_detail
            }
        )

@router.get("/logout")
def logout():
    """Cierra sesión del usuario eliminando cookies de autenticación.

    Elimina `access_token` y `refresh_token` de las cookies y redirige a
    la página de inicio.

    Returns:
        RedirectResponse: Redirección a `/`.
    """
    resp = RedirectResponse(url='/', status_code=303)
    resp.delete_cookie("access_token")
    resp.delete_cookie("refresh_token")
    return resp

#############################
# Endpoints administrativos admin   #
############################

@router.get("/admin/users", response_class=HTMLResponse)
@token_required
async def admin_users(request: Request, page: int = 1, search: str = None):
    """Muestra la lista de usuarios con paginación (solo admins).
    
    Args:
        request (Request): Petición entrante.
        page (int): Número de página.
        search (str): Término de búsqueda opcional.
        
    Returns:
        TemplateResponse: Lista de usuarios paginada.
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return RedirectResponse(url='/', status_code=303)
    
    client, headers, user = res
    
    # Verificar que sea admin
    if user.get("rol") != "admin":
        return RedirectResponse(url='/', status_code=303)
    
    # Llamar al endpoint de usuarios con paginación
    params = {"page": page, "limit": 10}
    if search:
        params["search"] = search
    
    resp = client.get("/usuarios", params=params, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        usuarios = data.get("usuarios", [])
        pagination = data.get("pagination", {})
        return templates.TemplateResponse(
            "admin_users.html",
            {
                "request": request,
                "user": user,
                "usuarios": usuarios,
                "pagination": pagination,
                "search": search or ""
            }
        )
    else:
        return templates.TemplateResponse(
            "admin_users.html",
            {
                "request": request,
                "user": user,
                "usuarios": [],
                "pagination": {},
                "search": search or "",
                "error": "Error al obtener usuarios"
            }
        )

@router.post("/admin/create-user")
@token_required
async def admin_create_user(request: Request, username: str = Form(...), role: str = Form(...), password: str = Form(None)):
    """Crea un nuevo usuario (solo admins).
    
    Args:
        request (Request): Petición entrante.
        username (str): Nombre del usuario.
        role (str): Rol del usuario (user o admin).
        password (str): Contraseña (solo para admins).
        
    Returns:
        RedirectResponse: Redirige al dashboard.
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return RedirectResponse(url='/', status_code=303)
    
    client, headers, user = res
    
    # Verificar que sea admin
    if user.get("rol") != "admin":
        return RedirectResponse(url='/', status_code=303)
    
    # Crear usuario según el rol
    if role == "admin":
        if not password:
            tareas = _get_tareas_for_user(client, headers, user)
            return templates.TemplateResponse(
                "dashboard.html",
                {
                    "request": request,
                    "user": user,
                    "tareas": tareas,
                    "error": "Se requiere contraseña para crear un administrador"
                }
            )
        resp = client.post(
            "/usuarios/admin",
            json={"nombre": username, "contraseña": password},
            headers=headers
        )
    else:
        resp = client.post(
            "/usuarios",
            json={"nombre": username},
            headers=headers
        )
    
    tareas = _get_tareas_for_user(client, headers, user)
    
    if resp.status_code == 200:
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "tareas": tareas,
                "success": f"Usuario '{username}' creado exitosamente"
            }
        )
    else:
        error_detail = resp.json().get("detail", "Error al crear usuario")
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "tareas": tareas,
                "error": error_detail
            }
        )

@router.post("/admin/reset-password")
@token_required
async def admin_reset_password(request: Request, username: str = Form(...)):
    """Resetea la contraseña de un usuario (solo admins).
    
    Args:
        request (Request): Petición entrante.
        username (str): Nombre del usuario a resetear.
        
    Returns:
        TemplateResponse: Dashboard con mensaje de éxito/error.
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return RedirectResponse(url='/', status_code=303)
    
    client, headers, user = res
    
    # Verificar que sea admin
    if user.get("rol") != "admin":
        return RedirectResponse(url='/', status_code=303)
    
    # Llamar al endpoint de reset password
    resp = client.post(
        "/auth/reset-password",
        json={
            "nombre_admin": user["nombre"],
            "nombre_usuario": username
        },
        headers=headers
    )
    
    if resp.status_code == 200:
        # Redirigir a la página de usuarios con mensaje de éxito
        return RedirectResponse(url=f'/admin/users?reset_success={username}', status_code=303)
    else:
        error_detail = resp.json().get("detail", "Error al resetear contraseña")
        return RedirectResponse(url=f'/admin/users?reset_error={error_detail}', status_code=303)

@router.post("/admin/delete-user")
@token_required
async def admin_delete_user(request: Request, username: str = Form(...)):
    """Elimina un usuario (solo admins).
    
    Args:
        request (Request): Petición entrante.
        username (str): Nombre del usuario a eliminar.
        
    Returns:
        RedirectResponse: Redirige a la lista de usuarios.
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return RedirectResponse(url='/', status_code=303)
    
    client, headers, user = res
    
    # Verificar que sea admin
    if user.get("rol") != "admin":
        return RedirectResponse(url='/', status_code=303)
    
    # Llamar al endpoint de eliminación
    resp = client.delete(f"/usuarios/{username}", headers=headers)
    
    if resp.status_code == 200:
        return RedirectResponse(url=f'/admin/users?delete_success={username}', status_code=303)
    else:
        error_detail = resp.json().get("detail", "Error al eliminar usuario")
        return RedirectResponse(url=f'/admin/users?delete_error={error_detail}', status_code=303)

@router.get("/admin/stats", response_class=HTMLResponse)
@token_required
async def admin_stats(request: Request):
    """Muestra las estadísticas del sistema (solo admins).
    
    Args:
        request (Request): Petición entrante.
        
    Returns:
        TemplateResponse: Página con estadísticas del sistema.
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return RedirectResponse(url='/', status_code=303)
    
    client, headers, user = res
    
    # Verificar que sea admin
    if user.get("rol") != "admin":
        return RedirectResponse(url='/', status_code=303)
    
    # Llamar al endpoint de estadísticas
    resp = client.get("/stats", headers=headers)
    
    if resp.status_code == 200:
        stats = resp.json()
        return templates.TemplateResponse(
            "admin_stats.html",
            {
                "request": request,
                "user": user,
                "stats": stats
            }
        )
    else:
        return templates.TemplateResponse(
            "admin_stats.html",
            {
                "request": request,
                "user": user,
                "error": "Error al obtener estadísticas"
            }
        )

#############################
# Endpoints tareas  admin   #
############################

@router.post("/admin/create-task")
@token_required
async def admin_create_task(request: Request, nombre: str = Form(...), descripcion: str = Form(...)):
    """Crea una nueva tarea (solo admins).
    
    Args:
        request (Request): Petición entrante.
        nombre (str): Nombre de la tarea.
        descripcion (str): Descripción de la tarea.
        
    Returns:
        RedirectResponse: Redirige al dashboard.
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return RedirectResponse(url='/', status_code=303)
    
    client, headers, user = res
    
    # Verificar que sea admin
    if user.get("rol") != "admin":
        return RedirectResponse(url='/', status_code=303)
    
    # Crear tarea
    resp = client.post(
        "/tareas",
        json={"nombre": nombre, "descripcion": descripcion},
        headers=headers
    )
    
    tareas = _get_tareas_for_user(client, headers, user)
    
    if resp.status_code == 200:
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "tareas": tareas,
                "success": f"Tarea '{nombre}' creada exitosamente"
            }
        )
    else:
        error_detail = resp.json().get("detail", "Error al crear tarea")
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "tareas": tareas,
                "error": error_detail
            }
        )

##########################
# Endpoints de la UI web #
##########################

@router.get("/", response_class=HTMLResponse)
@token_required
def index(request: Request):
    """Página de inicio / landing.

    Si el usuario está autenticado muestra el `dashboard.html` con las tareas
    adecuadas (usa la API interna vía `TestClient`). Si no hay token válido
    renderiza la página de login `index.html`.

    Args:
        request (Request): Petición de FastAPI.

    Returns:
        TemplateResponse: Plantilla renderizada para la UI.
    """
    # usar API interna para obtener user y tareas (evitar usar gestor directamente)
    res = _get_api_client_headers_user(request)
    if res:
        client, headers, user = res
        tareas = _get_tareas_for_user(client, headers, user)
        return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "tareas": tareas})
    else:
        # landing/login
        return templates.TemplateResponse("index.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
@token_required
def dashboard(request: Request):
    """Renderiza el dashboard del usuario autenticado.

    Obtiene la identidad del usuario y las tareas usando los endpoints
    internos de la API. Usa `request.state.access_token_current` si el
    decorador renueva el token; en caso contrario lee el token de las
    cookies.

    Args:
        request (Request): Petición de FastAPI; `request.state.user` estará
            disponible cuando el decorador haya validado el token.

    Returns:
        TemplateResponse | RedirectResponse: Plantilla del dashboard o
            redirección al login si no es posible autenticar.
    """
    # Obtener user y tareas desde la API interna
    res = _get_api_client_headers_user(request)
    if not res:
        return RedirectResponse(url='/', status_code=303)

    client, headers, user = res
    tareas = _get_tareas_for_user(client, headers, user)

    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "tareas": tareas})

@router.get("/tareas/lista", response_class=HTMLResponse)
@token_required
def tareas_lista(request: Request):
    """Devuelve el fragmento HTML con la lista de tareas del usuario.

    Consulta la API interna para obtener el usuario autenticado y filtra
    las tareas que correspondan. Si no está autenticado renderiza un
    fragmento vacío que muestra el formulario de login.

    Args:
        request (Request): Petición de FastAPI; el usuario autenticado se
            puede leer en `request.state.user` cuando el decorador lo
            haya establecido.

    Returns:
        TemplateResponse: Fragmento HTML `_tareas_fragment.html` con las
            tareas (posiblemente vacío si no hay autenticación).
    """
    # devuelve fragmento de tareas del usuario si autenticado; usa API interna
    res = _get_api_client_headers_user(request)
    if not res:
        # usuario no autenticado: pedir login en el fragmento
        return templates.TemplateResponse("_tareas_fragment.html", {"request": request, "tareas": []})

    client, headers, user = res
    tareas = _get_tareas_for_user(client, headers, user)
    return templates.TemplateResponse("_tareas_fragment.html", {"request": request, "tareas": tareas})

@router.get("/tareas/detalle/{nombre_tarea}", response_class=HTMLResponse)
@token_required
async def tarea_detalle(
    request: Request,
    nombre_tarea: str,
    usuario_filter: str = None,
    fecha_desde: str = None,
    fecha_hasta: str = None
):
    """Muestra la vista detallada de una tarea específica.
    
    Incluye información completa de la tarea, historial de comentarios
    con capacidad de filtrado, y funciones administrativas si el usuario
    es admin.
    
    Args:
        request (Request): Petición entrante.
        nombre_tarea (str): Nombre de la tarea a mostrar.
        usuario_filter (str, opcional): Filtrar comentarios por usuario.
        fecha_desde (str, opcional): Filtrar comentarios desde fecha.
        fecha_hasta (str, opcional): Filtrar comentarios hasta fecha.
        
    Returns:
        TemplateResponse: Vista detallada de la tarea.
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return RedirectResponse(url='/', status_code=303)

    client, headers, user = res
    
    # Obtener detalles de la tarea
    resp_tarea = client.get(f"/tareas/{nombre_tarea}", headers=headers)
    
    if resp_tarea.status_code != 200:
        return RedirectResponse(url='/', status_code=303)
    
    tarea = resp_tarea.json()
    
    # Obtener todos los usuarios para el filtro y asignación (solo admin)
    # Hace paginación automática para obtener todos los usuarios
    usuarios = []
    if user.get("rol") == "admin":
        logger.debug(f"Usuario admin, obteniendo lista completa de usuarios con paginación")
        page = 1
        while True:
            resp_usuarios = client.get("/usuarios", params={"limit": 100, "page": page}, headers=headers)
            logger.debug(f"Respuesta /usuarios página {page}: status={resp_usuarios.status_code}")
            
            if resp_usuarios.status_code == 200:
                usuarios_data = resp_usuarios.json()
                usuarios_pagina = usuarios_data.get("usuarios", [])
                usuarios.extend(usuarios_pagina)
                
                # Verificar si hay más páginas
                pagination = usuarios_data.get("pagination", {})
                total_pages = pagination.get("total_pages", 1)
                logger.debug(f"Página {page}/{total_pages}, obtenidos {len(usuarios_pagina)} usuarios")
                
                if page >= total_pages:
                    break
                page += 1
            else:
                logger.warning(f"Error al obtener usuarios página {page}: {resp_usuarios.status_code} - {resp_usuarios.text}")
                break
        
        logger.info(f"Se obtuvieron {len(usuarios)} usuarios en total para el select")
    else:
        logger.debug(f"Usuario no es admin, no se cargan usuarios para select")
    
    # Filtrar comentarios si se proporcionan filtros
    comentarios = tarea.get("comentarios", [])
    comentarios_filtrados = comentarios.copy()
    
    # Aplicar filtros
    if usuario_filter:
        comentarios_filtrados = [
            c for c in comentarios_filtrados 
            if c.get("usuario", "").lower() == usuario_filter.lower()
        ]
    
    if fecha_desde:
        try:
            from datetime import datetime
            fecha_desde_dt = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
            comentarios_filtrados = [
                c for c in comentarios_filtrados
                if datetime.fromisoformat(c.get("fecha", "").replace('Z', '+00:00')) >= fecha_desde_dt
            ]
        except:
            pass
    
    if fecha_hasta:
        try:
            from datetime import datetime
            fecha_hasta_dt = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
            comentarios_filtrados = [
                c for c in comentarios_filtrados
                if datetime.fromisoformat(c.get("fecha", "").replace('Z', '+00:00')) <= fecha_hasta_dt
            ]
        except:
            pass
    
    # Ordenar por fecha (más recientes primero)
    comentarios_filtrados.sort(
        key=lambda x: x.get("fecha", ""),
        reverse=True
    )
    
    return templates.TemplateResponse(
        "tarea_detalle.html",
        {
            "request": request,
            "user": user,
            "tarea": tarea,
            "comentarios": comentarios_filtrados,
            "usuarios": usuarios,
            "usuario_filter": usuario_filter,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        }
    )


# ================================
# ENDPOINTS DE ACCIÓN SOBRE TAREAS
# ================================

@router.post("/web/tareas/comentario")
@token_required
async def agregar_comentario_web(request: Request):
    """Agregar comentario a una tarea desde la interfaz web.
    
    Endpoint proxy que recibe datos JSON desde HTMX, extrae el token de cookies,
    y llama a la API interna POST /tareas/comentario.
    
    **Autenticación:** Cookies HttpOnly (access_token)
    
    **Request Body (JSON):**
        - nombre_tarea (str): Nombre de la tarea
        - comentario (str): Texto del comentario
    
    **Returns:**
        JSONResponse: Resultado de la API con status code correspondiente
        
    **Errors:**
        - 401: No autenticado
        - 400: Datos inválidos o tarea no encontrada
        - 500: Error interno
    """
    res = _get_api_client_headers_user(request)
    if not res:
        logger.warning("agregar_comentario_web: No se pudo autenticar usuario")
        return JSONResponse({"detail": "No autorizado"}, status_code=401)
    
    client, headers, user = res
    
    # Obtener datos del formulario JSON
    data = await request.json()
    logger.info(f"agregar_comentario_web: Usuario {user.get('nombre')} ({user.get('rol')}) agregando comentario a '{data.get('nombre_tarea')}'")
    logger.debug(f"agregar_comentario_web: Payload completo: {data}")
    
    # Llamar a la API interna
    resp = client.post("/tareas/comentario", headers=headers, json=data)
    logger.debug(f"agregar_comentario_web: Respuesta API status={resp.status_code}")
    
    try:
        resp_json = resp.json()
        logger.debug(f"agregar_comentario_web: Respuesta body={resp_json}")
    except Exception as e:
        logger.error(f"agregar_comentario_web: Error parseando respuesta JSON: {e}")
        return JSONResponse({"detail": "Error interno del servidor"}, status_code=500)
    
    if resp.status_code == 200:
        logger.info(f"agregar_comentario_web: Comentario agregado exitosamente")
        return JSONResponse(resp_json)
    else:
        logger.warning(f"agregar_comentario_web: Error al agregar comentario: {resp_json}")
        return JSONResponse(resp_json, status_code=resp.status_code)


@router.post("/web/tareas/asignar")
@token_required
async def asignar_usuario_web(request: Request):
    """Asignar usuario a una tarea desde la interfaz web.
    
    Endpoint proxy que recibe datos JSON desde HTMX, extrae el token de cookies,
    y llama a la API interna POST /tareas/asignar.
    
    **Autenticación:** Cookies HttpOnly (access_token)
    
    **Request Body (JSON):**
        - nombre_tarea (str): Nombre de la tarea
        - nombre_usuario (str): Nombre del usuario a asignar
    
    **Returns:**
        JSONResponse: Resultado de la API con status code correspondiente
        
    **Errors:**
        - 401: No autenticado
        - 400: Tarea o usuario no encontrado
        - 500: Error interno
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return JSONResponse({"detail": "No autorizado"}, status_code=401)
    
    client, headers, user = res
    
    # Verificar que sea admin
    if user.get("rol") != "admin":
        return JSONResponse({"detail": "Acceso denegado"}, status_code=403)
    
    # Obtener datos del formulario JSON
    data = await request.json()
    
    # Llamar a la API interna
    resp = client.post("/tareas/asignar", headers=headers, json=data)
    
    if resp.status_code == 200:
        return JSONResponse(resp.json())
    else:
        return JSONResponse(resp.json(), status_code=resp.status_code)


@router.post("/web/tareas/desasignar")
@token_required
async def desasignar_usuario_web(request: Request):
    """Desasignar (quitar) usuario de una tarea desde la interfaz web (solo administradores).
    
    Endpoint proxy que recibe datos JSON desde HTMX, valida que el usuario sea admin,
    extrae el token de cookies, y llama a la API interna POST /tareas/desasignar.
    
    **Autenticación:** Cookies HttpOnly (access_token) + rol admin
    
    **Request Body (JSON):**
        - nombre_tarea (str): Nombre de la tarea
        - nombre_usuario (str): Nombre del usuario a desasignar
    
    **Returns:**
        JSONResponse: Resultado de la API con status code correspondiente
        
    **Errors:**
        - 401: No autenticado
        - 403: No es administrador
        - 400: Tarea no encontrada o usuario no asignado
        - 500: Error interno
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return JSONResponse({"detail": "No autorizado"}, status_code=401)
    
    client, headers, user = res
    
    # Verificar que sea admin
    if user.get("rol") != "admin":
        return JSONResponse({"detail": "Acceso denegado"}, status_code=403)
    
    # Obtener datos del JSON
    data = await request.json()
    
    # Llamar a la API interna
    resp = client.post("/tareas/desasignar", headers=headers, json=data)
    
    if resp.status_code == 200:
        return JSONResponse(resp.json())
    else:
        return JSONResponse(resp.json(), status_code=resp.status_code)


@router.post("/web/tareas/finalizar")
@token_required
async def finalizar_tarea_web(request: Request):
    """Finalizar una tarea desde la interfaz web (solo administradores).
    
    Endpoint que recibe datos de formulario, valida que el usuario sea admin,
    extrae el token de cookies, y llama a la API interna POST /tareas/finalizar.
    Redirige de vuelta a la página de detalle de la tarea.
    
    **Autenticación:** Cookies HttpOnly (access_token) + rol admin
    
    **Form Data:**
        - nombre_tarea (str): Nombre de la tarea a finalizar
    
    **Returns:**
        RedirectResponse: Redirección a /tareas/detalle/{nombre_tarea}
        
    **Errors:**
        - 303: Redirect a / si no autenticado o no es admin
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return RedirectResponse(url='/', status_code=303)
    
    client, headers, user = res
    
    # Verificar que sea admin
    if user.get("rol") != "admin":
        return RedirectResponse(url='/', status_code=303)
    
    # Obtener datos del formulario
    form_data = await request.form()
    nombre_tarea = form_data.get("nombre_tarea")
    
    # Llamar a la API interna
    resp = client.post(
        "/tareas/finalizar",
        headers=headers,
        json={"nombre_tarea": nombre_tarea}
    )
    
    # Redirigir de vuelta a la vista de detalle
    return RedirectResponse(url=f'/tareas/detalle/{nombre_tarea}', status_code=303)


@router.put("/web/tareas/{nombre_tarea}/reactivar")
@token_required
async def reactivar_tarea_web(request: Request, nombre_tarea: str):
    """Reactivar una tarea finalizada (solo administradores).
    
    Endpoint proxy que valida que el usuario sea admin, extrae el token de cookies,
    y llama a la API interna PUT /tareas/{nombre}/reactivar para cambiar el estado
    de la tarea de finalizada a pendiente.
    
    **Autenticación:** Cookies HttpOnly (access_token) + rol admin
    
    **Path Parameters:**
        - nombre_tarea (str): Nombre de la tarea a reactivar
    
    **Returns:**
        JSONResponse: {success: true, message: "Tarea reactivada exitosamente"}
        
    **Errors:**
        - 401: No autenticado
        - 403: No es administrador
        - 400: Tarea no encontrada o no está finalizada
        - 500: Error interno
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return JSONResponse({"detail": "No autorizado"}, status_code=401)
    
    client, headers, user = res
    
    # Verificar que sea admin
    if user.get("rol") != "admin":
        return JSONResponse({"detail": "Acceso denegado"}, status_code=403)
    
    # Llamar a la API interna
    resp = client.put(f"/tareas/{nombre_tarea}/reactivar", headers=headers)
    
    if resp.status_code == 200:
        return JSONResponse(resp.json())
    else:
        return JSONResponse(resp.json(), status_code=resp.status_code)


@router.delete("/web/tareas/{nombre_tarea}")
@token_required
async def eliminar_tarea_web(request: Request, nombre_tarea: str):
    """Eliminar permanentemente una tarea finalizada (solo administradores).
    
    Endpoint proxy que valida que el usuario sea admin, extrae el token de cookies,
    y llama a la API interna DELETE /tareas/{nombre} para eliminar permanentemente
    una tarea que esté en estado finalizada. Esta acción es IRREVERSIBLE.
    
    **Autenticación:** Cookies HttpOnly (access_token) + rol admin
    
    **Path Parameters:**
        - nombre_tarea (str): Nombre de la tarea a eliminar
    
    **Returns:**
        JSONResponse: {success: true, message: "Tarea eliminada permanentemente"}
        
    **Errors:**
        - 401: No autenticado
        - 403: No es administrador
        - 400: Tarea no encontrada o no está finalizada
        - 500: Error interno
        
    **⚠️ Advertencia:**
        Esta operación elimina la tarea de forma permanente.
        Solo se pueden eliminar tareas finalizadas.
    """
    res = _get_api_client_headers_user(request)
    if not res:
        return JSONResponse({"detail": "No autorizado"}, status_code=401)
    
    client, headers, user = res
    
    # Verificar que sea admin
    if user.get("rol") != "admin":
        return JSONResponse({"detail": "Acceso denegado"}, status_code=403)
    
    # Llamar a la API interna
    resp = client.delete(f"/tareas/{nombre_tarea}", headers=headers)
    
    if resp.status_code == 200:
        return JSONResponse(resp.json())
    else:
        return JSONResponse(resp.json(), status_code=resp.status_code)

