"""Módulo para gestión de tareas.

Este módulo contiene la clase Tarea que maneja la información
y operaciones relacionadas con las tareas del sistema.
"""

from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from textwrap import fill


class Tarea:
    """Representa una tarea en el sistema de gestión.
    
    Una tarea contiene información sobre el trabajo a realizar,
    usuarios asignados, comentarios y estado de finalización.
    
    Attributes:
        nombre (str)                             : Nombre único de la tarea.
        descripcion (str)                        : Descripción detallada de la tarea.
        estado (str)                             : Estado actual ('pendiente' o 'finalizada').
        fecha_creacion (str)                     : Fecha y hora de creación.
        usuarios_asignados (List[str])           : Lista de nombres de usuarios asignados.
        comentarios (List[Tuple[str, str, str]]) : Lista de comentarios con formato
                                                     (comentario, usuario, fecha).
    """
    
    ESTADO_PENDIENTE  = "pendiente"
    ESTADO_FINALIZADA = "finalizada"
    
    def __init__(self, nombre: str, descripcion: str, 
                 usuarios_asignados: Optional[List[str]] = None) -> None:
        """Inicializa una nueva tarea.
        
        Args:
            nombre: Nombre único de la tarea.
            descripcion: Descripción detallada de la tarea.
            usuarios_asignados: Lista opcional de usuarios asignados.
            
        Raises:
            ValueError: Si el nombre o descripción están vacíos.
        """
        if not nombre or nombre.strip() == "":
            raise ValueError("El nombre de la tarea no puede estar vacío")
        if not descripcion or descripcion.strip() == "":
            raise ValueError("La descripción de la tarea no puede estar vacía")
            
        self.nombre             = nombre.strip()
        self.descripcion        = descripcion.strip()
        self.estado             = self.ESTADO_PENDIENTE
        self.fecha_creacion     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.usuarios_asignados = usuarios_asignados if usuarios_asignados else []
        
        self.comentarios : List[Tuple[str, str, str]] = []
    
    def agregar_usuario(self, usuario: str) -> bool:
        """Agrega un usuario a la tarea si no está ya asignado.
        
        Args:
            usuario: Nombre del usuario a agregar.
            
        Returns:
            True si el usuario se agregó exitosamente, False si ya estaba asignado.
            
        Raises:
            ValueError: Si el nombre del usuario está vacío.
        """
        if not usuario or usuario.strip() == "":
            raise ValueError("El nombre del usuario no puede estar vacío")
            
        usuario = usuario.strip()
        if usuario not in self.usuarios_asignados:
            self.usuarios_asignados.append(usuario)
            return True
        return False
    
    def quitar_usuario(self, usuario: str) -> bool:
        """Quita un usuario de la tarea si está asignado.
        
        Args:
            usuario: Nombre del usuario a quitar.
            
        Returns:
            True si el usuario se quitó exitosamente, False si no estaba asignado.
        """
        if usuario in self.usuarios_asignados:
            self.usuarios_asignados.remove(usuario)
            return True
        return False
    
    def finalizar_tarea(self) -> bool:
        """Marca la tarea como finalizada.
        
        Returns:
            True si la tarea se finalizó exitosamente, False si ya estaba finalizada.
        """
        if self.estado != self.ESTADO_FINALIZADA:
            self.estado = self.ESTADO_FINALIZADA
            return True
        return False
    
    def activar_tarea(self) -> bool:
        """Activa la tarea (la marca como pendiente).
        
        Returns:
            True si la tarea se activó exitosamente, False si ya estaba pendiente.
        """
        if self.estado != self.ESTADO_PENDIENTE:
            self.estado = self.ESTADO_PENDIENTE
            return True
        return False
    
    def esta_finalizada(self) -> bool:
        """Verifica si la tarea está finalizada.
        
        Returns:
            True si la tarea está finalizada, False en caso contrairo.
        """
        return self.estado == self.ESTADO_FINALIZADA
    
    def agregar_comentario(self, comentario: str, usuario: str) -> bool:
        """Agrega un comentario a la tarea con timestamp.
        
        Args:
            comentario  : Texto del comentario.
            usuario     : Nombre del usuario que hace el comentario.
            
        Returns:
            True si el comentario se agregó exitosamente.
            
        Raises:
            ValueError: Si el comentario o usuario están vacíos.
        """
        if not comentario or comentario.strip() == "":
            raise ValueError("El comentario no puede estar vacío")
        if not usuario or usuario.strip() == "":
            raise ValueError("El nombre del usuario no puede estar vacío")
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.comentarios.append((comentario.strip(), usuario.strip(), timestamp))
        return True
    
    def obtener_resumen(self) -> Dict[str, Any]:
        """Obtiene un resumen de la información de la tarea.
        
        Returns:
            Diccionario con el resumen de la tarea.
        """
        return {
            "nombre"             : self.nombre,
            "descripcion"        : self.descripcion,
            "estado"             : self.estado,
            "fecha_creacion"     : self.fecha_creacion,
            "usuarios_asignados" : self.usuarios_asignados.copy(),
            "total_comentarios"  : len(self.comentarios),
            "esta_finalizada"    : self.esta_finalizada()
        }
    
    def obtener_info_detallada(self) -> str:
        """Genera una representación detallada de la tarea en formato texto.
        
        Returns:
            String con toda la información de la tarea formateada.
        """
        info_lines = []
        info_lines.append("#" * 90)
        info_lines.append(f"# Tarea: {self.nombre:<80}#")
        info_lines.append(f"# Fecha de creación: {self.fecha_creacion:<68}#")
        
        usuarios_str = ', '.join(self.usuarios_asignados) if self.usuarios_asignados else 'Ninguno'
        info_lines.append(f"# Usuarios asignados: {usuarios_str:<67}#")
        info_lines.append(f"# Estado: {self.estado:<79}#")
        info_lines.append(f"# Descripción: {self.descripcion:<75}#")
        info_lines.append("#{:<88}#".format(" Comentarios :"))
        
        for idx, (comentario, usuario, fecha) in enumerate(self.comentarios, start=1):
            info_lines.append(f"#   {idx}) Realizado por {usuario} el {fecha}:")
            info_lines.append("#\t  " + "-" * 79 + "#")
            # Dividir comentario en líneas de 80 caracteres
            comentario_lines = fill(comentario, 80).split('\n')
            for line in comentario_lines:
                info_lines.append(f"#\t{line:<87}#")
            info_lines.append("#\t  " + "-" * 79 + "#")
        
        if not self.comentarios:
            info_lines.append("#   No hay comentarios aún.<" + " " * 69 + "#")
        
        info_lines.append("#" * 90)
        return "\n".join(info_lines)
    
    def to_json(self) -> Dict[str, Any]:
        """Convierte la tarea a formato diccionario para serialización JSON.
        
        Returns:
            Diccionario con todos los datos de la tarea.
        """
        return {
            "nombre"             : self.nombre,
            "descripcion"        : self.descripcion,
            "estado"             : self.estado,
            "fecha_creacion"     : self.fecha_creacion,
            "usuarios_asignados" : self.usuarios_asignados.copy(),
            "comentarios"        : [list(comentario) for comentario in self.comentarios]
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Tarea':
        """Crea una instancia de Tarea desde datos JSON.
        
        Args:
            data: Diccionario con los datos de la tarea.
            
        Returns:
            Nueva instancia de Tarea.
            
        Raises:
            KeyError: Si faltan claves requeridas.
            ValueError: Si los datos no son válidos.
        """
        tarea                = cls(data["nombre"], data["descripcion"], data.get("usuarios_asignados"))
        tarea.estado         = data["estado"]
        tarea.fecha_creacion = data["fecha_creacion"]
        
        # Convertir comentarios de vuelta a tuplas
        tarea.comentarios = [tuple(comentario) for comentario in data.get("comentarios", [])]
        
        return tarea
    
    def __str__(self) -> str:
        """Representación en string de la tarea.
        
        Returns:
            String con información básica de la tarea.
        """
        return f"Tarea(nombre='{self.nombre}', estado='{self.estado}')"
    
    def __repr__(self) -> str:
        """Representación técnica de la tarea.
        
        Returns:
            String con la representación técnica de la tarea.
        """
        return self.__str__()
