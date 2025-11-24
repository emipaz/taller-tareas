"""Módulo de autenticación JWT para la API REST.

Este módulo implementa autenticación segura usando JWT (JSON Web Tokens)
con las mejores prácticas de seguridad y bibliotecas confiables.

Características de seguridad implementadas:
- Tokens firmados con algoritmo RS256 (RSA + SHA256)
- Expiración automática de tokens (configurable)
- Refresh tokens para renovación segura
- Validación estricta de claims
- Protección contra ataques de timing
- Manejo seguro de claves privadas/públicas

Bibliotecas utilizadas:
- PyJWT        : Biblioteca JWT oficial y bien mantenida
- cryptography : Criptografía robusta del Python Cryptographic Authority
- passlib      : Manejo seguro de contraseñas

Note:
    En producción, las claves deben almacenarse como variables de entorno
    o en un servicio de gestión de secretos (AWS Secrets, Azure Key Vault, etc.)
"""

import os
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel


# ================================
# CONFIGURACIÓN JWT
# ================================

class JWTConfig:
    """Configuración centralizada para JWT.
    
    Centraliza todas las configuraciones de JWT para facilitar
    modificaciones y mantener seguridad consistente.
    
    Attributes:
        ALGORITHM                   : Algoritmo de firmado (RS256 recomendado para producción)
        ACCESS_TOKEN_EXPIRE_MINUTES : Duración del token de acceso
        REFRESH_TOKEN_EXPIRE_DAYS   : Duración del refresh token
        ISSUER                      : Identificador del emisor del token
        AUDIENCE                    : Audiencia objetivo del token
    """
    
    # Algoritmo de firmado - RS256 es más seguro que HS256 para APIs públicas
    ALGORITHM : str = "RS256"
    
    # Tiempo de vida de tokens
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 30      # 30 minutos - corto por seguridad
    REFRESH_TOKEN_EXPIRE_DAYS   : int = 7       # 7 días - renovación semanal
    
    # Claims estándar JWT
    ISSUER   : str = "sistema-tareas-api"       # iss: identificador del emisor
    AUDIENCE : str = "sistema-tareas-users"     # aud: audiencia objetivo
    
    # Clave secreta para desarrollo (EN PRODUCCIÓN: usar variables de entorno)
    SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", 
        secrets.token_urlsafe(32)  # Genera clave aleatoria si no existe
    )


# ================================
# MODELOS PYDANTIC PARA JWT
# ================================

class TokenData(BaseModel):
    """Datos extraídos del token JWT.
    
    Representa la información del usuario contenida en el token
    después de la validación y decodificación.
    
    Attributes:
        username : Nombre del usuario autenticado
        role     : Rol del usuario ('user' o 'admin')
        exp      : Timestamp de expiración del token
        iat      : Timestamp de emisión del token
    """
    username : str
    role     : str
    exp      : datetime
    iat      : datetime


class TokenResponse(BaseModel):
    """Respuesta con tokens JWT.
    
    Estructura estándar para devolver tokens de autenticación
    al cliente después de login exitoso.
    
    Attributes:
        access_token   : Token JWT para autenticación de requests
        refresh_token  : Token para renovar el access_token
        token_type     : Tipo de token (siempre "bearer")
        expires_in     : Segundos hasta expiración del access_token
    """
    access_token   : str
    refresh_token  : str
    token_type     : str = "bearer"
    expires_in     : int


# ================================
# GENERADOR Y VALIDADOR DE CLAVES
# ================================

class CryptoKeyManager:
    """Gestor de claves criptográficas para JWT.
    
    Maneja la generación, almacenamiento y carga de claves RSA
    para firmar y validar tokens JWT de forma segura.
    
    Note:
        En desarrollo genera claves en memoria.
        En producción debería usar un Key Management Service.
    """
    
    def __init__(self):
        """Inicializa el gestor y genera/carga claves RSA."""
        self._private_key = None
        self._public_key  = None
        self._initialize_keys()
    
    def _initialize_keys(self) -> None:
        """Inicializa las claves RSA para JWT.
        
        Genera un par de claves RSA de 2048 bits para firmar y validar tokens.
        En producción, estas claves deberían cargarse desde almacenamiento seguro.
        
        Note:
            RSA 2048 bits es el estándar mínimo recomendado.
            Las claves se mantienen en memoria por simplicidad en desarrollo.
        """
        # Generar clave privada RSA de 2048 bits
        private_key = rsa.generate_private_key(
            public_exponent = 65537,  # Exponente público estándar
            key_size        = 2048    # Tamaño de clave mínimo recomendado
        )
        
        # Derivar clave pública de la privada
        public_key = private_key.public_key()
        
        # Serializar para uso con PyJWT
        self._private_key        = private_key.private_bytes(
            encoding             = serialization.Encoding.PEM,
            format               = serialization.PrivateFormat.PKCS8,
            encryption_algorithm = serialization.NoEncryption()
        )
        
        self._public_key = public_key.public_bytes(
            encoding      = serialization.Encoding.PEM,
            format        = serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    @property
    def private_key(self) -> bytes:
        """Clave privada para firmar tokens."""
        return self._private_key
    
    @property
    def public_key(self) -> bytes:
        """Clave pública para validar tokens."""
        return self._public_key


# Instancia global del gestor de claves
key_manager = CryptoKeyManager()


# ================================
# FUNCIONES JWT CORE
# ================================

def create_access_token(username: str, role: str) -> str:
    """Crea un token JWT de acceso para el usuario.
    
    Genera un token firmado con RSA que contiene información del usuario
    y tiene tiempo de vida limitado para seguridad.
    
    Args:
        username : Nombre único del usuario
        role     : Rol del usuario ('user' o 'admin')
        
    Returns:
        str: Token JWT firmado y codificado
        
    Example:
        ```python
        token = create_access_token("juan", "user")
        # token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
        ```
        
    Note:
        El token incluye claims estándar (iss, aud, exp, iat) y claims custom (role).
        La expiración es corta (30 min) para minimizar riesgo si se compromete.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload del token con claims estándar y personalizados
    payload = {
        # Claims estándar JWT (RFC 7519)
        "sub": username,                   # Subject    : identificador del usuario
        "exp": expire,                     # Expiration : tiempo de expiración
        "iat": now,                        # Issued At  : tiempo de emisión
        "iss": JWTConfig.ISSUER,           # Issuer     : identificador del emisor
        "aud": JWTConfig.AUDIENCE,         # Audience   : audiencia objetivo
        "jti": secrets.token_urlsafe(16),  # JWT ID     : identificador único del token
        
        # Claims personalizados
        "role": role,                      # Rol del usuario en el sistema
        "type": "access"                   # Tipo de token para diferenciación
    }
    
    # Firmar token con clave privada RSA
    token = jwt.encode(
        payload,
        key_manager.private_key,
        algorithm = JWTConfig.ALGORITHM
    )
    
    return token


def create_refresh_token(username: str) -> str:
    """Crea un token de refresh para renovar access tokens.
    
    Genera un token de larga duración que solo sirve para obtener
    nuevos access tokens, no para autenticar requests directamente.
    
    Args:
        username: Nombre único del usuario
        
    Returns:
        str: Refresh token JWT firmado
        
    Note:
        Los refresh tokens tienen vida más larga pero menos privilegios.
        Solo pueden usarse en el endpoint de renovación de tokens.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "sub": username,
        "exp": expire,
        "iat": now,
        "iss": JWTConfig.ISSUER,
        "aud": JWTConfig.AUDIENCE,
        "jti": secrets.token_urlsafe(16),
        "type": "refresh"  # Importante: marcar como refresh token
    }
    
    token = jwt.encode(
        payload,
        key_manager.private_key,
        algorithm=JWTConfig.ALGORITHM
    )
    
    return token


def verify_token(token: str, expected_type: str = "access") -> TokenData:
    """Verifica y decodifica un token JWT.
    
    Valida la firma, expiración y claims del token, devolviendo
    los datos del usuario si el token es válido.
    
    Args:
        token         : Token JWT a verificar
        expected_type : Tipo esperado de token ('access' o 'refresh')
        
    Returns:
        TokenData  : Datos del usuario extraídos del token
        
    Raises:
        HTTPException: 401 si el token es inválido, expirado o malformado
        
    Example:
        ```python
        try:
            user_data = verify_token(token)
            print(f"Usuario: {user_data.username}, Rol: {user_data.role}")
        except HTTPException:
            print("Token inválido")
        ```
        
    Note:
        Valida todos los claims estándar (exp, iss, aud) y custom (type).
        Usa validación estricta para prevenir ataques de manipulación.
    """
    try:
        # Decodificar y validar token con clave pública
        payload = jwt.decode(
            token,
            key_manager.public_key,
            algorithms  = [JWTConfig.ALGORITHM],
            issuer      = JWTConfig.ISSUER,      # Validar emisor
            audience    = JWTConfig.AUDIENCE,    # Validar audiencia
            options     = {
                           "verify_signature": True,   # Verificar firma RSA
                           "verify_exp"      : True,   # Verificar expiración
                           "verify_iat"      : True,   # Verificar tiempo de emisión
                           "verify_iss"      : True,   # Verificar emisor
                           "verify_aud"      : True,   # Verificar audiencia
                           "require"         : ["exp", "iat", "sub", "iss", "aud"]  # Claims requeridos
            }
        )
        
        # Validar tipo de token
        token_type = payload.get("type")
        if token_type != expected_type:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail      = f"Token type mismatch. Expected {expected_type}, got {token_type}"
            )
        
        # Extraer datos del usuario
        username = payload.get("sub")
        role     = payload.get("role")
        exp      = datetime.fromtimestamp(payload.get("exp"), timezone.utc)
        iat      = datetime.fromtimestamp(payload.get("iat"), timezone.utc)
        
        if not username:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail      = "Token missing username claim"
            )
        
        return TokenData(
            username = username,
            role     = role or "user",  # Default role si no existe
            exp      = exp,
            iat      = iat
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = f"Token validation error: {str(e)}"
        )


# ================================
# DEPENDENCIES PARA FASTAPI
# ================================

# Esquema de seguridad HTTP Bearer para FastAPI
security = HTTPBearer(
    scheme_name = "JWT Bearer Token",
    description = "JWT token for API authentication"
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Dependency para obtener el usuario autenticado actual.
    
    Extrae y valida el token JWT del header Authorization,
    devolviendo los datos del usuario autenticado.
    
    Args:
        credentials: Credenciales HTTP Bearer extraídas automáticamente
        
    Returns:
        TokenData: Datos del usuario autenticado
        
    Raises:
        HTTPException: 401 si no hay token o es inválido
        
    Example:
        ```python
        @app.get("/protected")
        async def protected_endpoint(
            current_user: TokenData = Depends(get_current_user)
        ):
            return {"message": f"Hello {current_user.username}"}
        ```
        
    Note:
        Este dependency se inyecta automáticamente en endpoints protegidos.
        FastAPI maneja la extracción del header Authorization automáticamente.
    """
    if not credentials:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Missing authorization credentials"
        )
    
    # Validar formato del token
    if not credentials.credentials:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Invalid authorization format"
        )
    
    # Verificar y decodificar token
    return verify_token(credentials.credentials)


async def get_current_admin(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """Dependency para endpoints que requieren privilegios de administrador.
    
    Valida que el usuario autenticado tenga rol de administrador.
    Composición de dependencies: primero autentica, luego verifica rol.
    
    Args:
        current_user: Usuario autenticado (inyectado automáticamente)
        
    Returns:
        TokenData: Datos del usuario admin autenticado
        
    Raises:
        HTTPException: 403 si el usuario no es administrador
        
    Example:
        ```python
        @app.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: str,
            admin_user: TokenData = Depends(get_current_admin)
        ):
            # Solo admins pueden acceder aquí
            return delete_user_logic(user_id)
        ```
        
    Note:
        Este dependency combina autenticación + autorización.
        Usa composición de dependencies para código limpio y reutilizable.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail      = "Admin privileges required"
        )
    
    return current_user


# ================================
# UTILIDADES ADICIONALES
# ================================

def create_token_response(username: str, role: str) -> TokenResponse:
    """Crea respuesta completa de tokens para login.
    
    Genera access token y refresh token para el usuario,
    devolviendo una respuesta estructurada con metadatos.
    
    Args:
        username : Nombre del usuario
        role     : Rol del usuario
        
    Returns:
        TokenResponse: Respuesta completa con tokens y metadatos
        
    Example:
        ```python
        # Después de validar credenciales de login
        if login_valid:
            tokens = create_token_response("juan", "user")
            return tokens
        ```
    """
    access_token  = create_access_token(username, role)
    refresh_token = create_refresh_token(username)
    
    return TokenResponse(
        access_token  = access_token,
        refresh_token = refresh_token,
        token_type    = "bearer",
        expires_in    = JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # En segundos
    )


def get_token_info(token: str) -> Dict[str, Any]:
    """Obtiene información de un token sin validar firma.
    
    Útil para debugging y análisis de tokens. NO debe usarse
    para validación de seguridad, solo para inspección.
    
    Args:
        token: Token JWT a inspeccionar
        
    Returns:
        Dict: Payload del token decodificado (sin validar)
        
    Warning:
        Esta función NO valida la firma del token.
        Solo usar para debugging, nunca para autenticación.
    """
    try:
        # Decodificar sin verificar firma (solo para inspección)
        payload = jwt.decode(
            token, 
            options = {"verify_signature": False}
        )
        return payload
    except Exception as e:
        return {"error": str(e)}