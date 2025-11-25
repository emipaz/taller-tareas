"""
API REST del Sistema de Gestión de Tareas

Este módulo contiene la implementación completa de la API REST usando FastAPI,
incluyendo autenticación JWT, modelos Pydantic y documentación automática.

Componentes principales:
- api_rest        : Aplicación FastAPI principal
- api_models      : Modelos Pydantic para validación de datos
- jwt_auth        : Sistema de autenticación JWT
- test_api_client : Cliente para pruebas de la API

Uso:
    from api_rest import app, create_access_token, verify_token
"""

# Importar componentes principales usando imports absolutos
import sys
import os

# Agregar el directorio actual al path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from api_rest import app
from api_models import *
from jwt_auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    JWTConfig,
    TokenData,
    TokenResponse,
    get_token_info
)

__version__ = "1.0.0"
__author__ = "Sistema de Gestión de Tareas"

# Exportar para facilitar imports externos
__all__ = [
    "app",
    "create_access_token", 
    "create_refresh_token",
    "verify_token",
    "JWTConfig",
    "TokenData",
    "TokenResponse",
    "get_token_info"
]