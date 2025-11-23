"""Pruebas unitarias para la clase Tarea.

Este módulo contiene las pruebas unitarias para verificar el correcto
funcionamiento de la clase Tarea, incluyendo creación, asignación de usuarios,
gestión de comentarios y cambios de estado.

Author:
    Sistema de Gestión de Tareas
    
Classes:
    TestTarea: Clase de pruebas para la funcionalidad de tareas.
"""

import unittest
from datetime import datetime
from core.tarea import Tarea


class TestTarea(unittest.TestCase):
    """Conjunto de pruebas para la clase Tarea.
    
    Esta clase contiene métodos de prueba para verificar:
    - Inicialización correcta de tareas
    - Asignación y gestión de usuarios
    - Sistema de comentarios
    - Cambios de estado (pendiente/finalizada)
    - Serialización y formato de datos
    """

    def test_tarea_init(self):
        """Prueba la inicialización básica de una tarea.
        
        Verifica que una tarea se cree correctamente con todos sus
        atributos por defecto: nombre, descripción, estado pendiente,
        listas vacías y timestamp válido.
        """
        # Crear tarea de prueba
        tarea = Tarea("Test Task", "This is a test task.")
        
        # Verificar inicialización correcta
        self.assertEqual(tarea.nombre, "Test Task")
        self.assertEqual(tarea.descripcion, "This is a test task.")
        self.assertEqual(tarea.estado, "pendiente")
        self.assertEqual(tarea.usuarios_asignados, [])
        self.assertEqual(tarea.comentarios, [])
        
        # Verificar que la fecha de creación es válida
        self.assertTrue(datetime.strptime(tarea.fecha_creacion, "%Y-%m-%d %H:%M:%S"))

    def test_agregar_usuario(self):
        """Prueba la asignación de usuarios a una tarea.
        
        Verifica que se puedan agregar usuarios correctamente
        a la lista de asignados de una tarea.
        """
        tarea = Tarea("Test Task", "This is a test task.")
        tarea.agregar_usuario("user1")
        self.assertIn("user1", tarea.usuarios_asignados)

    def test_quitar_usuario(self):
        """Prueba la remoción de usuarios de una tarea.
        
        Verifica que se puedan quitar usuarios correctamente
        de la lista de asignados de una tarea.
        """
        # Crear tarea con usuario pre-asignado
        tarea = Tarea("Test Task", "This is a test task.", ["user1"])
        tarea.quitar_usuario("user1")
        self.assertNotIn("user1", tarea.usuarios_asignados)

    def test_finalizar_tarea(self):
        """Prueba el cambio de estado de tarea a finalizada.
        
        Verifica que una tarea pueda ser marcada como finalizada
        y que su estado cambie correctamente.
        """
        tarea = Tarea("Test Task", "This is a test task.")
        tarea.finalizar_tarea()
        self.assertEqual(tarea.estado, "finalizada")

    def test_agregar_comentario(self):
        """Prueba la funcionalidad de comentarios en tareas.
        
        Verifica que se puedan agregar comentarios correctamente
        con usuario y timestamp válidos.
        """
        tarea = Tarea("Test Task", "This is a test task.")
        tarea.agregar_comentario("This is a comment.", "user1")
        
        # Verificar que el comentario se agregó correctamente
        self.assertEqual(len(tarea.comentarios), 1)
        self.assertEqual(tarea.comentarios[0][0], "This is a comment.")
        self.assertEqual(tarea.comentarios[0][1], "user1")
        # Verificar que el timestamp es válido
        self.assertTrue(datetime.strptime(tarea.comentarios[0][2], "%Y-%m-%d %H:%M:%S"))

    def test_obtener_info_detallada(self):
        """Prueba la generación de información detallada de tarea.
        
        Verifica que el método obtener_info_detallada genere
        un string formateado con toda la información relevante.
        """
        # Preparar tarea con datos completos
        tarea = Tarea("Test Task", "This is a test task.")
        tarea.agregar_usuario("user1")
        tarea.agregar_comentario("This is a comment.", "user1")
        
        # Obtener información detallada
        info = tarea.obtener_info_detallada()
        
        # Verificar que contiene los elementos esperados
        self.assertIn("Test Task", info)
        self.assertIn("user1", info)
        self.assertIn("This is a comment.", info)

    def test_to_json(self):
        """Prueba la serialización de tarea a formato JSON.
        
        Verifica que el método to_json convierta correctamente
        todos los datos de la tarea a un diccionario serializable.
        """
        # Preparar tarea con datos completos
        tarea = Tarea("Test Task", "This is a test task.")
        tarea.agregar_usuario("user1")
        tarea.agregar_comentario("This is a comment.", "user1")
        
        # Convertir a JSON
        tarea_json = tarea.to_json()
        
        # Verificar estructura y contenido del JSON
        self.assertEqual(tarea_json["nombre"], "Test Task")
        self.assertEqual(tarea_json["descripcion"], "This is a test task.")
        self.assertEqual(tarea_json["estado"], "pendiente")
        self.assertEqual(tarea_json["usuarios_asignados"], ["user1"])
        self.assertEqual(len(tarea_json["comentarios"]), 1)
        self.assertEqual(tarea_json["comentarios"][0][0], "This is a comment.")
        self.assertEqual(tarea_json["comentarios"][0][1], "user1")

if __name__ == '__main__':
    unittest.main()