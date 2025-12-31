"""Panel de administración del sistema de gestión de tareas.

Este módulo contiene la clase AdminPanel que proporciona una interfaz
completa para que los administradores gestionen usuarios, tareas,
y obtengan reportes del sistema.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from .ui_utils import ScrollableFrame, TaskCard, UserCard, ConfirmDialog
from .dialogs import TaskDialog, UserDialog, TaskDetailDialog


class AdminPanel:
    """Panel principal para usuarios administradores."""
    
    def __init__(self, parent: tk.Widget, gestor, usuario, logout_callback: Callable):
        """Inicializa el panel de administrador.
        
        Args:
            parent (tk.Widget): Widget padre donde se mostrará el panel.
            gestor (GestorSistema): Instancia del gestor del sistema.
            usuario (Usuario): Usuario administrador actual.
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
        """Carga los datos del sistema.
        
        Intenta cargar usuarios y tareas desde el gestor del sistema,
        mostrando errores si ocurren problemas durante la carga.
        """
        try:
            self.gestor.cargar_datos()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {e}")
        
    def _create_widgets(self):
        """Crea los widgets del panel.
        
        Construye la interfaz completa incluyendo header,
        notebook con pestañas y todas las secciones del panel.
        """
        # Header
        self._create_header()
        
        # Notebook con pestañas
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Pestañas
        self._create_dashboard_tab()
        self._create_tasks_tab()
        self._create_users_tab()
        self._create_reports_tab()
        
    def _create_header(self):
        """Crea el header del panel.
        
        Construye la barra superior con título, información del usuario
        y botón de cerrar sesión.
        """
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        # Título y usuario
        title_label = ttk.Label(header_frame, text="Panel de Administración", 
                               style='Title.TLabel')
        title_label.pack(side='left')
        
        # Frame derecho con info de usuario
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side='right')
        
        user_label = ttk.Label(right_frame, text=f"Usuario: {self.usuario.nombre} (Admin)")
        user_label.pack(side='left', padx=10)
        
        ttk.Button(right_frame, text="Cerrar Sesión", 
                  command=self.logout_callback).pack(side='left')
        
        # Separador
        ttk.Separator(self.parent, orient='horizontal').pack(fill='x', padx=10, pady=5)
        
    def _create_dashboard_tab(self):
        """Crea la pestaña de dashboard.
        
        Construye la vista principal con estadísticas del sistema,
        tareas recientes y acciones rápidas para administradores.
        """
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Frame principal con scroll
        main_frame = ScrollableFrame(dashboard_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        content = main_frame.scrollable_frame
        
        # Estadísticas
        stats_frame = ttk.LabelFrame(content, text="Estadísticas del Sistema", padding=15)
        stats_frame.pack(fill='x', pady=5)
        
        self._create_statistics_widgets(stats_frame)
        
        # Tareas recientes
        recent_frame = ttk.LabelFrame(content, text="Tareas Recientes", padding=15)
        recent_frame.pack(fill='both', expand=True, pady=5)
        
        self._create_recent_tasks_widgets(recent_frame)
        
        # Botones de acciones rápidas
        actions_frame = ttk.LabelFrame(content, text="Acciones Rápidas", padding=15)
        actions_frame.pack(fill='x', pady=5)
        
        btn_frame = ttk.Frame(actions_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Nueva Tarea", 
                  command=self._new_task).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Nuevo Usuario", 
                  command=self._new_user).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Actualizar Datos", 
                  command=self._refresh_data).pack(side='left', padx=5)
        
    def _create_tasks_tab(self):
        """Crea la pestaña de gestión de tareas.
        
        Construye la interfaz para administrar tareas incluyendo
        toolbar con acciones, filtros y lista de tareas.
        """
        tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(tasks_frame, text="Tareas")
        
        # Toolbar
        toolbar = ttk.Frame(tasks_frame)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(toolbar, text="Nueva Tarea", 
                  command=self._new_task).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Actualizar", 
                  command=self._refresh_tasks).pack(side='left', padx=5)
        
        # Filtros
        filter_frame = ttk.Frame(toolbar)
        filter_frame.pack(side='right')
        
        ttk.Label(filter_frame, text="Filtrar:").pack(side='left', padx=5)
        self.task_filter_var = tk.StringVar(value="todas")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.task_filter_var,
                                   values=["todas", "pendientes", "finalizadas"],
                                   state="readonly", width=12)
        filter_combo.pack(side='left', padx=5)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_tasks())
        
        # Lista de tareas con scroll
        self.tasks_scroll_frame = ScrollableFrame(tasks_frame)
        self.tasks_scroll_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self._refresh_tasks()
        
    def _create_users_tab(self):
        """Crea la pestaña de gestión de usuarios.
        
        Construye la interfaz para administrar usuarios incluyendo
        creación, edición y eliminación de cuentas.
        """
        users_frame = ttk.Frame(self.notebook)
        self.notebook.add(users_frame, text="Usuarios")
        
        # Toolbar
        toolbar = ttk.Frame(users_frame)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(toolbar, text="Nuevo Usuario", 
                  command=self._new_user).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Actualizar", 
                  command=self._refresh_users).pack(side='left', padx=5)
        
        # Lista de usuarios con scroll
        self.users_scroll_frame = ScrollableFrame(users_frame)
        self.users_scroll_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self._refresh_users()
        
    def _create_reports_tab(self):
        """Crea la pestaña de reportes.
        
        Construye la interfaz de reportes con estadísticas completas
        y análisis detallado del sistema.
        """
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reportes")
        
        # Frame con scroll para reportes
        reports_scroll = ScrollableFrame(reports_frame)
        reports_scroll.pack(fill='both', expand=True, padx=10, pady=10)
        
        content = reports_scroll.scrollable_frame
        
        # Reporte de estadísticas completas
        stats_frame = ttk.LabelFrame(content, text="Estadísticas Completas", padding=15)
        stats_frame.pack(fill='x', pady=5)
        
        self._create_detailed_statistics(stats_frame)
        
        # Reporte de tareas por usuario
        user_tasks_frame = ttk.LabelFrame(content, text="Tareas por Usuario", padding=15)
        user_tasks_frame.pack(fill='both', expand=True, pady=5)
        
        self._create_user_tasks_report(user_tasks_frame)
        
    def _create_statistics_widgets(self, parent: ttk.Frame):
        """Crea widgets de estadísticas básicas.
        
        Args:
            parent (ttk.Frame): Frame padre donde mostrar las estadísticas.
            
        Note:
            Muestra estadísticas de usuarios y tareas en formato de grid.
        """
        try:
            stats = self.gestor.obtener_estadisticas_sistema()
            
            # Grid de estadísticas
            stats_grid = ttk.Frame(parent)
            stats_grid.pack()
            
            row = 0
            # Estadísticas de usuarios
            if 'usuarios' in stats:
                user_stats = stats['usuarios']
                ttk.Label(stats_grid, text="Usuarios:", style='Header.TLabel').grid(
                    row=row, column=0, sticky='w', padx=5, pady=2)
                ttk.Label(stats_grid, text=f"Total: {user_stats.get('total', 0)}").grid(
                    row=row, column=1, padx=10, pady=2)
                ttk.Label(stats_grid, text=f"Admins: {user_stats.get('admins', 0)}").grid(
                    row=row, column=2, padx=10, pady=2)
                ttk.Label(stats_grid, text=f"Sin contraseña: {user_stats.get('sin_password', 0)}").grid(
                    row=row, column=3, padx=10, pady=2)
                row += 1
            
            # Estadísticas de tareas
            if 'tareas' in stats:
                task_stats = stats['tareas']
                ttk.Label(stats_grid, text="Tareas:", style='Header.TLabel').grid(
                    row=row, column=0, sticky='w', padx=5, pady=2)
                ttk.Label(stats_grid, text=f"Total: {task_stats.get('total', 0)}").grid(
                    row=row, column=1, padx=10, pady=2)
                ttk.Label(stats_grid, text=f"Pendientes: {task_stats.get('pendientes', 0)}").grid(
                    row=row, column=2, padx=10, pady=2)
                ttk.Label(stats_grid, text=f"Finalizadas: {task_stats.get('finalizadas', 0)}").grid(
                    row=row, column=3, padx=10, pady=2)
                    
        except Exception as e:
            ttk.Label(parent, text=f"Error al cargar estadísticas: {e}").pack()
            
    def _create_recent_tasks_widgets(self, parent: ttk.Frame):
        """Crea widgets para mostrar tareas recientes.
        
        Args:
            parent (ttk.Frame): Frame padre donde mostrar las tareas.
            
        Note:
            Muestra las 5 tareas más recientes como tarjetas interactivas.
        """
        try:
            tareas = self.gestor.cargar_tareas()
            # Mostrar las 5 tareas más recientes
            tareas_recientes = sorted(tareas, key=lambda t: t.fecha_creacion, reverse=True)[:5]
            
            if not tareas_recientes:
                ttk.Label(parent, text="No hay tareas registradas").pack()
                return
                
            for tarea in tareas_recientes:
                TaskCard(parent, tarea, self._view_task_details).pack(fill='x', pady=2)
                
        except Exception as e:
            ttk.Label(parent, text=f"Error al cargar tareas: {e}").pack()
            
    def _create_detailed_statistics(self, parent: ttk.Frame):
        """Crea estadísticas detalladas.
        
        Args:
            parent (ttk.Frame): Frame padre donde mostrar el reporte.
            
        Note:
            Genera un reporte textual completo en un widget Text
            con scroll para información detallada del sistema.
        """
        try:
            stats = self.gestor.obtener_estadisticas_sistema()
            
            # Crear texto con estadísticas
            text_widget = tk.Text(parent, height=10, width=80, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(parent, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Insertar estadísticas
            text_widget.insert('end', "=== ESTADÍSTICAS DETALLADAS DEL SISTEMA ===\n\n")
            
            if 'usuarios' in stats:
                user_stats = stats['usuarios']
                text_widget.insert('end', "USUARIOS:\n")
                text_widget.insert('end', f"  • Total de usuarios: {user_stats.get('total', 0)}\n")
                text_widget.insert('end', f"  • Administradores: {user_stats.get('admins', 0)}\n")
                text_widget.insert('end', f"  • Usuarios regulares: {user_stats.get('users', 0)}\n")
                text_widget.insert('end', f"  • Sin contraseña establecida: {user_stats.get('sin_password', 0)}\n\n")
            
            if 'tareas' in stats:
                task_stats = stats['tareas']
                text_widget.insert('end', "TAREAS:\n")
                text_widget.insert('end', f"  • Total de tareas: {task_stats.get('total', 0)}\n")
                text_widget.insert('end', f"  • Tareas pendientes: {task_stats.get('pendientes', 0)}\n")
                text_widget.insert('end', f"  • Tareas finalizadas: {task_stats.get('finalizadas', 0)}\n")
                text_widget.insert('end', f"  • Tareas sin asignar: {task_stats.get('sin_asignar', 0)}\n")
                
            text_widget.configure(state='disabled')
            
        except Exception as e:
            ttk.Label(parent, text=f"Error al generar reporte: {e}").pack()
            
    def _create_user_tasks_report(self, parent: ttk.Frame):
        """Crea reporte de tareas por usuario.
        
        Args:
            parent (ttk.Frame): Frame padre donde mostrar el reporte.
            
        Note:
            Utiliza un Treeview para mostrar estadísticas tabulares
            de tareas asignadas a cada usuario.
        """
        try:
            usuarios = self.gestor.cargar_usuarios()
            
            # Treeview para mostrar el reporte
            columns = ('Usuario', 'Rol', 'Total Tareas', 'Pendientes', 'Finalizadas')
            tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
            
            # Configurar columnas
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
                
            # Scrollbar
            scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Llenar datos
            for usuario in usuarios:
                tareas_usuario = self.gestor.obtener_tareas_usuario(usuario.nombre)
                total = len(tareas_usuario)
                pendientes = len([t for t in tareas_usuario if not t.esta_finalizada()])
                finalizadas = len([t for t in tareas_usuario if t.esta_finalizada()])
                
                tree.insert('', 'end', values=(
                    usuario.nombre, usuario.rol, total, pendientes, finalizadas))
                    
        except Exception as e:
            ttk.Label(parent, text=f"Error al generar reporte: {e}").pack()
    
    # Métodos de acciones
    
    def _refresh_data(self):
        """Actualiza todos los datos.
        
        Recarga datos del gestor y refresca todas las vistas
        del panel para mostrar información actualizada.
        """
        try:
            self._load_data()
            messagebox.showinfo("Éxito", "Datos actualizados correctamente")
            # Refrescar las pestañas visibles
            self._refresh_tasks()
            self._refresh_users()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar datos: {e}")
    
    def _refresh_tasks(self):
        """Actualiza la lista de tareas.
        
        Recarga las tareas desde el gestor, aplica filtros
        seleccionados y actualiza la vista de tarjetas.
        """
        try:
            # Limpiar frame
            for widget in self.tasks_scroll_frame.scrollable_frame.winfo_children():
                widget.destroy()
                
            # Obtener tareas
            tareas = self.gestor.cargar_tareas()
            
            # Aplicar filtro
            filtro = self.task_filter_var.get()
            if filtro == "pendientes":
                tareas = [t for t in tareas if not t.esta_finalizada()]
            elif filtro == "finalizadas":
                tareas = [t for t in tareas if t.esta_finalizada()]
                
            # Mostrar tareas
            if not tareas:
                ttk.Label(self.tasks_scroll_frame.scrollable_frame, 
                         text="No hay tareas que mostrar").pack(pady=20)
            else:
                for tarea in tareas:
                    TaskCard(self.tasks_scroll_frame.scrollable_frame, tarea, 
                            self._view_task_details).pack(fill='x', pady=2)
                            
        except Exception as e:
            ttk.Label(self.tasks_scroll_frame.scrollable_frame, 
                     text=f"Error al cargar tareas: {e}").pack()
    
    def _refresh_users(self):
        """Actualiza la lista de usuarios.
        
        Recarga los usuarios desde el gestor y actualiza
        la vista de tarjetas de usuarios.
        """
        try:
            # Limpiar frame
            for widget in self.users_scroll_frame.scrollable_frame.winfo_children():
                widget.destroy()
                
            # Obtener usuarios
            usuarios = self.gestor.cargar_usuarios()
            
            # Mostrar usuarios
            if not usuarios:
                ttk.Label(self.users_scroll_frame.scrollable_frame, 
                         text="No hay usuarios registrados").pack(pady=20)
            else:
                for usuario in usuarios:
                    UserCard(self.users_scroll_frame.scrollable_frame, usuario, 
                            self._manage_user).pack(fill='x', pady=2)
                            
        except Exception as e:
            ttk.Label(self.users_scroll_frame.scrollable_frame, 
                     text=f"Error al cargar usuarios: {e}").pack()
    
    def _new_task(self):
        """Crea una nueva tarea.
        
        Abre el diálogo de creación de tarea y actualiza
        la vista si se crea exitosamente.
        """
        dialog = TaskDialog(self.parent, self.gestor)
        if dialog.show():
            self._refresh_tasks()
            
    def _new_user(self):
        """Crea un nuevo usuario.
        
        Abre el diálogo de creación de usuario y actualiza
        la vista si se crea exitosamente.
        """
        dialog = UserDialog(self.parent, self.gestor)
        if dialog.show():
            self._refresh_users()
            
    def _view_task_details(self, tarea):
        """Muestra los detalles de una tarea.
        
        Args:
            tarea (Tarea): Tarea a mostrar en detalle.
            
        Note:
            Abre el diálogo de detalles con permisos completos de admin.
        """
        TaskDetailDialog(self.parent, self.gestor, tarea, self._refresh_tasks, 
                        readonly_mode=False, current_user=self.usuario.nombre)
        
    def _manage_user(self, usuario):
        """Gestiona un usuario (editar, eliminar, resetear password).
        
        Args:
            usuario (Usuario): Usuario a gestionar.
            
        Note:
            Abre el diálogo de gestión con opciones administrativas.
        """
        dialog = UserDialog(self.parent, self.gestor, usuario)
        if dialog.show():
            self._refresh_users()