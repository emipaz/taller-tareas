"""Módulo para gestión de usuarios.

Este módulo contiene la clase Usuario que maneja la autenticación
y gestión de usuarios en el sistema de tareas.
"""

import bcrypt
from typing import Optional


class Usuario:
    """Representa un usuario del sistema de gestión de tareas.
    
    Esta clase maneja la información del usuario incluyendo autenticación
    con contraseñas hasheadas usando bcrypt y gestión de roles.
    
    Attributes:
        nombre (str) : Nombre único del usuario.
        rol (str)    : Rol del usuario ('user' o 'admin').
    """
    
    def __init__(self, nombre: str, contraseña: Optional[str] = None, rol: str = "user") -> None:
        """Inicializa un nuevo usuario.
        
        Args:
            nombre: Nombre único del usuario.
            contraseña: Contraseña inicial del usuario. Si es None, el usuario
                       deberá establecerla en el primer login.
            rol: Rol del usuario. Debe ser 'user' o 'admin'.
            
        Raises:
            ValueError: Si el rol no es válido.
        """
        if rol not in ['user', 'admin']:
            raise ValueError("El rol debe ser 'user' o 'admin'")
            
        self.nombre     = nombre
        self.rol        = rol
        self.__password = self._hashear_password(contraseña) if contraseña else None
    
    def _hashear_password(self, contraseña: str) -> bytes:
        """Hashea la contraseña usando bcrypt.
        
        Args:
            contraseña: Contraseña en texto plano.
            
        Returns:
            Hash de la contraseña.
        """
        return bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())
    
    def verificar_password(self, contraseña: str) -> bool:
        """Verifica si la contraseña ingresada es correcta.
        
        Args:
            contraseña: Contraseña a verificar.
            
        Returns:
            True si la contraseña es correcta, False en caso contrario.
            También retorna False si no hay contraseña establecida.
        """
        if self.__password is None:
            return False
        return bcrypt.checkpw(contraseña.encode('utf-8'), self.__password)
    
    def cambiar_password(self, nueva_contraseña: str) -> bool:
        """Cambia la contraseña del usuario.
        
        Args:
            nueva_contraseña: Nueva contraseña del usuario.
            
        Returns:
            True si la contraseña se cambió exitosamente.
            
        Raises:
            ValueError: Si la contraseña está vacía.
        """
        if not nueva_contraseña or nueva_contraseña.strip() == "":
            raise ValueError("La contraseña no puede estar vacía")
            
        self.__password = self._hashear_password(nueva_contraseña)
        return True
    
    def tiene_password(self) -> bool:
        """Verifica si el usuario tiene una contraseña establecida.
        
        Returns:
            True si el usuario tiene contraseña, False en caso contrario.
        """
        return self.__password is not None
    
    def resetear_password(self) -> bool:
        """Resetea la contraseña del usuario (la elimina).
        
        Returns:
            True si la contraseña se reseteó exitosamente.
        """
        self.__password = None
        return True
    
    def es_admin(self) -> bool:
        """Verifica si el usuario es administrador.
        
        Returns:
            True si el usuario es admin, False en caso contrario.
        """
        return self.rol == "admin"
    
    def to_dict(self) -> dict:
        """Convierte el usuario a diccionario para serialización.
        
        Returns:
            Diccionario con los datos del usuario (sin la contraseña).
        """
        return {
            "nombre"         : self.nombre,
            "rol"            : self.rol,
            "tiene_password" : self.tiene_password()
        }
    
    def __str__(self) -> str:
        """Representación en string del usuario.
        
        Returns:
            String con la información básica del usuario.
        """
        return f"Usuario(nombre='{self.nombre}', rol='{self.rol}')"
    
    def __repr__(self) -> str:
        """Representación técnica del usuario.
        
        Returns:
            String con la representación técnica del usuario.
        """
        return self.__str__()
