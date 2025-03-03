import unittest
from unittest.mock import patch, mock_open
import os
import json
from tempfile import TemporaryDirectory
from usuario import Usuario
from tarea import Tarea
from utils import cargar_datos, guardar_datos, generar_password, hay_admin, guardar_json
from main import crear_usuario, eliminar_usuario, login, crear_tarea

class TestApp(unittest.TestCase):
    def setUp(self):
        self.usuarios = [Usuario("admin", "1234", "admin"), Usuario("juan", "5678", "usuario")]
        self.tareas = [Tarea("Tarea 1", "Descripción 1"), Tarea("Tarea 2", "Descripción 2")]

    def test_generar_password(self):
        password = generar_password(10)
        self.assertEqual(len(password), 10)
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(any(c.isalpha() for c in password))

    def test_hay_admin(self):
        self.assertTrue(hay_admin(self.usuarios))
        self.assertFalse(hay_admin([Usuario("juan", "5678", "usuario")]))
        self.assertFalse(hay_admin([]))

    def test_guardar_y_cargar_datos(self):
        with TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.dat")
            guardar_datos(self.usuarios, filepath)
            datos_cargados = cargar_datos(filepath)
            self.assertEqual(len(datos_cargados), len(self.usuarios))
            self.assertEqual(datos_cargados[0].nombre, "admin")

    @patch("builtins.input", side_effect=["juan", "5678",])
    @patch("getpass.getpass", return_value="5678")
    def test_login_exitoso(self, mock_getpass, mock_input):
        with patch("utils.cargar_datos", return_value=self.usuarios):
            usuario = login(self.usuarios)
            self.assertEqual(usuario.nombre, "juan")

    def test_guardar_json(self):
        with TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.json")
            guardar_json({"tarea": "Ejemplo"}, filepath)
            with open(filepath, "r") as f:
                data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["tarea"], "Ejemplo")

if __name__ == "__main__":
    unittest.main()
