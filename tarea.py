# tarea.py
from datetime import datetime
from textwrap import fill

class Tarea:
    def __init__(self, nombre, descripcion, usuarios_asignados=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = "pendiente"
        self.fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.usuarios_asignados = usuarios_asignados if usuarios_asignados else []
        self.comentarios = []

    def agregar_usuario(self, usuario):
        """Agrega un usuario a la tarea."""
        if usuario not in self.usuarios_asignados:
            self.usuarios_asignados.append(usuario)
            
    def quitar_usuario(self, usuario):
        """Quita un usuario de la tarea."""
        if usuario in self.usuarios_asignados:
            self.usuarios_asignados.remove(usuario)

    def finalizar_tarea(self):
        """Marca la tarea como finalizada."""
        self.estado = "finalizada"

    def agregar_comentario(self, comentario, usuario):
        """Agrega un comentario a la tarea, incluyendo el usuario y la fecha."""
        self.comentarios.append((comentario, usuario, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def mostrar_info(self):
        """Muestra la información de la tarea en un formato legible."""
        info = "#"*90 + "\n"
        info += f"# Tarea: {self.nombre:<80}#\n"
        info += f"# Fecha de creación: {self.fecha_creacion:<68}#\n"
        info += f"# Usuarios asignados: {', '.join(self.usuarios_asignados) if self.usuarios_asignados else 'Ninguno':<67}#\n"
        info += f"# Estado: {self.estado:<79}#"
        info += "\n#{:<88}#\n".format(" Acciones :")
        for idx, (comentario, usuario, fecha) in enumerate(self.comentarios, start=1):
            info += f".   {idx}) Realizado por {usuario} el {fecha}) :\n"
            info += ".\t  "+"-"*79 + "#\n"
            info += f".\t{fill(comentario,80)}\n"
            info += ".\t  "+"-"*79 + "#\n"
        info += "#"*90 + "\n"
        return info

    def to_json(self):
        """Devuelve la tarea en formato JSON."""
        return {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion,
            "usuarios_asignados": self.usuarios_asignados,
            "comentarios": self.comentarios
        }
