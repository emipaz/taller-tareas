# Interfaz Gráfica - Sistema de Gestión de Tareas

Esta es la interfaz gráfica completa construida con tkinter para el sistema de gestión de tareas.

## Estructura de la UI

```
ui/
├── __init__.py          # Paquete principal
├── main_window.py       # Ventana principal y coordinador
├── login_window.py      # Ventana de autenticación
├── admin_panel.py       # Panel de administrador
├── user_panel.py        # Panel de usuario regular
├── dialogs.py          # Diálogos modales (tareas, usuarios, etc.)
└── ui_utils.py         # Widgets personalizados y utilidades
```

## Características

### 🔐 Autenticación
- Login seguro con validación de credenciales
- Creación de administrador inicial
- Establecimiento de contraseña inicial para usuarios nuevos
- Cambio de contraseña

### 👨‍💼 Panel de Administrador
- **Dashboard**: Estadísticas generales y tareas recientes
- **Gestión de Tareas**: 
  - Crear, editar y eliminar tareas
  - Asignar usuarios a tareas
  - Finalizar tareas
  - Ver detalles completos
  - Agregar comentarios
- **Gestión de Usuarios**:
  - Crear nuevos usuarios
  - Resetear contraseñas
  - Eliminar usuarios (excepto admins)
- **Reportes**: Estadísticas detalladas y reportes por usuario

### 👤 Panel de Usuario
- **Mis Tareas**: Ver tareas asignadas con filtros
- **Detalles de Tareas**: Ver información completa y agregar comentarios
- **Perfil**: Información personal y cambio de contraseña
- **Estadísticas**: Progreso personal y métricas de completitud

### 🎨 Interfaz
- Diseño moderno con pestañas organizadas
- Widgets personalizados (TaskCard, UserCard)
- Diálogos modales para acciones específicas
- Scrolling automático para listas largas
- Confirmaciones para acciones destructivas

## Uso

### Ejecutar la Aplicación
```bash
python app_tkinter.py
```

### Primer Uso
1. Al ejecutar por primera vez, se solicitará crear un administrador
2. Ingrese un nombre de usuario y contraseña
3. Una vez creado, puede hacer login como administrador

### Como Administrador
1. Haga login con sus credenciales
2. Acceda al panel de administración con múltiples pestañas:
   - **Dashboard**: Vista general del sistema
   - **Tareas**: Gestión completa de tareas
   - **Usuarios**: Administración de usuarios
   - **Reportes**: Estadísticas y análisis

### Como Usuario Regular
1. El administrador debe crear su cuenta
2. En el primer login, establezca su contraseña
3. Acceda a sus tareas asignadas y funcionalidades personales

## Widgets Personalizados

### TaskCard
Tarjeta visual que muestra información resumida de una tarea:
- Nombre y estado
- Fecha de creación
- Descripción (truncada)
- Usuarios asignados
- Número de comentarios

### UserCard
Tarjeta para mostrar información de usuarios:
- Nombre y rol
- Estado de contraseña
- Acciones disponibles

### ScrollableFrame
Frame con scroll vertical automático para contenido dinámico.

### ConfirmDialog
Diálogo de confirmación personalizado para acciones críticas.

## Diálogos Principales

### TaskDialog
- Crear nuevas tareas
- Asignar usuarios
- Editar descripción y detalles

### UserDialog
- Crear nuevos usuarios
- Gestionar usuarios existentes
- Resetear contraseñas y eliminar

### TaskDetailDialog
- Ver información completa de tareas
- Agregar comentarios
- Finalizar tareas (admin)
- Vista de solo lectura para usuarios

### ChangePasswordDialog
- Cambio seguro de contraseña
- Validación de contraseña actual
- Confirmación de nueva contraseña

## Funciones de Seguridad

- Validación de permisos por rol
- Confirmación para acciones destructivas
- Ocultación de funciones administrativas para usuarios regulares
- Manejo seguro de contraseñas (no se muestran en memoria)

## Manejo de Errores

- Validación de entrada en todos los formularios
- Mensajes de error descriptivos
- Recuperación automática de datos corruptos
- Logging de errores para debugging

## Personalización

La interfaz utiliza estilos TTK que pueden personalizarse:
- Colores y fuentes en `ui_utils.py`
- Tamaños de ventana configurables
- Temas adaptables

## Dependencias

- Python 3.6+
- tkinter (incluido con Python)
- Módulos del core (gestor_sistema, usuario, tarea)

## Notas de Desarrollo

- Arquitectura modular para fácil mantenimiento
- Separación clara entre lógica y presentación
- Widgets reutilizables
- Callbacks para comunicación entre componentes
- Gestión de memoria eficiente