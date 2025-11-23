"""Módulo gestor del sistema de tareas.

Este módulo contiene la lógica de negocio del sistema de gestión de tareas,
separada de la interfaz de usuario para permitir reutilización.
"""

from typing import List, Optional, Dict, Any, Tuple
from .usuario import Usuario
from .tarea import Tarea
from .utils import (
    cargar_datos, guardar_datos, guardar_json, hay_admin, 
    generar_password, buscar_usuario_por_nombre, buscar_tarea_por_nombre,
    filtrar_tareas_por_usuario, obtener_estadisticas_tareas
)


class GestorSistema:
    """Gestor principal del sistema de tareas.
    
    Esta clase encapsula toda la lógica de negocio del sistema,
    incluyendo gestión de usuarios, tareas y autenticación.
    """
    
    def __init__(self, 
                 archivo_usuarios       : str = "usuarios.dat", 
                 archivo_tareas         : str = "tareas.dat",
                 archivo_finalizadas    : str = "tareas_finalizadas.json"):
        """Inicializa el gestor del sistema.
        
        Args:
            archivo_usuarios: Ruta del archivo de usuarios.
            archivo_tareas: Ruta del archivo de tareas.
            archivo_finalizadas: Ruta del archivo de tareas finalizadas.
        """
        self.archivo_usuarios    = archivo_usuarios
        self.archivo_tareas      = archivo_tareas
        self.archivo_finalizadas = archivo_finalizadas
    
    # Gestión de usuarios

    
    def cargar_usuarios(self) -> List[Usuario]:
        """Carga la lista de usuarios del archivo.
        
        Returns:
            Lista de usuarios cargados.
            
        Raises:
            IOError: Si hay error al cargar el archivo.
        """
        return cargar_datos(self.archivo_usuarios)
    
    def guardar_usuarios(self, usuarios: List[Usuario]) -> bool:
        """Guarda la lista de usuarios en el archivo.
        
        Args:
            usuarios: Lista de usuarios a guardar.
            
        Returns:
            True si se guardó exitosamente.
            
        Raises:
            IOError: Si hay error al guardar el archivo.
        """
        return guardar_datos(usuarios, self.archivo_usuarios)
    
    def existe_admin(self) -> bool:
        """Verifica si existe al menos un administrador.
        
        Returns:
            True si existe al menos un admin, False en caso contrario.
        """
        usuarios = self.cargar_usuarios()
        return hay_admin(usuarios)
    
    def crear_admin(self, nombre: str, contraseña: str) -> Tuple[bool, str]:
        """Crea un usuario administrador.
        
        Args:
            nombre: Nombre del administrador.
            contraseña: Contraseña del administrador.
            
        Returns:
            Tupla con (éxito, mensaje).
        """
        try:
            usuarios = self.cargar_usuarios()
            
            if buscar_usuario_por_nombre(usuarios, nombre):
                return False, "Ya existe un usuario con ese nombre"
            
            admin = Usuario(nombre, contraseña, rol="admin")
            usuarios.append(admin)
            self.guardar_usuarios(usuarios)
            
            return True, f"Administrador '{nombre}' creado exitosamente"
            
        except Exception as e:
            return False, f"Error al crear administrador: {e}"
    
    def crear_usuario(self, nombre: str) -> Tuple[bool, str]:
        """Crea un nuevo usuario sin contraseña inicial.
        
        Args:
            nombre: Nombre del usuario.
            
        Returns:
            Tupla con (éxito, mensaje).
        """
        try:
            usuarios = self.cargar_usuarios()
            
            if buscar_usuario_por_nombre(usuarios, nombre):
                return False, "Ya existe un usuario con ese nombre"
            
            usuario = Usuario(nombre)  # Sin contraseña inicial
            usuarios.append(usuario)
            self.guardar_usuarios(usuarios)
            
            return True, f"Usuario '{nombre}' creado exitosamente"
            
        except Exception as e:
            return False, f"Error al crear usuario: {e}"
    
    def eliminar_usuario(self, identificador: str) -> Tuple[bool, str]:
        """Elimina un usuario del sistema.
        
        Args:
            identificador: Nombre del usuario a eliminar.
            
        Returns:
            Tupla con (éxito, mensaje).
        """
        try:
            usuarios = self.cargar_usuarios()
            usuario_encontrado = buscar_usuario_por_nombre(usuarios, identificador)
            
            if not usuario_encontrado:
                return False, "Usuario no encontrado"
            
            if usuario_encontrado.es_admin():
                return False, "No se puede eliminar un administrador"
            
            usuarios = [u for u in usuarios if u.nombre != identificador]
            self.guardar_usuarios(usuarios)
            
            return True, f"Usuario '{identificador}' eliminado exitosamente"
            
        except Exception as e:
            return False, f"Error al eliminar usuario: {e}"
    
    def autenticar_usuario(self, nombre: str, contraseña: str) -> Tuple[Optional[Usuario], str]:
        """Autentica un usuario en el sistema.
        
        Args:
            nombre: Nombre del usuario.
            contraseña: Contraseña del usuario.
            
        Returns:
            Tupla con (usuario o None, mensaje).
        """
        usuarios = self.cargar_usuarios()
        usuario = buscar_usuario_por_nombre(usuarios, nombre)
        
        if not usuario:
            return None, "Usuario no encontrado"
        
        if not usuario.tiene_password():
            return None, "sin_password"  # Caso especial
        
        if usuario.verificar_password(contraseña):
            return usuario, "Autenticación exitosa"
        else:
            return None, "Contraseña incorrecta"
    
    def establecer_password_inicial(self, nombre: str, contraseña: str) -> Tuple[bool, str]:
        """Establece la contraseña inicial de un usuario.
        
        Args:
            nombre: Nombre del usuario.
            contraseña: Nueva contraseña.
            
        Returns:
            Tupla con (éxito, mensaje).
        """
        try:
            usuarios = self.cargar_usuarios()
            
            for i, usuario in enumerate(usuarios):
                if usuario.nombre == nombre:
                    if usuario.tiene_password():
                        return False, "El usuario ya tiene contraseña establecida"
                    
                    usuario.cambiar_password(contraseña)
                    usuarios[i] = usuario
                    self.guardar_usuarios(usuarios)
                    
                    return True, "Contraseña establecida exitosamente"
            
            return False, "Usuario no encontrado"
            
        except Exception as e:
            return False, f"Error al establecer contraseña: {e}"
    
    def cambiar_password(self, nombre: str, contraseña_actual: str, 
                        contraseña_nueva: str) -> Tuple[bool, str]:
        """Cambia la contraseña de un usuario.
        
        Args:
            nombre: Nombre del usuario.
            contraseña_actual: Contraseña actual del usuario.
            contraseña_nueva: Nueva contraseña del usuario.
            
        Returns:
            Tupla con (éxito, mensaje).
        """
        try:
            usuarios = self.cargar_usuarios()
            
            for i, usuario in enumerate(usuarios):
                if usuario.nombre == nombre:
                    if not usuario.verificar_password(contraseña_actual):
                        return False, "Contraseña actual incorrecta"
                    
                    if contraseña_actual == contraseña_nueva:
                        return False, "La nueva contraseña debe ser diferente"
                    
                    usuario.cambiar_password(contraseña_nueva)
                    usuarios[i] = usuario
                    self.guardar_usuarios(usuarios)
                    
                    return True, "Contraseña cambiada exitosamente"
            
            return False, "Usuario no encontrado"
            
        except Exception as e:
            return False, f"Error al cambiar contraseña: {e}"
    
    def resetear_password_usuario(self, nombre_admin: str, nombre_usuario: str) -> Tuple[bool, str]:
        """Resetea la contraseña de un usuario (solo admin).
        
        Args:
            nombre_admin: Nombre del administrador que hace la operación.
            nombre_usuario: Nombre del usuario cuya contraseña se resetea.
            
        Returns:
            Tupla con (éxito, mensaje).
        """
        try:
            usuarios = self.cargar_usuarios()
            admin = buscar_usuario_por_nombre(usuarios, nombre_admin)
            
            if not admin or not admin.es_admin():
                return False, "Solo los administradores pueden resetear contraseñas"
            
            for i, usuario in enumerate(usuarios):
                if usuario.nombre == nombre_usuario:
                    if usuario.es_admin():
                        return False, "No se puede resetear la contraseña de un administrador"
                    
                    usuario.resetear_password()
                    usuarios[i] = usuario
                    self.guardar_usuarios(usuarios)
                    
                    return True, f"Contraseña de '{nombre_usuario}' reseteada exitosamente"
            
            return False, "Usuario no encontrado"
            
        except Exception as e:
            return False, f"Error al resetear contraseña: {e}"
    
    # Gestión de tareas

    def cargar_tareas(self) -> List[Tarea]:
        """Carga la lista de tareas del archivo.
        
        Returns:
            Lista de tareas cargadas.
        """
        return cargar_datos(self.archivo_tareas)
    
    def guardar_tareas(self, tareas: List[Tarea]) -> bool:
        """Guarda la lista de tareas en el archivo.
        
        Args:
            tareas: Lista de tareas a guardar.
            
        Returns:
            True si se guardó exitosamente.
        """
        return guardar_datos(tareas, self.archivo_tareas)
    
    def crear_tarea(self, nombre: str, descripcion: str) -> Tuple[bool, str]:
        """Crea una nueva tarea.
        
        Args:
            nombre: Nombre de la tarea.
            descripcion: Descripción de la tarea.
            
        Returns:
            Tupla con (éxito, mensaje).
        """
        try:
            tareas = self.cargar_tareas()
            
            if buscar_tarea_por_nombre(tareas, nombre):
                return False, "Ya existe una tarea con ese nombre"
            
            tarea = Tarea(nombre, descripcion)
            tareas.append(tarea)
            self.guardar_tareas(tareas)
            
            return True, f"Tarea '{nombre}' creada exitosamente"
            
        except Exception as e:
            return False, f"Error al crear tarea: {e}"
    
    def asignar_usuario_tarea(self, nombre_tarea: str, nombre_usuario: str) -> Tuple[bool, str]:
        """Asigna un usuario a una tarea.
        
        Args:
            nombre_tarea: Nombre de la tarea.
            nombre_usuario: Nombre del usuario.
            
        Returns:
            Tupla con (éxito, mensaje).
        """
        try:
            tareas = self.cargar_tareas()
            usuarios = self.cargar_usuarios()
            
            tarea = buscar_tarea_por_nombre(tareas, nombre_tarea)
            if not tarea:
                return False, "Tarea no encontrada"
            
            usuario = buscar_usuario_por_nombre(usuarios, nombre_usuario)
            if not usuario:
                return False, "Usuario no encontrado"
            
            if tarea.agregar_usuario(nombre_usuario):
                self.guardar_tareas(tareas)
                return True, f"Usuario '{nombre_usuario}' asignado a la tarea"
            else:
                return False, "El usuario ya estaba asignado a la tarea"
                
        except Exception as e:
            return False, f"Error al asignar usuario: {e}"
    
    def finalizar_tarea(self, nombre_tarea: str) -> Tuple[bool, str]:
        """Finaliza una tarea y la guarda en el archivo de finalizadas.
        
        Args:
            nombre_tarea: Nombre de la tarea.
            
        Returns:
            Tupla con (éxito, mensaje).
        """
        try:
            tareas = self.cargar_tareas()
            tarea = buscar_tarea_por_nombre(tareas, nombre_tarea)
            
            if not tarea:
                return False, "Tarea no encontrada"
            
            if tarea.esta_finalizada():
                return False, "La tarea ya está finalizada"
            
            tarea.finalizar_tarea()
            self.guardar_tareas(tareas)
            
            # Guardar en archivo de finalizadas
            try:
                guardar_json(tarea.to_json(), self.archivo_finalizadas)
            except Exception:
                pass  # No es crítico si falla el guardado en JSON
            
            return True, f"Tarea '{nombre_tarea}' finalizada exitosamente"
            
        except Exception as e:
            return False, f"Error al finalizar tarea: {e}"
    
    def obtener_tareas_usuario(self, nombre_usuario: str, incluir_finalizadas: bool = True) -> List[Tarea]:
        """Obtiene las tareas asignadas a un usuario.
        
        Args:
            nombre_usuario: Nombre del usuario.
            incluir_finalizadas: Si incluir tareas finalizadas.
            
        Returns:
            Lista de tareas del usuario.
        """
        tareas = self.cargar_tareas()
        tareas_usuario = filtrar_tareas_por_usuario(tareas, nombre_usuario)
        
        if not incluir_finalizadas:
            tareas_usuario = [t for t in tareas_usuario if not t.esta_finalizada()]
        
        return tareas_usuario
    
    def agregar_comentario_tarea(self, nombre_tarea: str, comentario: str, 
                                nombre_usuario: str) -> Tuple[bool, str]:
        """Agrega un comentario a una tarea.
        
        Args:
            nombre_tarea: Nombre de la tarea.
            comentario: Texto del comentario.
            nombre_usuario: Usuario que hace el comentario.
            
        Returns:
            Tupla con (éxito, mensaje).
        """
        try:
            tareas = self.cargar_tareas()
            tarea = buscar_tarea_por_nombre(tareas, nombre_tarea)
            
            if not tarea:
                return False, "Tarea no encontrada"
            
            tarea.agregar_comentario(comentario, nombre_usuario)
            self.guardar_tareas(tareas)
            
            return True, "Comentario agregado exitosamente"
            
        except Exception as e:
            return False, f"Error al agregar comentario: {e}"
    
    def obtener_estadisticas_sistema(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del sistema.
        
        Returns:
            Diccionario con estadísticas del sistema.
        """
        try:
            usuarios = self.cargar_usuarios()
            tareas = self.cargar_tareas()
            
            stats_usuarios = {
                "total": len(usuarios),
                "admins": sum(1 for u in usuarios if u.es_admin()),
                "users": sum(1 for u in usuarios if not u.es_admin()),
                "sin_password": sum(1 for u in usuarios if not u.tiene_password())
            }
            
            stats_tareas = obtener_estadisticas_tareas(tareas)
            
            return {
                "usuarios": stats_usuarios,
                "tareas": stats_tareas
            }
            
        except Exception:
            return {"error": "No se pudieron obtener las estadísticas"}