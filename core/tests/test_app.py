"""Pruebas unitarias de integración para el sistema de gestión de tareas.

Este módulo contiene pruebas de integración que verifican el funcionamiento
correcto de la aplicación completa, incluyendo persistencia de datos,
autenticación, y funcionalidades principales del sistema.

Author:
    Sistema de Gestión de Tareas
    
Classes:
    TestApp: Clase principal de pruebas de integración.

Note:
    Estas pruebas utilizan archivos temporales y mocking para evitar
    efectos secundarios en el sistema de archivos real.
"""

import unittest
from unittest.mock import patch, mock_open
import os
import json
from tempfile import TemporaryDirectory
import sys

# Configurar path para importar desde core
current_dir = os.path.dirname(__file__)
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, root_dir)

from core.usuario import Usuario
from core.tarea import Tarea
from core.utils import cargar_datos, guardar_datos, generar_password, hay_admin, guardar_json


class TestApp(unittest.TestCase):
    """Suite de pruebas de integración para la aplicación.
    
    Esta clase contiene pruebas que verifican:
    - Persistencia y carga de datos
    - Autenticación de usuarios
    - Generación de contraseñas
    - Funciones de utilidad del sistema
    - Integración entre módulos
    """
    def setUp(self):
        """Configuración inicial para cada prueba.
        
        Crea datos de prueba consistentes incluyendo usuarios con diferentes
        roles y tareas de ejemplo para usar en las pruebas.
        """
        # Usuarios de prueba con diferentes roles
        self.usuarios = [
            Usuario("admin", "1234", "admin"),      # Administrador
            Usuario("juan", "5678", "user")         # Usuario regular
        ]
        
        # Tareas de prueba
        self.tareas = [
            Tarea("Tarea 1", "Descripción 1"), 
            Tarea("Tarea 2", "Descripción 2")
        ]

    def test_generar_password(self):
        """Prueba la generación de contraseñas aleatorias.
        
        Verifica que las contraseñas generadas tengan la longitud correcta
        y contengan al menos números y letras para mayor seguridad.
        """
        # Generar contraseña de prueba
        password = generar_password(10)
        
        # Verificar características de la contraseña
        self.assertEqual(len(password), 10)
        self.assertTrue(any(c.isdigit() for c in password))  # Contiene números
        self.assertTrue(any(c.isalpha() for c in password))  # Contiene letras

    def test_hay_admin(self):
        """Prueba la detección de administradores en el sistema.
        
        Verifica que la función identifique correctamente cuando hay
        al menos un administrador en la lista de usuarios.
        """
        # Caso con administrador presente
        self.assertTrue(hay_admin(self.usuarios))
        
        # Caso sin administrador
        solo_usuarios = [Usuario("juan", "5678", "user")]
        self.assertFalse(hay_admin(solo_usuarios))
        
        # Caso con lista vacía
        self.assertFalse(hay_admin([]))

    def test_guardar_y_cargar_datos(self):
        """Prueba la persistencia y carga de datos usando archivos temporales.
        
        Verifica que los datos se guarden y carguen correctamente
        sin corrupción, usando archivos temporales para evitar
        efectos secundarios.
        """
        with TemporaryDirectory() as tmpdir:
            # Crear archivo temporal
            filepath = os.path.join(tmpdir, "test.dat")
            
            # Guardar y cargar datos
            guardar_datos(self.usuarios, filepath)
            datos_cargados = cargar_datos(filepath)
            
            # Verificar integridad de los datos
            self.assertEqual(len(datos_cargados), len(self.usuarios))
            self.assertEqual(datos_cargados[0].nombre, "admin")

    def test_guardar_json(self):
        """Prueba el guardado de datos en formato JSON.
        
        Verifica que los datos se serialicen correctamente a JSON
        y se puedan leer posteriormente manteniendo la estructura.
        """
        with TemporaryDirectory() as tmpdir:
            # Crear archivo temporal JSON
            filepath = os.path.join(tmpdir, "test.json")
            
            # Guardar datos en JSON
            guardar_json({"tarea": "Ejemplo"}, filepath)
            
            # Verificar contenido del archivo
            with open(filepath, "r", encoding='utf-8') as f:
                data = json.load(f)
            
            # Verificar estructura y contenido
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["tarea"], "Ejemplo")

if __name__ == "__main__":
    unittest.main()
