from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

from jwt_auth import verify_token
import logging

logger = logging.getLogger("web")
from fastapi.testclient import TestClient

router = APIRouter()

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


def _validate_token_from_request(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        info = verify_token(token)
        return info
    except Exception:
        return None


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    # usar API interna para obtener user y tareas (evitar usar gestor directamente)
    token = request.cookies.get("access_token")
    if token:
        client = TestClient(request.app)
        headers = {"Authorization": f"Bearer {token}"}
        logger.debug("web: requesting /auth/me with token present (len=%s)", len(token))
        me = client.get("/auth/me", headers=headers)
        logger.debug("web: /auth/me status=%s body=%s", me.status_code, me.text[:200])
        if me.status_code == 200:
            user = me.json()
            if user.get("rol") == "admin":
                logger.debug("es admin, no filtrar tareas")
                tareas_resp = client.get("/tareas", headers=headers)
                logger.debug("web: /tareas status=%s body_len=%s", tareas_resp.status_code, len(tareas_resp.text))
            else:
                tareas_resp = client.get(f"/tareas/usuario/{user.get('nombre')}", headers=headers)
            tareas = []
            if tareas_resp.status_code == 200:
                tareas = tareas_resp.json().get("tareas", [])
                # filtrar tareas del usuario
                # tareas = [t for t in tareas if user.get("nombre") in t.get("usuarios_asignados", [])]
            return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "tareas": tareas})

    # landing/login
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
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
    if not access:
        return templates.TemplateResponse("index.html", {"request": request, "error": "No se obtuvo token"})

    resp = RedirectResponse(url='/', status_code=303)
    resp.set_cookie("access_token", access, httponly=True)
    return resp


@router.post("/set-password")
async def set_password(request: Request, username: str = Form(...), password: str = Form(...)):
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
    resp = RedirectResponse(url='/', status_code=303)
    resp.set_cookie("access_token", access, httponly=True)
    return resp


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    # Obtener user y tareas desde la API interna
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(url='/', status_code=303)

    client = TestClient(request.app)
    headers = {"Authorization": f"Bearer {token}"}
    logger.debug("web: dashboard requesting /auth/me")
    me = client.get("/auth/me", headers=headers)
    logger.debug("web: dashboard /auth/me status=%s", me.status_code)
    if me.status_code != 200:
        return RedirectResponse(url='/', status_code=303)

    user = me.json()
    if user.get("rol") == "admin":
        logger.debug("es admin, no filtrar tareas")
        tareas_resp = client.get("/tareas", headers=headers)
        logger.debug("web: dashboard /tareas status=%s", tareas_resp.status_code)
        logger.debug("web: dashboard /tareas body_len=%s", len(tareas_resp.text))
    
    else:
        tareas_resp = client.get(f"/tareas/usuario/{user.get('nombre')}", headers=headers)
    tareas = []
    if tareas_resp.status_code == 200:
        tareas = tareas_resp.json().get("tareas", [])
        # tareas = [t for t in tareas if user.get("nombre") in t.get("usuarios_asignados", [])]

    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "tareas": tareas})

@router.get("/tareas/lista", response_class=HTMLResponse)
def tareas_lista(request: Request):
    # devuelve fragmento de tareas del usuario si autenticado; usa API interna
    token = request.cookies.get("access_token")
    if token:
        client = TestClient(request.app)
        headers = {"Authorization": f"Bearer {token}"}
        me = client.get("/auth/me", headers=headers)
        logger.debug("web: tareas_lista /auth/me status=%s", me.status_code)
        if me.status_code == 200:
            user = me.json()
            tareas_resp = client.get("/tareas", headers=headers)
            logger.debug("web: tareas_lista /tareas status=%s body_len=%s", tareas_resp.status_code, len(tareas_resp.text))
            tareas = []
            if tareas_resp.status_code == 200:
                tareas = tareas_resp.json().get("tareas", [])
                tareas = [t for t in tareas if user.get("nombre") in t.get("usuarios_asignados", [])]
            return templates.TemplateResponse("_tareas_fragment.html", {"request": request, "tareas": tareas})

    # usuario no autenticado: pedir login en el fragmento
    return templates.TemplateResponse("_tareas_fragment.html", {"request": request, "tareas": []})


@router.get("/logout")
def logout():
    resp = RedirectResponse(url='/', status_code=303)
    resp.delete_cookie("access_token")
    return resp