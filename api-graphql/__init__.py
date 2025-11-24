"""
API GraphQL para el Sistema de Gestión de Tareas
==============================================

Este módulo implementa una API GraphQL completa para el sistema de gestión de tareas,
utilizando Strawberry GraphQL y FastAPI como base.

Características:
- Schema GraphQL tipado con Strawberry
- Autenticación JWT integrada
- Resolvers que utilizan el módulo core existente
- Soporte para queries, mutations y subscriptions
- Documentación GraphiQL integrada

Estructura:
- schema.py: Definición del schema GraphQL
- types.py: Tipos GraphQL (Usuario, Tarea, etc.)
- resolvers.py: Resolvers para queries y mutations
- auth.py: Middleware de autenticación JWT
- server.py: Servidor GraphQL con FastAPI
- client.py: Cliente Python para consumir la API
"""

from . import schema
from . import graphql_types
from . import resolvers
from . import auth
from . import server
from . import client


__version__ = "1.0.0"
__author__ = "Sistema de Gestión de Tareas"

__all__ = [
    "schema",
    "graphql_types",
    "resolvers",
    "auth",
    "server",
    "client",
    
]