#!/usr/bin/env python3
"""Aplicación principal de gestión de tareas con interfaz Tkinter.

Esta aplicación proporciona una interfaz gráfica completa para el sistema 
de gestión de tareas, permitiendo a administradores y usuarios gestionar 
tareas, usuarios y configuraciones del sistema.

Características principales:
    - Login con autenticación segura
    - Panel de administrador con gestión completa
    - Panel de usuario para tareas personales
    - Creación y gestión de tareas
    - Gestión de usuarios y permisos
    - Reportes y estadísticas
    - Sistema de comentarios en tareas

Example:
    Ejecutar la aplicación:
        $ python app_tkinter.py

Note:
    Requiere Python 3.6+ y tkinter (incluido con Python).
    En el primer uso se debe crear un administrador.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui import MainWindow
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrese de que todos los archivos de la UI están presentes.")
    sys.exit(1)


def main():
    """Función principal de la aplicación.
    
    Inicializa y ejecuta la aplicación GUI, manejando errores
    y verificando requisitos del sistema.
    
    Raises:
        SystemExit: Si Python < 3.6 o error crítico de importación.
    """
    try:
        # Verificar versión de Python
        if sys.version_info < (3, 6):
            messagebox.showerror("Error", "Esta aplicación requiere Python 3.6 o superior")
            return
            
        # Crear y ejecutar la aplicación
        app = MainWindow()
        app.run()
        
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario")
    except Exception as e:
        messagebox.showerror("Error Fatal", f"Error inesperado: {e}")
        print(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()