"""
Core del Sistema de Gestión de Tareas

Este módulo contiene la lógica de negocio principal del sistema de gestión de tareas.
Puede ser utilizado por diferentes interfaces (consola, API REST, GUI, web).

Componentes principales:
- Usuario: Gestión de usuarios del sistema
- Tarea: Gestión de tareas y sus estados
- GestorSistema: Coordinador principal del sistema
- utils: Utilidades y funciones auxiliares

Ejemplo de uso:
    from core import GestorSistema
    
    gestor = GestorSistema()
    exito, mensaje = gestor.crear_usuario("juan")
"""

from .usuario import Usuario
from .tarea import Tarea
from .gestor_sistema import GestorSistema
from .utils import *

__version__ = "1.0.0"
__author__ = "Sistema de Gestión de Tareas"

__all__ = [
    "Usuario",
    "Tarea", 
    "GestorSistema",
    # Utils se importan automáticamente con *
]