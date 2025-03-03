import unittest
from usuario import Usuario
import bcrypt

class TestUsuario(unittest.TestCase):

    def test_usuario_init(self):
        nombre = "testuser"
        contraseña = "password123"
        rol = "admin"
        
        usuario = Usuario(nombre, contraseña, rol)
        
        self.assertEqual(usuario.nombre, nombre)
        self.assertTrue(usuario.verificar_password(contraseña))
        self.assertEqual(usuario.rol, rol)

    def test_usuario_init_default_rol(self):
        nombre = "testuser"
        contraseña = "password123"
        
        usuario = Usuario(nombre, contraseña)
        
        self.assertEqual(usuario.nombre, nombre)
        self.assertTrue(usuario.verificar_password(contraseña))
        self.assertEqual(usuario.rol, "user")

    def test_hashear_password(self):
        usuario = Usuario("testuser", "password123")
        hashed_password = usuario.hashear_password("password123")
        
        self.assertTrue(bcrypt.checkpw("password123".encode('utf-8'), hashed_password))
        self.assertNotEqual(hashed_password, usuario.hashear_password("password123"))

    def test_verificar_password_correct(self):
        usuario = Usuario("testuser", "password123")
        self.assertTrue(usuario.verificar_password("password123"))

    def test_verificar_password_incorrect(self):
        usuario = Usuario("testuser", "password123")
        self.assertFalse(usuario.verificar_password("wrongpassword"))

    def test_cambiar_password(self):
        usuario = Usuario("testuser", "password123")
        nueva_contraseña = "newpassword123"
        
        usuario.cambiar_password(nueva_contraseña)
        
        self.assertTrue(usuario.verificar_password(nueva_contraseña))
        self.assertFalse(usuario.verificar_password("password123"))

if __name__ == '__main__':
    unittest.main()
