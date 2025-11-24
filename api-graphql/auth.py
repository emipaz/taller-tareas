"""
Autenticación JWT para GraphQL

Este módulo proporciona middleware y utilidades para manejar autenticación
y autorización JWT en GraphQL, reutilizando el sistema JWT existente
del módulo api-rest.

Clases principales:
    - AuthenticationError : Excepción para errores de autenticación
    - AuthorizationError  : Excepción para errores de permisos
    - IsAuthenticated     : Permiso que requiere autenticación
    - IsAdmin             : Permiso que requiere rol de administrador
    
Funciones principales:
    - get_current_user           : Obtiene usuario actual desde token JWT
    - extract_token_from_request : Extrae token de headers HTTP
"""

import sys
import os
from typing import Optional

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import strawberry
    from strawberry.permission import BasePermission
    from strawberry.types import Info
    from fastapi import Request, HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    import jwt
except ImportError:
    # Para desarrollo sin dependencias instaladas
    pass

# Importar JWT auth desde jwt_auth.py directamente
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api-rest'))
from jwt_auth import verify_token, JWTConfig, TokenData
import jwt


class AuthenticationError(Exception):
    """Excepción lanzada cuando falla la autenticación de usuario.
    
    Esta excepción se lanza cuando:
    - No se proporciona un token JWT válido
    - El token ha expirado
    - El token está mal formado o es inválido
    - El usuario del token no existe en el sistema
    
    Example:
        if not token:
            raise AuthenticationError("Token no proporcionado")
    """
    pass


class AuthorizationError(Exception):
    """Excepción lanzada cuando falla la autorización de usuario.
    
    Esta excepción se lanza cuando:
    - El usuario está autenticado pero no tiene permisos suficientes
    - Se intenta acceder a recursos que requieren rol de administrador
    - Se viola alguna regla de negocio de permisos
    
    Example:
        if user.rol != "admin":
            raise AuthorizationError("Se requieren permisos de administrador")
    """
    pass


security = HTTPBearer()


def get_current_user(request: Optional[Request]) -> Optional[dict]:
    """Obtiene el usuario actual desde el token JWT en el request HTTP.
    
    Esta función extrae y valida el token JWT del header Authorization,
    decodifica la información del usuario y retorna sus datos.
    
    Args:
        request (Optional[Request]): Request de FastAPI que contiene:
            - Headers HTTP incluyendo Authorization
            - Cookies de sesión
            - Otros datos de contexto de la petición
            
    Returns:
        Optional[dict]: Datos del usuario decodificados del token conteniendo:
            - sub: Identificador del usuario (username)
            - rol: Rol del usuario (admin/usuario)
            - exp: Timestamp de expiración
            - otros claims del JWT
            
    Raises:
        AuthenticationError: En los siguientes casos:
            - Request no disponible
            - Token de autorización no presente
            - Formato de token inválido (no Bearer)
            - Token JWT malformado o expirado
            - Usuario no encontrado en el sistema
            
    Example:
        try:
            user = get_current_user(request)
            if user['rol'] == 'admin':
                # Usuario con permisos de administrador
                pass
        except AuthenticationError:
            # Manejar error de autenticación
            pass
            
    Note:
        Esta función reutiliza el sistema JWT del módulo api-rest
        para mantener consistencia entre GraphQL y REST API.
    """
    if not request:
        raise AuthenticationError("Request no disponible")
    
    # Obtener token del header Authorization
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise AuthenticationError("Token de autorización requerido")
    
    # Extraer esquema y token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise AuthenticationError("Esquema de autorización inválido")
    except ValueError:
        raise AuthenticationError("Formato de autorización inválido")
    
    try:
        # Usar la función verify_token del módulo jwt_auth
        token_data = verify_token(token, "access")
        
        # Obtener el username del token
        username = token_data.username
        
        if not username:
            raise AuthenticationError("Token inválido")
            
        # Crear un objeto usuario básico (esto se puede mejorar)
        # Por ahora retornamos un dict simple con la información del token
        return {
            "username": username,
            "role": getattr(token_data, 'role', 'user'),
            "token_type": getattr(token_data, 'token_type', 'access')
        }
        
    except jwt.InvalidTokenError:
        raise AuthenticationError("Token JWT inválido")
    except Exception as e:
        raise AuthenticationError(f"Error de autenticación: {str(e)}")


class IsAuthenticated(BasePermission):
    """Permiso de GraphQL que requiere autenticación de usuario.
    
    Esta clase de permiso verifica que el usuario tenga un token
    JWT válido en el header Authorization. Se aplica a campos
    y mutaciones que requieren que el usuario esté logueado.
    
    Attributes:
        message (str): Mensaje de error mostrado cuando falla el permiso.
        
    Example:
        @strawberry.field(permission_classes=[IsAuthenticated])
        def datos_usuario(self, info: Info) -> Usuario:
            # Solo usuarios autenticados pueden acceder
            return get_user_data(info)
            
    Note:
        Este permiso no verifica roles específicos, solo autenticación.
        Para verificar roles use IsAdmin o implemente permisos personalizados.
    """
    
    message = "Usuario no autenticado"
    

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        """Verifica si el usuario está autenticado.
        
        Args:
            source       : Objeto fuente (no usado en este permiso)
            info (Info)  : Contexto de GraphQL con request y datos de sesión
            **kwargs     : Parámetros adicionales del campo GraphQL
            
        Returns:
            bool: True si el usuario está autenticado, False en caso contrario
            
        Note:
            Este método es llamado automáticamente por Strawberry GraphQL
            antes de ejecutar el resolver del campo protegido.
        """
        try:
            request = info.context.get("request")
            user    = get_current_user(request)
            return user is not None
        except AuthenticationError:
            return False


class IsAdmin(BasePermission):
    """Permiso de GraphQL que requiere rol de administrador.
    
    Esta clase de permiso verifica que el usuario esté autenticado
    Y además tenga rol de administrador. Se aplica a operaciones
    privilegiadas como crear usuarios o acceder a estadísticas globales.
    
    Attributes:
        message (str): Mensaje de error mostrado cuando falla el permiso.
        
    Example:
        @strawberry.field(permission_classes=[IsAdmin])
        def crear_usuario(self, input: CrearUsuarioInput) -> UsuarioResponse:
            # Solo administradores pueden crear usuarios
            return create_new_user(input)
            
    Note:
        Este permiso implica autenticación, no es necesario combinar
        con IsAuthenticated. Si el usuario no está autenticado
        o no es admin, el permiso fallará.
    """
    
    message = "Permisos de administrador requeridos"
    
    def has_permission(self, source, info: Info, **kwargs) -> bool:
        """Verifica si el usuario es administrador.
        
        Args:
            source: Objeto fuente (no usado en este permiso)
            info (Info): Contexto de GraphQL con request y datos de sesión
            **kwargs: Parámetros adicionales del campo GraphQL
            
        Returns:
            bool: True si el usuario es administrador, False en caso contrario
            
        Note:
            Verifica tanto autenticación como rol de administrador en una
            sola validación, simplificando el uso en los resolvers.
        """
        try:
            request = info.context.get("request")
            user    = get_current_user(request)
            return user and user.get("rol") == "admin"
        except AuthenticationError:
            return False


class IsOwnerOrAdmin(BasePermission):
    """Permiso que permite al propietario del recurso o admin"""
    
    message = "Permisos de propietario o administrador requeridos"
    
    def has_permission(self, source, info: Info, **kwargs) -> bool:
        try:
            request = info.context.get("request")
            user    = get_current_user(request)
            
            if not user:
                return False
            
            # Admin siempre tiene acceso
            if user.get("rol") == "admin":
                return True
            
            # Verificar si es el propietario del recurso
            # Esto dependerá del contexto específico de cada resolver
            resource_owner = kwargs.get("owner_id") or source.get("owner_id")
            return user.get("username") == resource_owner
            
        except AuthenticationError:
            return False


def get_auth_context(request: Request) -> dict:
    """
    Crear contexto de autenticación para GraphQL.
    
    Args:
        request: Request de FastAPI
        
    Returns:
        dict: Contexto que incluye el request y datos del usuario
    """
    context = {"request": request}
    
    try:
        user            = get_current_user(request)
        context["user"] = user
    except AuthenticationError:
        context["user"] = None
    
    return context


# Decorador para proteger resolvers
def require_auth(func):
    """
    Decorador para requerir autenticación en resolvers.
    
    Usage:
        @require_auth
        def my_resolver(self, info: Info):
            # El usuario estará disponible en info.context["user"]
            pass
    """
    def wrapper(*args, **kwargs):
        # El objeto Info generalmente es el segundo argumento
        info = None
        for arg in args:
            if hasattr(arg, 'context'):
                info = arg
                break
        
        if not info:
            raise Exception("Info object no encontrado")
        
        try:
            user                 = get_current_user(info.context.get("request"))
            info.context["user"] = user
            return func(*args, **kwargs)
        except AuthenticationError as e:
            raise Exception(f"Autenticación requerida: {str(e)}")
    
    return wrapper


def require_admin(func):
    """
    Decorador para requerir permisos de administrador.
    
    Usage:
        @require_admin
        def admin_resolver(self, info: Info):
            pass
    """
    def wrapper(*args, **kwargs):
        info = None
        for arg in args:
            if hasattr(arg, 'context'):
                info = arg
                break
        
        if not info:
            raise Exception("Info object no encontrado")
        
        try:
            user = get_current_user(info.context.get("request"))
            if user.get("rol") != "admin":
                raise Exception("Permisos de administrador requeridos")
            
            info.context["user"] = user
            return func(*args, **kwargs)
        except AuthenticationError as e:
            raise Exception(f"Autenticación requerida: {str(e)}")
    
    return wrapper


# Middleware para agregar contexto de autenticación
class AuthMiddleware:
    """Middleware para agregar contexto de autenticación a GraphQL"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] == "/graphql":
            # Crear contexto de autenticación para GraphQL
            request = Request(scope, receive)
            scope["auth_context"] = get_auth_context(request)
        
        await self.app(scope, receive, send)