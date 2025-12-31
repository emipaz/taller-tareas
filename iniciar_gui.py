"""Script de inicio para la aplicación GUI de gestión de tareas.

Este script proporciona un punto de entrada simple para la aplicación
con manejo robusto de errores y mensajes informativos.

Example:
    Ejecutar la aplicación:
        $ python iniciar_gui.py
        
Note:
    Incluye manejo de errores de importación y pausa para
    mostrar mensajes de error antes del cierre.
"""

import os
import sys

# Asegurar que podemos importar los módulos del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

if __name__ == "__main__":
    try:
        from app_tkinter import main
        main()
    except ImportError as e:
        print(f"Error de importación: {e}")
        print("Verifique que todos los archivos estén presentes")
        input("Presione Enter para salir...")
    except Exception as e:
        print(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("Presione Enter para salir...")