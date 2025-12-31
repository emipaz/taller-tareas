"""Utilidades y widgets personalizados para la interfaz de usuario.

Este módulo contiene funciones de utilidad y widgets personalizados
que son reutilizados a lo largo de la aplicación, incluyendo
funciones de posicionamiento, widgets con scroll y tarjetas de información.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable


def center_window(window: tk.Toplevel | tk.Tk, width: int, height: int):
    """Centra una ventana en la pantalla.
    
    Args:
        window (tk.Toplevel | tk.Tk): Ventana a centrar.
        width (int): Ancho deseado de la ventana en píxeles.
        height (int): Alto deseado de la ventana en píxeles.
        
    Note:
        Calcula la posición para centrar la ventana basándose
        en las dimensiones de la pantalla.
    """
    # Obtener dimensiones de la pantalla
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calcular posición para centrar
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")


def apply_theme(root: tk.Tk):
    """Aplica un tema básico a la aplicación.
    
    Args:
        root (tk.Tk): Ventana raíz de la aplicación.
        
    Note:
        Configura colores, fuentes y estilos TTK para
        mantener consistencia visual en toda la aplicación.
    """
    # Configurar estilo general
    style = ttk.Style()
    
    # Configurar colores
    root.configure(bg='#f0f0f0')
    
    # Configurar fuentes
    default_font = ('Segoe UI', 9)
    header_font = ('Segoe UI', 12, 'bold')
    title_font = ('Segoe UI', 14, 'bold')
    
    # Configurar estilos para ttk
    style.configure('Title.TLabel', font=title_font)
    style.configure('Header.TLabel', font=header_font)
    style.configure('Custom.TButton', padding=5)


class ScrollableFrame(ttk.Frame):
    """Frame con scroll vertical."""
    
    def __init__(self, parent: tk.Widget):
        """Inicializa el frame scrollable.
        
        Args:
            parent (tk.Widget): Widget padre donde se ubicará el frame.
            
        Note:
            Configura automáticamente canvas, scrollbar y manejo
            de eventos de scroll con rueda del mouse.
        """
        super().__init__(parent)
        
        # Crear canvas y scrollbar
        self.canvas = tk.Canvas(self, bg='white')
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configurar scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Posicionar elementos
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """Maneja el scroll con la rueda del mouse.
        
        Args:
            event: Evento de rueda del mouse de tkinter.
            
        Note:
            Convierte el delta de la rueda en unidades de scroll
            para el canvas.
        """
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


class TaskCard(ttk.Frame):
    """Widget personalizado para mostrar información de una tarea."""
    
    def __init__(self, parent: tk.Widget, tarea, on_select: Optional[Callable] = None):
        """Inicializa la tarjeta de tarea.
        
        Args:
            parent (tk.Widget): Widget padre donde se mostrará la tarjeta.
            tarea (Tarea): Objeto Tarea a mostrar.
            on_select (Optional[Callable]): Callback ejecutado al seleccionar la tarea.
            
        Note:
            Crea una representación visual compacta con información
            clave de la tarea y botón de acción opcional.
        """
        super().__init__(parent, relief='ridge', borderwidth=1, padding=10)
        self.tarea = tarea
        self.on_select = on_select
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Crea los widgets de la tarjeta."""
        # Nombre de la tarea (título)
        name_label = ttk.Label(self, text=self.tarea.nombre, style='Header.TLabel')
        name_label.grid(row=0, column=0, sticky='w', columnspan=2)
        
        # Estado
        estado_color = '#28a745' if self.tarea.esta_finalizada() else '#ffc107'
        estado_label = ttk.Label(self, text=f"Estado: {self.tarea.estado}")
        estado_label.grid(row=1, column=0, sticky='w', pady=2)
        
        # Fecha de creación
        fecha_label = ttk.Label(self, text=f"Creada: {self.tarea.fecha_creacion}")
        fecha_label.grid(row=1, column=1, sticky='e', pady=2)
        
        # Descripción (truncada)
        desc_text = self.tarea.descripcion
        if len(desc_text) > 80:
            desc_text = desc_text[:77] + "..."
        desc_label = ttk.Label(self, text=desc_text, wraplength=400)
        desc_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=2)
        
        # Usuarios asignados
        usuarios_text = f"Usuarios: {', '.join(self.tarea.usuarios_asignados) if self.tarea.usuarios_asignados else 'Ninguno'}"
        users_label = ttk.Label(self, text=usuarios_text)
        users_label.grid(row=3, column=0, columnspan=2, sticky='w', pady=2)
        
        # Comentarios
        comentarios_text = f"Comentarios: {len(self.tarea.comentarios)}"
        comments_label = ttk.Label(self, text=comentarios_text)
        comments_label.grid(row=4, column=0, sticky='w', pady=2)
        
        # Botón de selección si se proporciona callback
        if self.on_select:
            select_btn = ttk.Button(self, text="Ver detalles", 
                                  command=lambda: self.on_select(self.tarea))
            select_btn.grid(row=4, column=1, sticky='e', pady=2)


class UserCard(ttk.Frame):
    """Widget personalizado para mostrar información de un usuario."""
    
    def __init__(self, parent: tk.Widget, usuario, on_select: Optional[Callable] = None):
        """Inicializa la tarjeta de usuario.
        
        Args:
            parent (tk.Widget): Widget padre donde se mostrará la tarjeta.
            usuario (Usuario): Objeto Usuario a mostrar.
            on_select (Optional[Callable]): Callback ejecutado al seleccionar usuario.
            
        Note:
            Muestra información esencial del usuario con
            botón de gestión opcional.
        """
        super().__init__(parent, relief='ridge', borderwidth=1, padding=10)
        self.usuario = usuario
        self.on_select = on_select
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Crea los widgets de la tarjeta."""
        # Nombre del usuario
        name_label = ttk.Label(self, text=self.usuario.nombre, style='Header.TLabel')
        name_label.grid(row=0, column=0, sticky='w')
        
        # Rol
        rol_color = '#007bff' if self.usuario.es_admin() else '#6c757d'
        rol_label = ttk.Label(self, text=f"Rol: {self.usuario.rol}")
        rol_label.grid(row=1, column=0, sticky='w', pady=2)
        
        # Estado de contraseña
        password_status = "Establecida" if self.usuario.tiene_password() else "Pendiente"
        password_label = ttk.Label(self, text=f"Contraseña: {password_status}")
        password_label.grid(row=2, column=0, sticky='w', pady=2)
        
        # Botón de selección si se proporciona callback
        if self.on_select:
            select_btn = ttk.Button(self, text="Gestionar", 
                                  command=lambda: self.on_select(self.usuario))
            select_btn.grid(row=0, column=1, rowspan=3, sticky='e', padx=10)


class ConfirmDialog:
    """Diálogo de confirmación personalizado."""
    
    def __init__(self, parent: tk.Widget, title: str, message: str):
        """Inicializa el diálogo de confirmación.
        
        Args:
            parent (tk.Widget): Widget padre del diálogo.
            title (str): Título de la ventana del diálogo.
            message (str): Mensaje a mostrar al usuario.
            
        Note:
            Crea un diálogo modal con botones Sí/No para confirmación.
        """
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        
        center_window(self.dialog, 400, 150)
        
        # Mensaje
        msg_label = ttk.Label(self.dialog, text=message, wraplength=350)
        msg_label.pack(pady=20)
        
        # Botones
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Sí", command=self._on_yes).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="No", command=self._on_no).pack(side='left', padx=10)
        
        # Configurar cierre
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_no)
        
    def _on_yes(self):
        """Confirma la acción.
        
        Establece el resultado como True y cierra el diálogo.
        """
        self.result = True
        self.dialog.destroy()
        
    def _on_no(self):
        """Cancela la acción.
        
        Establece el resultado como False y cierra el diálogo.
        """
        self.result = False
        self.dialog.destroy()
        
    def show(self) -> bool:
        """Muestra el diálogo y retorna el resultado.
        
        Returns:
            bool: True si se confirmó, False si se canceló.
            
        Note:
            Bloquea la ejecución hasta que el usuario
            toma una decisión.
        """
        self.dialog.wait_window()
        return self.result