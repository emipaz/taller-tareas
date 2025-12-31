"""Diálogos modales para gestión de tareas y usuarios.

Este módulo contiene las clases de diálogos modales utilizados
para crear, editar y gestionar tareas y usuarios en el sistema.
Incluyendo diálogos de detalles, creación y cambio de contraseñas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from .ui_utils import center_window, ScrollableFrame, ConfirmDialog


class TaskDialog:
    """Diálogo para crear/editar tareas."""
    
    def __init__(self, parent: tk.Widget, gestor, tarea=None):
        """Inicializa el diálogo de tarea.
        
        Args:
            parent (tk.Widget): Widget padre del diálogo.
            gestor (GestorSistema): Instancia del gestor del sistema.
            tarea (Tarea, optional): Tarea a editar. None para crear nueva.
        """
        self.parent = parent
        self.gestor = gestor
        self.tarea = tarea
        self.result = False
        
        self.dialog = None
        
    def show(self) -> bool:
        """Muestra el diálogo.
        
        Returns:
            bool: True si se guardó la tarea, False si se canceló.
            
        Note:
            Bloquea la ejecución hasta que el usuario cierre el diálogo.
        """
        self.dialog = tk.Toplevel(self.parent)
        title = "Editar Tarea" if self.tarea else "Nueva Tarea"
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        
        center_window(self.dialog, 500, 400)
        
        self._create_widgets()
        self._load_data()
        
        self.dialog.wait_window()
        return self.result
        
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title = "Editar Tarea" if self.tarea else "Nueva Tarea"
        ttk.Label(main_frame, text=title, style='Header.TLabel').pack(pady=(0, 15))
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='both', expand=True)
        
        # Nombre
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, pady=5, padx=(10, 0), columnspan=2)
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=1, column=0, sticky='nw', pady=5)
        self.desc_text = tk.Text(form_frame, height=8, width=40, wrap=tk.WORD)
        self.desc_text.grid(row=1, column=1, pady=5, padx=(10, 0), columnspan=2)
        
        # Scrollbar para descripción
        desc_scroll = ttk.Scrollbar(form_frame, orient="vertical", command=self.desc_text.yview)
        desc_scroll.grid(row=1, column=3, sticky='ns', pady=5)
        self.desc_text.configure(yscrollcommand=desc_scroll.set)
        
        # Usuarios disponibles (solo para admin)
        ttk.Label(form_frame, text="Usuarios:").grid(row=2, column=0, sticky='nw', pady=5)
        
        users_frame = ttk.Frame(form_frame)
        users_frame.grid(row=2, column=1, pady=5, padx=(10, 0), columnspan=2, sticky='w')
        
        # Lista de usuarios con checkboxes
        self.user_vars = {}
        self._create_user_checkboxes(users_frame)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="Guardar", command=self._save_task).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy).pack(side='left', padx=5)
        
    def _create_user_checkboxes(self, parent: ttk.Frame):
        """Crea checkboxes para seleccionar usuarios.
        
        Args:
            parent (ttk.Frame): Frame padre para los checkboxes.
            
        Note:
            Crea una lista scrollable de usuarios disponibles
            excluyendo administradores.
        """
        try:
            usuarios = self.gestor.cargar_usuarios()
            
            if not usuarios:
                ttk.Label(parent, text="No hay usuarios disponibles").pack()
                return
                
            # Frame con scroll para usuarios
            canvas = tk.Canvas(parent, height=100, width=300)
            scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Crear checkboxes
            for i, usuario in enumerate(usuarios):
                if not usuario.es_admin():  # No mostrar admins en la lista
                    var = tk.BooleanVar()
                    self.user_vars[usuario.nombre] = var
                    
                    cb = ttk.Checkbutton(scrollable_frame, text=usuario.nombre, 
                                        variable=var)
                    cb.grid(row=i, column=0, sticky='w', pady=2)
                    
        except Exception as e:
            ttk.Label(parent, text=f"Error al cargar usuarios: {e}").pack()
            
    def _load_data(self):
        """Carga datos de la tarea si está editando.
        
        Rellena los campos del formulario con los datos de la tarea
        existente cuando se está en modo de edición.
        """
        if self.tarea:
            self.name_var.set(self.tarea.nombre)
            self.desc_text.insert('1.0', self.tarea.descripcion)
            
            # Marcar usuarios asignados
            for usuario_nombre in self.tarea.usuarios_asignados:
                if usuario_nombre in self.user_vars:
                    self.user_vars[usuario_nombre].set(True)
                    
    def _save_task(self):
        """Guarda la tarea.
        
        Valida los datos ingresados, crea o edita la tarea
        y asigna los usuarios seleccionados.
        
        Note:
            La edición de tareas existentes requiere implementación
            adicional en el gestor del sistema.
        """
        nombre = self.name_var.get().strip()
        descripcion = self.desc_text.get('1.0', 'end-1c').strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
            
        if not descripcion:
            messagebox.showerror("Error", "La descripción es obligatoria")
            return
            
        try:
            if self.tarea:
                # Editar tarea existente (esto requeriría métodos adicionales en el gestor)
                messagebox.showinfo("Info", "Función de edición no implementada aún")
            else:
                # Crear nueva tarea
                exito, mensaje = self.gestor.crear_tarea(nombre, descripcion)
                
                if exito:
                    # Asignar usuarios seleccionados
                    for usuario_nombre, var in self.user_vars.items():
                        if var.get():
                            self.gestor.asignar_usuario_tarea(nombre, usuario_nombre)
                    
                    messagebox.showinfo("Éxito", mensaje)
                    self.result = True
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", mensaje)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar tarea: {e}")


class UserDialog:
    """Diálogo para crear/gestionar usuarios."""
    
    def __init__(self, parent: tk.Widget, gestor, usuario=None):
        """Inicializa el diálogo de usuario.
        
        Args:
            parent (tk.Widget): Widget padre del diálogo.
            gestor (GestorSistema): Instancia del gestor del sistema.
            usuario (Usuario, optional): Usuario a gestionar. None para crear nuevo.
        """
        self.parent = parent
        self.gestor = gestor
        self.usuario = usuario
        self.result = False
        
        self.dialog = None
        
    def show(self) -> bool:
        """Muestra el diálogo.
        
        Returns:
            bool: True si se guardó/modificó, False si se canceló.
            
        Note:
            El tamaño del diálogo varía según si es creación o gestión.
        """
        self.dialog = tk.Toplevel(self.parent)
        title = "Gestionar Usuario" if self.usuario else "Nuevo Usuario"
        self.dialog.title(title)
        
        size = "400x300" if self.usuario else "350x150"
        self.dialog.geometry(size)
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        
        center_window(self.dialog, 400 if self.usuario else 350, 300 if self.usuario else 150)
        
        self._create_widgets()
        
        self.dialog.wait_window()
        return self.result
        
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        if self.usuario:
            self._create_manage_widgets(main_frame)
        else:
            self._create_new_user_widgets(main_frame)
            
    def _create_new_user_widgets(self, parent: ttk.Frame):
        """Crea widgets para nuevo usuario.
        
        Args:
            parent (ttk.Frame): Frame padre para los widgets.
            
        Note:
            Interfaz simplificada con solo campo de nombre
            para creación de usuarios.
        """
        ttk.Label(parent, text="Nuevo Usuario", style='Header.TLabel').pack(pady=(0, 15))
        
        # Nombre
        name_frame = ttk.Frame(parent)
        name_frame.pack(fill='x', pady=5)
        ttk.Label(name_frame, text="Nombre:").pack(side='left')
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var, width=25).pack(side='right')
        
        # Botones
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="Crear", command=self._create_user).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy).pack(side='left', padx=5)
        
    def _create_manage_widgets(self, parent: ttk.Frame):
        """Crea widgets para gestionar usuario existente.
        
        Args:
            parent (ttk.Frame): Frame padre para los widgets.
            
        Note:
            Interfaz completa con información del usuario y
            opciones de gestión administrativa.
        """
        ttk.Label(parent, text=f"Gestionar Usuario: {self.usuario.nombre}", 
                 style='Header.TLabel').pack(pady=(0, 15))
        
        # Información
        info_frame = ttk.LabelFrame(parent, text="Información", padding=10)
        info_frame.pack(fill='x', pady=5)
        
        info_grid = ttk.Frame(info_frame)
        info_grid.pack()
        
        ttk.Label(info_grid, text="Nombre:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(info_grid, text=self.usuario.nombre).grid(row=0, column=1, sticky='w', padx=15, pady=2)
        
        ttk.Label(info_grid, text="Rol:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(info_grid, text=self.usuario.rol).grid(row=1, column=1, sticky='w', padx=15, pady=2)
        
        password_status = "Establecida" if self.usuario.tiene_password() else "No establecida"
        ttk.Label(info_grid, text="Contraseña:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(info_grid, text=password_status).grid(row=2, column=1, sticky='w', padx=15, pady=2)
        
        # Acciones
        actions_frame = ttk.LabelFrame(parent, text="Acciones", padding=10)
        actions_frame.pack(fill='x', pady=5)
        
        if not self.usuario.es_admin():
            ttk.Button(actions_frame, text="Resetear Contraseña", 
                      command=self._reset_password).pack(fill='x', pady=2)
            ttk.Button(actions_frame, text="Eliminar Usuario", 
                      command=self._delete_user).pack(fill='x', pady=2)
        else:
            ttk.Label(actions_frame, text="Los administradores no pueden ser gestionados").pack()
            
        # Cerrar
        ttk.Button(parent, text="Cerrar", command=self.dialog.destroy).pack(pady=10)
        
    def _create_user(self):
        """Crea un nuevo usuario.
        
        Valida el nombre ingresado y crea el usuario en el sistema
        usando el gestor.
        """
        nombre = self.name_var.get().strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
            
        try:
            exito, mensaje = self.gestor.crear_usuario(nombre)
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", mensaje)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear usuario: {e}")
            
    def _reset_password(self):
        """Resetea la contraseña del usuario.
        
        Solicita confirmación y resetea la contraseña del usuario
        usando credenciales de administrador.
        """
        confirm = ConfirmDialog(self.dialog, "Confirmar", 
                               f"¿Está seguro que desea resetear la contraseña de {self.usuario.nombre}?")
        
        if confirm.show():
            try:
                # Obtener un admin para hacer la operación
                usuarios = self.gestor.cargar_usuarios()
                admin = next((u for u in usuarios if u.es_admin()), None)
                
                if admin:
                    exito, mensaje = self.gestor.resetear_password_usuario(admin.nombre, self.usuario.nombre)
                    
                    if exito:
                        messagebox.showinfo("Éxito", mensaje)
                        self.result = True
                    else:
                        messagebox.showerror("Error", mensaje)
                else:
                    messagebox.showerror("Error", "No se encontró un administrador")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al resetear contraseña: {e}")
                
    def _delete_user(self):
        """Elimina el usuario.
        
        Solicita confirmación y elimina permanentemente
        el usuario del sistema.
        
        Warning:
            Esta acción no se puede deshacer.
        """
        confirm = ConfirmDialog(self.dialog, "Confirmar", 
                               f"¿Está seguro que desea eliminar el usuario {self.usuario.nombre}?")
        
        if confirm.show():
            try:
                exito, mensaje = self.gestor.eliminar_usuario(self.usuario.nombre)
                
                if exito:
                    messagebox.showinfo("Éxito", mensaje)
                    self.result = True
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", mensaje)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar usuario: {e}")


class TaskDetailDialog:
    """Diálogo para ver/editar detalles de una tarea."""
    
    def __init__(self, parent: tk.Widget, gestor, tarea, refresh_callback=None, readonly_mode=False, current_user=None):
        """Inicializa el diálogo de detalles de tarea.
        
        Args:
            parent (tk.Widget): Widget padre del diálogo.
            gestor (GestorSistema): Instancia del gestor del sistema.
            tarea (Tarea): Tarea a mostrar en detalle.
            refresh_callback (Callable, optional): Callback para refrescar vista padre.
            readonly_mode (bool): Si True, solo permite lectura.
            current_user (str, optional): Usuario actual para comentarios.
        """
        self.parent = parent
        self.gestor = gestor
        self.tarea = tarea
        self.refresh_callback = refresh_callback
        self.readonly_mode = readonly_mode
        self.current_user = current_user or "usuario_actual"
        
        self._show_dialog()
        
    def _show_dialog(self):
        """Muestra el diálogo.
        
        Configura y muestra la ventana modal con los detalles
        completos de la tarea.
        """
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Tarea: {self.tarea.nombre}")
        self.dialog.geometry("600x500")
        self.dialog.grab_set()
        
        center_window(self.dialog, 600, 500)
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        # Frame principal con scroll
        main_frame = ScrollableFrame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        content = main_frame.scrollable_frame
        
        # Información básica
        self._create_basic_info(content)
        
        # Usuarios asignados
        self._create_assigned_users(content)
        
        # Comentarios
        self._create_comments_section(content)
        
        # Acciones
        self._create_actions_section(content)
        
    def _create_basic_info(self, parent: ttk.Frame):
        """Crea la sección de información básica.
        
        Args:
            parent (ttk.Frame): Frame padre para la sección.
            
        Note:
            Muestra nombre, estado, fecha de creación y descripción
            de la tarea en formato de solo lectura.
        """
        info_frame = ttk.LabelFrame(parent, text="Información de la Tarea", padding=15)
        info_frame.pack(fill='x', pady=5)
        
        # Nombre
        ttk.Label(info_frame, text="Nombre:", style='Header.TLabel').grid(
            row=0, column=0, sticky='w', pady=2)
        ttk.Label(info_frame, text=self.tarea.nombre).grid(
            row=0, column=1, sticky='w', padx=15, pady=2)
        
        # Estado
        ttk.Label(info_frame, text="Estado:", style='Header.TLabel').grid(
            row=1, column=0, sticky='w', pady=2)
        estado_text = self.tarea.estado.title()
        if self.tarea.esta_finalizada():
            estado_text += " ✓"
        ttk.Label(info_frame, text=estado_text).grid(
            row=1, column=1, sticky='w', padx=15, pady=2)
        
        # Fecha de creación
        ttk.Label(info_frame, text="Creada:", style='Header.TLabel').grid(
            row=2, column=0, sticky='w', pady=2)
        ttk.Label(info_frame, text=self.tarea.fecha_creacion).grid(
            row=2, column=1, sticky='w', padx=15, pady=2)
        
        # Descripción
        ttk.Label(info_frame, text="Descripción:", style='Header.TLabel').grid(
            row=3, column=0, sticky='nw', pady=2)
        
        desc_text = tk.Text(info_frame, height=4, width=50, wrap=tk.WORD,
                           state='disabled')
        desc_text.grid(row=3, column=1, padx=15, pady=2, sticky='ew')
        
        desc_text.configure(state='normal')
        desc_text.insert('1.0', self.tarea.descripcion)
        desc_text.configure(state='disabled')
        
    def _create_assigned_users(self, parent: ttk.Frame):
        """Crea la sección de usuarios asignados.
        
        Args:
            parent (ttk.Frame): Frame padre para la sección.
            
        Note:
            Lista todos los usuarios asignados a la tarea
            o muestra mensaje si no hay ninguno.
        """
        users_frame = ttk.LabelFrame(parent, text="Usuarios Asignados", padding=15)
        users_frame.pack(fill='x', pady=5)
        
        if not self.tarea.usuarios_asignados:
            ttk.Label(users_frame, text="No hay usuarios asignados").pack()
        else:
            for i, usuario in enumerate(self.tarea.usuarios_asignados):
                user_label = ttk.Label(users_frame, text=f"• {usuario}")
                user_label.grid(row=i, column=0, sticky='w', pady=2)
                
    def _create_comments_section(self, parent: ttk.Frame):
        """Crea la sección de comentarios.
        
        Args:
            parent (ttk.Frame): Frame padre para la sección.
            
        Note:
            Muestra todos los comentarios existentes y proporciona
            interfaz para agregar nuevos (si no es modo readonly).
        """
        comments_frame = ttk.LabelFrame(parent, text=f"Comentarios ({len(self.tarea.comentarios)})", 
                                       padding=15)
        comments_frame.pack(fill='both', expand=True, pady=5)
        
        # Lista de comentarios
        if not self.tarea.comentarios:
            ttk.Label(comments_frame, text="No hay comentarios").pack()
        else:
            # Frame con scroll para comentarios
            comments_scroll = ScrollableFrame(comments_frame)
            comments_scroll.pack(fill='both', expand=True)
            
            for i, (comentario, usuario, fecha) in enumerate(self.tarea.comentarios):
                comment_frame = ttk.Frame(comments_scroll.scrollable_frame, relief='ridge', 
                                        borderwidth=1, padding=10)
                comment_frame.pack(fill='x', pady=2)
                
                # Header del comentario
                header = f"{usuario} - {fecha}"
                ttk.Label(comment_frame, text=header, style='Header.TLabel').pack(anchor='w')
                
                # Contenido del comentario
                ttk.Label(comment_frame, text=comentario, wraplength=500).pack(anchor='w', pady=(5, 0))
        
        # Nuevo comentario (si no es readonly)
        if not self.readonly_mode:
            new_comment_frame = ttk.Frame(comments_frame)
            new_comment_frame.pack(fill='x', pady=(10, 0))
            
            ttk.Label(new_comment_frame, text="Nuevo comentario:").pack(anchor='w')
            self.comment_text = tk.Text(new_comment_frame, height=3, wrap=tk.WORD)
            self.comment_text.pack(fill='x', pady=2)
            
            ttk.Button(new_comment_frame, text="Agregar Comentario", 
                      command=self._add_comment).pack(anchor='e', pady=2)
                      
    def _create_actions_section(self, parent: ttk.Frame):
        """Crea la sección de acciones.
        
        Args:
            parent (ttk.Frame): Frame padre para la sección.
            
        Note:
            Proporciona botones de acción disponibles según
            permisos del usuario y estado de la tarea.
        """
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(fill='x', pady=10)
        
        # Botones de acción (solo para admin)
        if not self.readonly_mode:
            if not self.tarea.esta_finalizada():
                ttk.Button(actions_frame, text="Finalizar Tarea", 
                          command=self._finalize_task).pack(side='left', padx=5)
            
        # Botón cerrar
        ttk.Button(actions_frame, text="Cerrar", 
                  command=self.dialog.destroy).pack(side='right', padx=5)
                  
    def _add_comment(self):
        """Agrega un comentario a la tarea.
        
        Valida el contenido del comentario, lo agrega a la tarea
        y actualiza la vista para mostrar el nuevo comentario.
        
        Note:
            Recrea el diálogo para mostrar la información actualizada.
        """
        comentario = self.comment_text.get('1.0', 'end-1c').strip()
        
        if not comentario:
            messagebox.showerror("Error", "El comentario no puede estar vacío")
            return
            
        try:
            exito, mensaje = self.gestor.agregar_comentario_tarea(
                self.tarea.nombre, comentario, self.current_user)
            
            if exito:
                messagebox.showinfo("Éxito", "Comentario agregado")
                self.comment_text.delete('1.0', 'end')
                
                # Refrescar la vista
                if self.refresh_callback:
                    self.refresh_callback()
                    
                # Recrear el diálogo para mostrar el nuevo comentario
                self.dialog.destroy()
                # Recargar tarea actualizada
                tareas = self.gestor.cargar_tareas()
                tarea_actualizada = next((t for t in tareas if t.nombre == self.tarea.nombre), None)
                if tarea_actualizada:
                    TaskDetailDialog(self.parent, self.gestor, tarea_actualizada, 
                                   self.refresh_callback, self.readonly_mode, self.current_user)
            else:
                messagebox.showerror("Error", mensaje)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar comentario: {e}")
            
    def _finalize_task(self):
        """Finaliza la tarea.
        
        Solicita confirmación y marca la tarea como finalizada
        en el sistema.
        
        Warning:
            Una vez finalizada, la tarea no puede volver a estado pendiente.
        """
        confirm = ConfirmDialog(self.dialog, "Confirmar", 
                               f"¿Está seguro que desea finalizar la tarea '{self.tarea.nombre}'?")
        
        if confirm.show():
            try:
                exito, mensaje = self.gestor.finalizar_tarea(self.tarea.nombre)
                
                if exito:
                    messagebox.showinfo("Éxito", mensaje)
                    
                    if self.refresh_callback:
                        self.refresh_callback()
                        
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", mensaje)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al finalizar tarea: {e}")


class ChangePasswordDialog:
    """Diálogo para cambiar contraseña."""
    
    def __init__(self, parent: tk.Widget, gestor, username: str):
        """Inicializa el diálogo de cambio de contraseña.
        
        Args:
            parent (tk.Widget): Widget padre del diálogo.
            gestor (GestorSistema): Instancia del gestor del sistema.
            username (str): Nombre del usuario que cambiará contraseña.
        """
        self.parent = parent
        self.gestor = gestor
        self.username = username
        
        self.dialog = None
        
    def show(self):
        """Muestra el diálogo.
        
        Presenta la interfaz modal para cambio de contraseña
        con validación de contraseña actual.
        """
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Cambiar Contraseña")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        
        center_window(self.dialog, 350, 200)
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Cambiar Contraseña", style='Header.TLabel').pack(pady=(0, 15))
        
        # Contraseña actual
        current_frame = ttk.Frame(main_frame)
        current_frame.pack(fill='x', pady=5)
        ttk.Label(current_frame, text="Actual:").pack(side='left')
        self.current_var = tk.StringVar()
        ttk.Entry(current_frame, textvariable=self.current_var, show='*').pack(side='right')
        
        # Nueva contraseña
        new_frame = ttk.Frame(main_frame)
        new_frame.pack(fill='x', pady=5)
        ttk.Label(new_frame, text="Nueva:").pack(side='left')
        self.new_var = tk.StringVar()
        ttk.Entry(new_frame, textvariable=self.new_var, show='*').pack(side='right')
        
        # Confirmar nueva
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.pack(fill='x', pady=5)
        ttk.Label(confirm_frame, text="Confirmar:").pack(side='left')
        self.confirm_var = tk.StringVar()
        ttk.Entry(confirm_frame, textvariable=self.confirm_var, show='*').pack(side='right')
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="Cambiar", command=self._change_password).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy).pack(side='left', padx=5)
        
    def _change_password(self):
        """Cambia la contraseña."""
        current = self.current_var.get()
        new_pass = self.new_var.get()
        confirm = self.confirm_var.get()
        
        if not current or not new_pass:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
            
        if new_pass != confirm:
            messagebox.showerror("Error", "Las contraseñas nuevas no coinciden")
            return
            
        if len(new_pass) < 4:
            messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres")
            return
            
        try:
            exito, mensaje = self.gestor.cambiar_password(self.username, current, new_pass)
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", mensaje)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar contraseña: {e}")