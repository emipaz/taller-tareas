"""Módulo de utilidades para el sistema de gestión de tareas.

Este módulo contiene funciones de utilidad para manejo de archivos,
generación de contraseñas y operaciones de persistencia de datos.
"""

from os import path
import json
from pickle import load, dump
from random import choice
from string import ascii_letters, digits
from typing import List, Any, Dict, Optional
from usuario import Usuario
from tarea import Tarea


def cargar_datos(archivo: str) -> List[Any]:
    """Carga datos desde un archivo .dat usando pickle.
    
    Args:
        archivo: Ruta del archivo a cargar.
        
    Returns:
        Lista con los datos cargados. Lista vacía si el archivo no existe.
        
    Raises:
        IOError: Si hay error al leer el archivo.
        pickle.UnpicklingError: Si el archivo no tiene formato pickle válido.
    """
    if path.exists(archivo):
        try:
            with open(archivo, 'rb') as f:
                return load(f)
        except (IOError, OSError) as e:
            raise IOError(f"Error al cargar el archivo {archivo}: {e}")
    return []


def guardar_datos(datos: List[Any], archivo: str) -> bool:
    """Guarda datos en un archivo .dat usando pickle.
    
    Args:
        datos: Lista de datos a guardar.
        archivo: Ruta del archivo donde guardar.
        
    Returns:
        True si se guardó exitosamente.
        
    Raises:
        IOError: Si hay error al escribir el archivo.
    """
    try:
        with open(archivo, 'wb') as f:
            dump(datos, f)
        return True
    except (IOError, OSError) as e:
        raise IOError(f"Error al guardar el archivo {archivo}: {e}")


def guardar_json(dato: Dict[str, Any], archivo: str) -> bool:
    """Guarda un dato en un archivo JSON manteniendo datos existentes.
    
    Args:
        dato: Diccionario con el dato a guardar.
        archivo: Ruta del archivo JSON.
        
    Returns:
        True si se guardó exitosamente.
        
    Raises:
        IOError: Si hay error al leer/escribir el archivo.
        json.JSONDecodeError: Si el archivo existente no es JSON válido.
    """
    datos = []
    
    # Cargar datos existentes si el archivo existe
    if path.exists(archivo):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Archivo JSON inválido {archivo}: {e.msg}", e.doc, e.pos)
        except (IOError, OSError) as e:
            raise IOError(f"Error al leer el archivo {archivo}: {e}")
    
    # Agregar nuevo dato
    datos.append(dato)
    
    # Guardar datos actualizados
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    except (IOError, OSError) as e:
        raise IOError(f"Error al escribir el archivo {archivo}: {e}")


def cargar_json(archivo: str) -> List[Dict[str, Any]]:
    """Carga datos desde un archivo JSON.
    
    Args:
        archivo: Ruta del archivo JSON a cargar.
        
    Returns:
        Lista con los datos del archivo JSON. Lista vacía si no existe.
        
    Raises:
        IOError: Si hay error al leer el archivo.
        json.JSONDecodeError: Si el archivo no es JSON válido.
    """
    if not path.exists(archivo):
        return []
        
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Archivo JSON inválido {archivo}: {e.msg}", e.doc, e.pos)
    except (IOError, OSError) as e:
        raise IOError(f"Error al leer el archivo {archivo}: {e}")


def hay_admin(usuarios: List[Usuario]) -> bool:
    """Verifica si existe al menos un administrador en la lista de usuarios.
    
    Args:
        usuarios: Lista de usuarios a verificar.
        
    Returns:
        True si hay al menos un administrador, False en caso contrario.
    """
    if not usuarios:
        return False
    return any(usuario.rol == "admin" for usuario in usuarios)


def generar_password(longitud: int = 12, incluir_simbolos: bool = False) -> str:
    """Genera una contraseña aleatoria.
    
    Args:
        longitud: Longitud de la contraseña a generar.
        incluir_simbolos: Si incluir símbolos especiales en la contraseña.
        
    Returns:
        Contraseña generada aleatoriamente.
        
    Raises:
        ValueError: Si la longitud es menor a 1.
    """
    if longitud < 1:
        raise ValueError("La longitud debe ser mayor a 0")
        
    caracteres = ascii_letters + digits
    if incluir_simbolos:
        from string import punctuation
        # Excluir algunos símbolos problemáticos
        simbolos_seguros = "!@#$%&*+-="
        caracteres += simbolos_seguros
    
    return ''.join(choice(caracteres) for _ in range(longitud))


def validar_nombre_usuario(nombre: str) -> bool:
    """Valida que un nombre de usuario sea válido.
    
    Args:
        nombre: Nombre a validar.
        
    Returns:
        True si el nombre es válido, False en caso contrario.
    """
    if not nombre or nombre.strip() == "":
        return False
    
    nombre = nombre.strip()
    
    # Verificar longitud
    if len(nombre) < 3 or len(nombre) > 20:
        return False
    
    # Solo letras, números y guiones bajos
    return nombre.replace('_', '').isalnum()


def buscar_usuario_por_nombre(usuarios: List[Usuario], nombre: str) -> Optional[Usuario]:
    """Busca un usuario por nombre en una lista.
    
    Args:
        usuarios: Lista de usuarios donde buscar.
        nombre: Nombre del usuario a buscar.
        
    Returns:
        Usuario encontrado o None si no existe.
    """
    for usuario in usuarios:
        if usuario.nombre == nombre:
            return usuario
    return None


def buscar_tarea_por_nombre(tareas: List[Tarea], nombre: str) -> Optional[Tarea]:
    """Busca una tarea por nombre en una lista.
    
    Args:
        tareas: Lista de tareas donde buscar.
        nombre: Nombre de la tarea a buscar.
        
    Returns:
        Tarea encontrada o None si no existe.
    """
    for tarea in tareas:
        if tarea.nombre == nombre:
            return tarea
    return None


def filtrar_tareas_por_usuario(tareas: List[Tarea], nombre_usuario: str) -> List[Tarea]:
    """Filtra las tareas asignadas a un usuario específico.
    
    Args:
        tareas: Lista de tareas a filtrar.
        nombre_usuario: Nombre del usuario.
        
    Returns:
        Lista de tareas asignadas al usuario.
    """
    return [tarea for tarea in tareas if nombre_usuario in tarea.usuarios_asignados]


def obtener_estadisticas_tareas(tareas: List[Tarea]) -> Dict[str, int]:
    """Obtiene estadísticas básicas de una lista de tareas.
    
    Args:
        tareas: Lista de tareas para analizar.
        
    Returns:
        Diccionario con estadísticas (total, pendientes, finalizadas).
    """
    total       = len(tareas)
    finalizadas = sum(1 for tarea in tareas if tarea.esta_finalizada())
    pendientes  = total - finalizadas
    
    return {
        "total"       : total,
        "pendientes"  : pendientes,
        "finalizadas": finalizadas
    }

