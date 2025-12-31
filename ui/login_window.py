"""Módulo de autenticación y login.

Este módulo contiene las clases necesarias para manejar la autenticación
de usuarios, incluyendo la ventana de login, creación de administrador
inicial y establecimiento de contraseñas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from .ui_utils import center_window, apply_theme


class LoginWindow:
    """Ventana de login para autenticación de usuarios."""
    
    def __init__(self, parent: tk.Tk, gestor, on_success: Callable):
        """Inicializa la ventana de login.
        
        Args:
            parent (tk.Tk): Ventana padre principal.
            gestor (GestorSistema): Instancia del gestor del sistema.
            on_success (Callable): Callback ejecutado tras login exitoso.
        """
        self.parent = parent
        self.gestor = gestor
        self.on_success = on_success
        
        self.window = None
        
    def show(self):
        """Muestra la ventana de login.
        
        Crea y configura la ventana de login como ventana modal,
        verifica la existencia de administradores y presenta la interfaz.
        """
        self.window = tk.Toplevel(self.parent)
        self.window.title("Iniciar Sesión")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.window.grab_set()
        
        center_window(self.window, 400, 300)
        
        # Configurar cierre
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._create_widgets()
        self._check_admin_exists()
        
    def _create_widgets(self):
        """Crea los widgets de la ventana de login.
        
        Construye la interfaz completa incluyendo campos de usuario,
        contraseña y botones de acción.
        """
        # Frame principal
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Sistema de Gestión de Tareas", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Frame de login
        login_frame = ttk.LabelFrame(main_frame, text="Iniciar Sesión", padding=15)
        login_frame.pack(fill='x', pady=10)
        
        # Usuario
        ttk.Label(login_frame, text="Usuario:").grid(row=0, column=0, sticky='w', pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(login_frame, textvariable=self.username_var, width=25)
        self.username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Contraseña
        ttk.Label(login_frame, text="Contraseña:").grid(row=1, column=0, sticky='w', pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(login_frame, textvariable=self.password_var, 
                                       show='*', width=25)
        self.password_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Botones
        btn_frame = ttk.Frame(login_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="Entrar", command=self._login).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Crear Admin", command=self._show_create_admin).pack(side='left', padx=5)
        
        # Configurar Enter
        self.window.bind('<Return>', lambda e: self._login())
        
        # Focus en username
        self.username_entry.focus()
        
    def _check_admin_exists(self):
        """Verifica si existe al menos un administrador.
        
        Comprueba la existencia de administradores en el sistema.
        Si no hay ninguno o hay errores en los datos, ofrece opciones
        para crear un administrador o limpiar datos corruptos.
        """
        try:
            if not self.gestor.existe_admin():
                messagebox.showinfo("Primer uso", 
                                  "No hay administradores en el sistema.\n"
                                  "Debe crear al menos un administrador para comenzar.")
                self._show_create_admin()
        except Exception as e:
            # Si hay error al verificar (archivos corruptos, etc.)
            result = messagebox.askyesno("Error de datos",
                                       f"Error al cargar datos del sistema: {e}\n\n"
                                       "¿Desea limpiar los archivos corruptos y comenzar de nuevo?")
            if result:
                self.gestor.limpiar_archivos_corruptos()
                self._show_create_admin()
    
    def _login(self):
        """Procesa el intento de login.
        
        Valida las credenciales ingresadas, maneja casos especiales
        como usuarios sin contraseña establecida y ejecuta el callback
        de éxito si la autenticación es correcta.
        """
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username:
            messagebox.showerror("Error", "Por favor ingrese un nombre de usuario")
            return
            
        if not password:
            messagebox.showerror("Error", "Por favor ingrese una contraseña")
            return
            
        try:
            usuario, mensaje = self.gestor.autenticar_usuario(username, password)
            
            if usuario:
                self.window.destroy()
                self.on_success(usuario)
            elif mensaje == "sin_password":
                self._show_set_password(username)
            else:
                messagebox.showerror("Error de autenticación", mensaje)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la autenticación: {e}")
    
    def _show_create_admin(self):
        """Muestra el diálogo para crear administrador.
        
        Abre el diálogo modal para crear el primer administrador
        del sistema.
        """
        CreateAdminDialog(self.window, self.gestor)
        
    def _show_set_password(self, username: str):
        """Muestra el diálogo para establecer contraseña inicial.
        
        Abre el diálogo para que un usuario establezca su contraseña
        inicial cuando aún no la ha configurado.
        
        Args:
            username (str): Nombre del usuario que debe establecer contraseña.
        """
        SetPasswordDialog(self.window, self.gestor, username)
        
    def _on_close(self):
        """Maneja el cierre de la ventana.
        
        Termina la aplicación completamente cuando se cierra
        la ventana de login.
        """
        self.parent.quit()
        self.parent.destroy()


class CreateAdminDialog:
    """Diálogo para crear un administrador."""
    
    def __init__(self, parent: tk.Widget, gestor):
        """Inicializa el diálogo de creación de administrador.
        
        Args:
            parent (tk.Widget): Ventana padre del diálogo.
            gestor (GestorSistema): Instancia del gestor del sistema.
        """
        self.gestor = gestor
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Crear Administrador")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        
        center_window(self.dialog, 350, 200)
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Crear Administrador", style='Header.TLabel').pack(pady=(0, 15))
        
        # Usuario
        user_frame = ttk.Frame(main_frame)
        user_frame.pack(fill='x', pady=5)
        ttk.Label(user_frame, text="Usuario:").pack(side='left')
        self.username_var = tk.StringVar()
        ttk.Entry(user_frame, textvariable=self.username_var).pack(side='right')
        
        # Contraseña
        pass_frame = ttk.Frame(main_frame)
        pass_frame.pack(fill='x', pady=5)
        ttk.Label(pass_frame, text="Contraseña:").pack(side='left')
        self.password_var = tk.StringVar()
        ttk.Entry(pass_frame, textvariable=self.password_var, show='*').pack(side='right')
        
        # Confirmar contraseña
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.pack(fill='x', pady=5)
        ttk.Label(confirm_frame, text="Confirmar:").pack(side='left')
        self.confirm_var = tk.StringVar()
        ttk.Entry(confirm_frame, textvariable=self.confirm_var, show='*').pack(side='right')
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="Crear", command=self._create_admin).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy).pack(side='left', padx=5)
        
    def _create_admin(self):
        """Crea el administrador.
        
        Valida los datos ingresados, verifica que las contraseñas
        coincidan y crea el administrador en el sistema.
        
        Note:
            Requiere mínimo 4 caracteres para la contraseña.
        """
        username = self.username_var.get().strip()
        password = self.password_var.get()
        confirm = self.confirm_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
            
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
            
        if len(password) < 4:
            messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres")
            return
            
        try:
            exito, mensaje = self.gestor.crear_admin(username, password)
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", mensaje)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear administrador: {e}")


class SetPasswordDialog:
    """Diálogo para establecer contraseña inicial."""
    
    def __init__(self, parent: tk.Widget, gestor, username: str):
        """Inicializa el diálogo de establecimiento de contraseña.
        
        Args:
            parent (tk.Widget): Ventana padre del diálogo.
            gestor (GestorSistema): Instancia del gestor del sistema.
            username (str): Nombre del usuario que establecerá contraseña.
        """
        self.gestor = gestor
        self.username = username
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Establecer Contraseña")
        self.dialog.geometry("350x180")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        
        center_window(self.dialog, 350, 180)
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text=f"Establecer contraseña para: {self.username}", 
                 style='Header.TLabel').pack(pady=(0, 15))
        
        # Contraseña
        pass_frame = ttk.Frame(main_frame)
        pass_frame.pack(fill='x', pady=5)
        ttk.Label(pass_frame, text="Contraseña:").pack(side='left')
        self.password_var = tk.StringVar()
        ttk.Entry(pass_frame, textvariable=self.password_var, show='*').pack(side='right')
        
        # Confirmar contraseña
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.pack(fill='x', pady=5)
        ttk.Label(confirm_frame, text="Confirmar:").pack(side='left')
        self.confirm_var = tk.StringVar()
        ttk.Entry(confirm_frame, textvariable=self.confirm_var, show='*').pack(side='right')
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="Establecer", command=self._set_password).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy).pack(side='left', padx=5)
        
    def _set_password(self):
        """Establece la contraseña.
        
        Valida que las contraseñas coincidan, verifica la longitud
        mínima y establece la contraseña en el sistema.
        
        Note:
            Requiere mínimo 4 caracteres para la contraseña.
        """
        password = self.password_var.get()
        confirm = self.confirm_var.get()
        
        if not password:
            messagebox.showerror("Error", "La contraseña no puede estar vacía")
            return
            
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
            
        if len(password) < 4:
            messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres")
            return
            
        try:
            exito, mensaje = self.gestor.establecer_password_inicial(self.username, password)
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", mensaje)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al establecer contraseña: {e}")