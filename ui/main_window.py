"""Ventana principal de la aplicación de gestión de tareas.

Este módulo contiene la clase MainWindow que actúa como coordinador
principal de la aplicación, manejando el flujo de autenticación y
navegación entre diferentes paneles según el rol del usuario.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os

# Agregar el directorio padre al path para importar core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import GestorSistema
from .login_window import LoginWindow
from .admin_panel import AdminPanel
from .user_panel import UserPanel
from .ui_utils import center_window, apply_theme


class MainWindow:
    """Ventana principal de la aplicación que maneja el flujo principal."""
    
    def __init__(self):
        """Inicializa la ventana principal.
        
        Configura la ventana principal, inicializa el gestor del sistema,
        aplica el tema visual y prepara la interfaz para el login inicial.
        """
        self.root = tk.Tk()
        self.root.title("Sistema de Gestión de Tareas")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Inicializar el gestor del sistema
        self.gestor = GestorSistema()
        
        # Variables de sesión
        self.usuario_actual = None
        self.panel_actual   = None
        
        # Aplicar tema y centrar ventana
        apply_theme(self.root)
        center_window(self.root, 800, 600)
        
        # Configurar el cierre de la ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Mostrar ventana de login al inicio
        self.mostrar_login()
    
    def mostrar_login(self):
        """Muestra la ventana de login.
        
        Oculta la ventana principal y presenta la interfaz de autenticación.
        Se ejecuta al inicio de la aplicación y después del logout.
        """
        # Ocultar ventana principal
        self.root.withdraw()
        
        # Crear y mostrar ventana de login
        login_window = LoginWindow(self.root, self.gestor, self.on_login_success)
        login_window.show()
    
    def on_login_success(self, usuario):
        """Callback ejecutado cuando el login es exitoso.
        
        Restaura la ventana principal y redirige al panel apropiado
        según el rol del usuario autenticado.
        
        Args:
            usuario (Usuario): Usuario autenticado exitosamente.
        """
        self.usuario_actual = usuario
        self.root.deiconify()  # Mostrar ventana principal
        
        # Mostrar panel apropiado según el rol
        if usuario.es_admin():
            self.mostrar_panel_admin()
        else:
            self.mostrar_panel_usuario()
    
    def mostrar_panel_admin(self):
        """Muestra el panel de administrador.
        
        Limpia la ventana y carga el panel administrativo con todas
        las funcionalidades de gestión del sistema.
        """
        self.limpiar_ventana()
        self.panel_actual = AdminPanel(self.root, self.gestor, self.usuario_actual, self.logout)
    
    def mostrar_panel_usuario(self):
        """Muestra el panel de usuario.
        
        Limpia la ventana y carga el panel de usuario regular con
        funcionalidades limitadas para gestión personal de tareas.
        """
        self.limpiar_ventana()
        self.panel_actual = UserPanel(self.root, self.gestor, self.usuario_actual, self.logout)
    
    def limpiar_ventana(self):
        """Limpia el contenido de la ventana principal.
        
        Destruye todos los widgets hijos de la ventana principal
        para preparar el cambio de panel.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def logout(self):
        """Cierra sesión y vuelve al login.
        
        Limpia la sesión actual, resetea las variables de estado
        y redirige a la ventana de autenticación.
        """
        self.usuario_actual = None
        self.panel_actual   = None
        self.mostrar_login()
    
    def on_close(self):
        """Maneja el cierre de la aplicación.
        
        Muestra una confirmación antes de cerrar y termina
        la aplicación de forma segura.
        """
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir?"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Inicia el bucle principal de la aplicación.
        
        Ejecuta el mainloop de tkinter con manejo de excepciones
        para interrupciones del teclado.
        
        Raises:
            KeyboardInterrupt: Capturada y manejada graciosamente.
        """
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_close()


if __name__ == "__main__":
    app = MainWindow()
    app.run()