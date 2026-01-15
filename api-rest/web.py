"""Módulo web para la capa HTML de la API REST.

Proporciona rutas que renderizan plantillas Jinja2 (dashboard, fragmentos
de tareas, login, set-password y logout) y utilidades relacionadas.

Incluye el decorador `token_required` que valida el `access_token`
almacenado en cookies y, en caso de expiración, intenta renovar usando el
`refresh_token` vía el endpoint interno `/auth/refresh`.

Las vistas de este módulo usan `TestClient` contra la misma aplicación
para consumir los endpoints de la API interna y obtener información de
usuario y tareas.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
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
# dunciones helpers #
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
# Endpoints administrativos #
############################@

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handler para el formulario de login.

    Envía las credenciales al endpoint interno `/auth/login`. Si el login
    es exitoso guarda `access_token` y `refresh_token` (si existe) en
    cookies HTTP-only y redirige al dashboard. En caso de error renderiza
    la plantilla de login con el mensaje apropiado.

    Args:
        request (Request): Petición entrante.
        username (str): Nombre de usuario desde el formulario.
        password (str): Contraseña desde el formulario.

    Returns:
        TemplateResponse | RedirectResponse: Respuesta que renderiza una
            plantilla o redirige al dashboard.
    """
    # Usar el endpoint interno /auth/login vía TestClient del mismo app
    client = TestClient(request.app)
    resp_api = client.post(
        "/auth/login",
        json={"nombre": username, "contraseña": password}
    )
    logger.debug("web: /auth/login resp status=%s body=%s", resp_api.status_code, resp_api.text[:200])

    if resp_api.status_code == 401:
        detail = resp_api.json().get("detail", "")
        if "sin contraseña" in detail or "sin_password" in detail:
            return templates.TemplateResponse("set_password.html", {"request": request, "username": username})
        return templates.TemplateResponse("index.html", {"request": request, "error": "Credenciales inválidas"})

    if resp_api.status_code != 200:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Error de autenticación"})

    tokens = resp_api.json()
    access = tokens.get("access_token")
    refresh = tokens.get("refresh_token")
    if not access:
        return templates.TemplateResponse("index.html", {"request": request, "error": "No se obtuvo token"})

    resp = RedirectResponse(url='/', status_code=303)
    resp.set_cookie("access_token", access, httponly=True)
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
    logger.debug("web: /auth/set-password status=%s body=%s", resp_api.status_code, resp_api.text[:200])
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


