"""Pruebas unitarias para la clase Usuario.

Este módulo contiene las pruebas unitarias para verificar el correcto
funcionamiento de la clase Usuario, incluyendo autenticación, gestión
de contraseñas y validación de roles.

Author:
    Sistema de Gestión de Tareas
    
Classes:
    TestUsuario: Clase de pruebas para la funcionalidad de usuarios.
"""

import unittest
import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core import Usuario
import bcrypt


class TestUsuario(unittest.TestCase):
    """Conjunto de pruebas para la clase Usuario.
    
    Esta clase contiene métodos de prueba para verificar:
    - Inicialización correcta de usuarios
    - Autenticación y verificación de contraseñas
    - Gestión de roles y permisos
    - Operaciones de seguridad
    """

    def test_usuario_init(self):
        """Prueba la inicialización básica de un usuario.
        
        Verifica que un usuario se cree correctamente con todos sus
        atributos: nombre, contraseña hasheada y rol asignado.
        """
        # Datos de prueba
        nombre = "testuser"
        contraseña = "password123"
        rol = "admin"
        
        # Crear usuario
        usuario = Usuario(nombre, contraseña, rol)
        
        # Verificaciones
        self.assertEqual(usuario.nombre, nombre)
        self.assertTrue(usuario.verificar_password(contraseña))
        self.assertEqual(usuario.rol, rol)

    def test_usuario_init_default_rol(self):
        """Prueba la inicialización con rol por defecto.
        
        Verifica que cuando no se especifica un rol, el usuario
        se crea automáticamente con rol 'user'.
        """
        # Datos de prueba (sin especificar rol)
        nombre = "testuser"
        contraseña = "password123"
        
        # Crear usuario sin rol específico
        usuario = Usuario(nombre, contraseña)
        
        # Verificar que se asigna el rol por defecto
        self.assertEqual(usuario.nombre, nombre)
        self.assertTrue(usuario.verificar_password(contraseña))
        self.assertEqual(usuario.rol, "user")

    def test_hashear_password(self):
        """Prueba el hashing de contraseñas con bcrypt.
        
        Verifica que las contraseñas se hashen correctamente y que
        cada hash sea único (incluso para la misma contraseña).
        """
        # Crear usuario y obtener hash
        usuario = Usuario("testuser", "password123")
        hashed_password = usuario._Usuario__password  # Acceder al atributo privado para testing
        
        # Verificar que el hash es válido
        self.assertTrue(bcrypt.checkpw("password123".encode('utf-8'), hashed_password))
        
        # Verificar que cada hash es único (sal diferente)
        otro_hash = usuario._hashear_password("password123")
        self.assertNotEqual(hashed_password, otro_hash)

    def test_verificar_password_correct(self):
        """Prueba la verificación correcta de contraseña.
        
        Verifica que el método de verificación funcione correctamente
        con la contraseña correcta.
        """
        usuario = Usuario("testuser", "password123")
        self.assertTrue(usuario.verificar_password("password123"))

    def test_verificar_password_incorrect(self):
        """Prueba la verificación con contraseña incorrecta.
        
        Verifica que el método de verificación rechace contraseñas
        incorrectas apropiadamente.
        """
        usuario = Usuario("testuser", "password123")
        self.assertFalse(usuario.verificar_password("wrongpassword"))

    def test_cambiar_password(self):
        """Prueba el cambio de contraseña de usuario.
        
        Verifica que se pueda cambiar la contraseña exitosamente
        y que la antigua contraseña ya no funcione.
        """
        # Crear usuario con contraseña inicial
        usuario = Usuario("testuser", "password123")
        nueva_contraseña = "newpassword123"
        
        # Cambiar contraseña
        usuario.cambiar_password(nueva_contraseña)
        
        # Verificar que la nueva contraseña funciona y la anterior no
        self.assertTrue(usuario.verificar_password(nueva_contraseña))
        self.assertFalse(usuario.verificar_password("password123"))

if __name__ == '__main__':
    unittest.main()
