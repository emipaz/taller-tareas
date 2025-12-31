"""Paquete de interfaz de usuario para el sistema de gestión de tareas.

Este paquete contiene todos los módulos relacionados con la interfaz gráfica
construida con tkinter.
"""

from .main_window import MainWindow
from .login_window import LoginWindow
from .admin_panel import AdminPanel
from .user_panel import UserPanel
from .dialogs import TaskDialog, UserDialog, TaskDetailDialog, ChangePasswordDialog
from .ui_utils import center_window, apply_theme, ScrollableFrame, TaskCard, UserCard, ConfirmDialog

__all__ = [
    'MainWindow', 'LoginWindow', 'AdminPanel', 'UserPanel',
    'TaskDialog', 'UserDialog', 'TaskDetailDialog', 'ChangePasswordDialog',
    'center_window', 'apply_theme', 'ScrollableFrame', 'TaskCard', 
    'UserCard', 'ConfirmDialog'
]