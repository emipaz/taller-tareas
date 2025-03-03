import bcrypt

class Usuario:
    def __init__(self, nombre, contraseña, rol="user"):
        self.nombre = nombre
        self.__password = self.hashear_password(contraseña)
        self.rol = rol

    def hashear_password(self, contraseña):
        """Hashea la contraseña usando bcrypt."""
        return bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

    def verificar_password(self, contraseña):
        """Verifica la contraseña ingresada con el hash almacenado."""
        return bcrypt.checkpw(contraseña.encode('utf-8'), self.__password)
    
    def cambiar_password(self, nueva_contraseña):
        """Cambia la contraseña del usuario."""
        self.__password = self.hashear_password(nueva_contraseña)
