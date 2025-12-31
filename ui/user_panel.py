"""Panel de usuario para gestión personal de tareas.

Este módulo contiene la clase UserPanel que proporciona una interfaz
especializada para usuarios regulares, permitiendo ver sus tareas
asignadas y gestionar su perfil personal.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from .ui_utils import ScrollableFrame, TaskCard
from .dialogs import TaskDetailDialog, ChangePasswordDialog


class UserPanel:
    """Panel principal para usuarios regulares."""
    
    def __init__(self, parent: tk.Widget, gestor, usuario, logout_callback: Callable):
        """Inicializa el panel de usuario.
        
        Args:
            parent (tk.Widget): Widget padre donde se mostrará el panel.
            gestor (GestorSistema): Instancia del gestor del sistema.
            usuario (Usuario): Usuario regular actual.
            logout_callback (Callable): Función para cerrar sesión.
        """
        self.parent = parent
        self.gestor = gestor
        self.usuario = usuario
        self.logout_callback = logout_callback
        
        # Cargar datos
        self._load_data()
        
        # Crear interface
        self._create_widgets()
        
        # Mostrar pestaña inicial
        self.notebook.select(0)
        
    def _load_data(self):
        """Carga los datos del usuario.
        
        Carga las tareas asignadas al usuario actual desde el
        gestor del sistema, manejando errores de carga.
        """
        try:
            self.gestor.cargar_datos()
            self.user_tasks = self.gestor.obtener_tareas_usuario(self.usuario.nombre)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {e}")
            self.user_tasks = []
        
    def _create_widgets(self):
        """Crea los widgets del panel."""
        # Header
        self._create_header()
        
        # Notebook con pestañas
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Pestañas
        self._create_my_tasks_tab()
        self._create_profile_tab()
        
    def _create_header(self):
        """Crea el header del panel."""
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        # Título y usuario
        title_label = ttk.Label(header_frame, text="Mis Tareas", 
                               style='Title.TLabel')
        title_label.pack(side='left')
        
        # Frame derecho con info de usuario
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side='right')
        
        user_label = ttk.Label(right_frame, text=f"Usuario: {self.usuario.nombre}")
        user_label.pack(side='left', padx=10)
        
        ttk.Button(right_frame, text="Cerrar Sesión", 
                  command=self.logout_callback).pack(side='left')
        
        # Separador
        ttk.Separator(self.parent, orient='horizontal').pack(fill='x', padx=10, pady=5)
        
    def _create_my_tasks_tab(self):
        """Crea la pestaña de mis tareas.
        
        Construye la interfaz principal del usuario mostrando
        resumen de tareas, filtros y lista de tareas asignadas.
        """
        tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(tasks_frame, text="Mis Tareas")
        
        # Resumen
        summary_frame = ttk.LabelFrame(tasks_frame, text="Resumen", padding=10)
        summary_frame.pack(fill='x', padx=10, pady=5)
        
        self._create_task_summary(summary_frame)
        
        # Filtros y toolbar
        toolbar = ttk.Frame(tasks_frame)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(toolbar, text="Actualizar", 
                  command=self._refresh_my_tasks).pack(side='left', padx=5)
        
        # Filtros
        filter_frame = ttk.Frame(toolbar)
        filter_frame.pack(side='right')
        
        ttk.Label(filter_frame, text="Mostrar:").pack(side='left', padx=5)
        self.task_filter_var = tk.StringVar(value="todas")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.task_filter_var,
                                   values=["todas", "pendientes", "finalizadas"],
                                   state="readonly", width=12)
        filter_combo.pack(side='left', padx=5)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_my_tasks())
        
        # Lista de tareas con scroll
        self.tasks_scroll_frame = ScrollableFrame(tasks_frame)
        self.tasks_scroll_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self._refresh_my_tasks()
        
    def _create_profile_tab(self):
        """Crea la pestaña de perfil del usuario.
        
        Construye la interfaz de perfil con información personal,
        estadísticas y opciones de gestión de cuenta.
        """
        profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(profile_frame, text="Perfil")
        
        # Frame principal con scroll
        main_frame = ScrollableFrame(profile_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        content = main_frame.scrollable_frame
        
        # Información del usuario
        info_frame = ttk.LabelFrame(content, text="Información Personal", padding=15)
        info_frame.pack(fill='x', pady=5)
        
        info_grid = ttk.Frame(info_frame)
        info_grid.pack()
        
        ttk.Label(info_grid, text="Nombre de usuario:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Label(info_grid, text=self.usuario.nombre, style='Header.TLabel').grid(row=0, column=1, sticky='w', padx=15, pady=5)
        
        ttk.Label(info_grid, text="Rol:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Label(info_grid, text=self.usuario.rol).grid(row=1, column=1, sticky='w', padx=15, pady=5)
        
        password_status = "Establecida" if self.usuario.tiene_password() else "No establecida"
        ttk.Label(info_grid, text="Contraseña:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        ttk.Label(info_grid, text=password_status).grid(row=2, column=1, sticky='w', padx=15, pady=5)
        
        # Estadísticas personales
        stats_frame = ttk.LabelFrame(content, text="Mis Estadísticas", padding=15)
        stats_frame.pack(fill='x', pady=5)
        
        self._create_personal_stats(stats_frame)
        
        # Acciones
        actions_frame = ttk.LabelFrame(content, text="Acciones", padding=15)
        actions_frame.pack(fill='x', pady=5)
        
        ttk.Button(actions_frame, text="Cambiar Contraseña", 
                  command=self._change_password).pack(pady=5)
                  
    def _create_task_summary(self, parent: ttk.Frame):
        """Crea el resumen de tareas.
        
        Args:
            parent (ttk.Frame): Frame padre donde mostrar el resumen.
            
        Note:
            Muestra totales de tareas pendientes y finalizadas
            en formato de grid horizontal.
        """
        total = len(self.user_tasks)
        pendientes = len([t for t in self.user_tasks if not t.esta_finalizada()])
        finalizadas = len([t for t in self.user_tasks if t.esta_finalizada()])
        
        summary_grid = ttk.Frame(parent)
        summary_grid.pack()
        
        ttk.Label(summary_grid, text="Total de tareas:", style='Header.TLabel').grid(
            row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(summary_grid, text=str(total)).grid(
            row=0, column=1, padx=10, pady=2)
            
        ttk.Label(summary_grid, text="Pendientes:", style='Header.TLabel').grid(
            row=0, column=2, sticky='w', padx=15, pady=2)
        ttk.Label(summary_grid, text=str(pendientes)).grid(
            row=0, column=3, padx=10, pady=2)
            
        ttk.Label(summary_grid, text="Finalizadas:", style='Header.TLabel').grid(
            row=0, column=4, sticky='w', padx=15, pady=2)
        ttk.Label(summary_grid, text=str(finalizadas)).grid(
            row=0, column=5, padx=10, pady=2)
            
    def _create_personal_stats(self, parent: ttk.Frame):
        """Crea estadísticas personales.
        
        Args:
            parent (ttk.Frame): Frame padre donde mostrar las estadísticas.
            
        Note:
            Incluye porcentaje de completitud y barra de progreso visual.
        """
        stats_grid = ttk.Frame(parent)
        stats_grid.pack()
        
        total = len(self.user_tasks)
        pendientes = len([t for t in self.user_tasks if not t.esta_finalizada()])
        finalizadas = len([t for t in self.user_tasks if t.esta_finalizada()])
        
        # Calcular porcentaje de completitud
        porcentaje = round((finalizadas / total) * 100) if total > 0 else 0
        
        row = 0
        ttk.Label(stats_grid, text="Tareas asignadas:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(stats_grid, text=str(total)).grid(row=row, column=1, padx=10, pady=2)
        
        row += 1
        ttk.Label(stats_grid, text="Tareas completadas:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(stats_grid, text=str(finalizadas)).grid(row=row, column=1, padx=10, pady=2)
        
        row += 1
        ttk.Label(stats_grid, text="Tareas pendientes:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(stats_grid, text=str(pendientes)).grid(row=row, column=1, padx=10, pady=2)
        
        row += 1
        ttk.Label(stats_grid, text="Porcentaje de completitud:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(stats_grid, text=f"{porcentaje}%").grid(row=row, column=1, padx=10, pady=2)
        
        # Barra de progreso
        row += 1
        progress = ttk.Progressbar(stats_grid, length=200, mode='determinate')
        progress.grid(row=row, column=0, columnspan=2, pady=10)
        progress['value'] = porcentaje
        
    def _refresh_my_tasks(self):
        """Actualiza la lista de tareas del usuario.
        
        Recarga las tareas asignadas al usuario desde el gestor,
        aplica filtros seleccionados y actualiza la vista.
        """
        try:
            # Recargar tareas del usuario
            self.user_tasks = self.gestor.obtener_tareas_usuario(self.usuario.nombre)
            
            # Limpiar frame
            for widget in self.tasks_scroll_frame.scrollable_frame.winfo_children():
                widget.destroy()
                
            # Aplicar filtro
            filtro = self.task_filter_var.get()
            tareas_filtradas = self.user_tasks.copy()
            
            if filtro == "pendientes":
                tareas_filtradas = [t for t in tareas_filtradas if not t.esta_finalizada()]
            elif filtro == "finalizadas":
                tareas_filtradas = [t for t in tareas_filtradas if t.esta_finalizada()]
                
            # Mostrar tareas
            if not tareas_filtradas:
                ttk.Label(self.tasks_scroll_frame.scrollable_frame, 
                         text="No hay tareas que mostrar").pack(pady=20)
            else:
                for tarea in tareas_filtradas:
                    TaskCard(self.tasks_scroll_frame.scrollable_frame, tarea, 
                            self._view_task_details).pack(fill='x', pady=2)
                            
            # Actualizar resumen
            self._update_summary()
            
        except Exception as e:
            ttk.Label(self.tasks_scroll_frame.scrollable_frame, 
                     text=f"Error al cargar tareas: {e}").pack()
    
    def _update_summary(self):
        """Actualiza el resumen de tareas.
        
        Placeholder para actualización dinámica del resumen
        cuando cambian las tareas del usuario.
        """
        # Actualizar el contenido de la pestaña de perfil también
        pass
        
    def _view_task_details(self, tarea):
        """Muestra los detalles de una tarea.
        
        Args:
            tarea (Tarea): Tarea a mostrar en detalle.
            
        Note:
            Los usuarios regulares tienen acceso limitado comparado
            con los administradores.
        """
        # Los usuarios pueden ver detalles pero con funcionalidad limitada
        TaskDetailDialog(self.parent, self.gestor, tarea, self._refresh_my_tasks, 
                        readonly_mode=not self.usuario.es_admin(), current_user=self.usuario.nombre)
        
    def _change_password(self):
        """Cambia la contraseña del usuario.
        
        Abre el diálogo de cambio de contraseña para que el usuario
        pueda actualizar sus credenciales de acceso.
        """
        dialog = ChangePasswordDialog(self.parent, self.gestor, self.usuario.nombre)
        dialog.show()