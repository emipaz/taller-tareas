import unittest
from datetime import datetime
from tarea import Tarea

# test_tarea.py

class TestTarea(unittest.TestCase):

    def test_tarea_init(self):
        tarea = Tarea("Test Task", "This is a test task.")
        self.assertEqual(tarea.nombre, "Test Task")
        self.assertEqual(tarea.descripcion, "This is a test task.")
        self.assertEqual(tarea.estado, "pendiente")
        self.assertEqual(tarea.usuarios_asignados, [])
        self.assertEqual(tarea.comentarios, [])
        self.assertTrue(datetime.strptime(tarea.fecha_creacion, "%Y-%m-%d %H:%M:%S"))

    def test_agregar_usuario(self):
        tarea = Tarea("Test Task", "This is a test task.")
        tarea.agregar_usuario("user1")
        self.assertIn("user1", tarea.usuarios_asignados)

    def test_quitar_usuario(self):
        tarea = Tarea("Test Task", "This is a test task.", ["user1"])
        tarea.quitar_usuario("user1")
        self.assertNotIn("user1", tarea.usuarios_asignados)

    def test_finalizar_tarea(self):
        tarea = Tarea("Test Task", "This is a test task.")
        tarea.finalizar_tarea()
        self.assertEqual(tarea.estado, "finalizada")

    def test_agregar_comentario(self):
        tarea = Tarea("Test Task", "This is a test task.")
        tarea.agregar_comentario("This is a comment.", "user1")
        self.assertEqual(len(tarea.comentarios), 1)
        self.assertEqual(tarea.comentarios[0][0], "This is a comment.")
        self.assertEqual(tarea.comentarios[0][1], "user1")
        self.assertTrue(datetime.strptime(tarea.comentarios[0][2], "%Y-%m-%d %H:%M:%S"))

    def test_mostrar_info(self):
        tarea = Tarea("Test Task", "This is a test task.")
        tarea.agregar_usuario("user1")
        tarea.agregar_comentario("This is a comment.", "user1")
        info = tarea.mostrar_info()
        self.assertIn("Test Task", info)
        self.assertIn("user1", info)
        self.assertIn("This is a comment.", info)

    def test_to_json(self):
        tarea = Tarea("Test Task", "This is a test task.")
        tarea.agregar_usuario("user1")
        tarea.agregar_comentario("This is a comment.", "user1")
        tarea_json = tarea.to_json()
        self.assertEqual(tarea_json["nombre"], "Test Task")
        self.assertEqual(tarea_json["descripcion"], "This is a test task.")
        self.assertEqual(tarea_json["estado"], "pendiente")
        self.assertEqual(tarea_json["usuarios_asignados"], ["user1"])
        self.assertEqual(len(tarea_json["comentarios"]), 1)
        self.assertEqual(tarea_json["comentarios"][0][0], "This is a comment.")
        self.assertEqual(tarea_json["comentarios"][0][1], "user1")

if __name__ == '__main__':
    unittest.main()