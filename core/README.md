# 🏗️ Core del Sistema de Gestión de Tareas

El módulo `core` contiene la lógica de negocio principal del sistema de gestión de tareas. Este diseño modular permite que múltiples interfaces (consola, API REST, GUI, web) utilicen la misma lógica subyacente.

## 📁 Estructura

```
core/
├── __init__.py           # Módulo principal con exports
├── usuario.py           # Gestión de usuarios
├── tarea.py             # Gestión de tareas
├── gestor_sistema.py    # Coordinador principal
├── utils.py             # Utilidades y funciones auxiliares
└── tests/               # Tests unitarios del core
    ├── __init__.py
    ├── test_usuario.py
    └── test_tarea.py
```

## 🔧 Componentes Principales

### Usuario (`usuario.py`)
- Clase para gestión de usuarios del sistema
- Manejo de contraseñas con hash seguro
- Roles de usuario (admin/estándar)
- Validación de datos de usuario

### Tarea (`tarea.py`)
- Clase para gestión de tareas
- Estados de tarea (pendiente/finalizada)
- Sistema de comentarios
- Asignación de usuarios
- Timestamps automáticos

### GestorSistema (`gestor_sistema.py`)
- Coordinador principal del sistema
- API unificada para todas las operaciones
- Manejo de persistencia de datos
- Validación de reglas de negocio
- Gestión de archivos JSON y pickle

### Utilidades (`utils.py`)
- Funciones de persistencia (JSON/pickle)
- Generación de contraseñas aleatorias
- Estadísticas del sistema
- Validaciones comunes
- Funciones auxiliares

## 🚀 Uso del Módulo

### Instalación Local
```python
# Desde el directorio raíz del proyecto
from core import GestorSistema, Usuario, Tarea

# Crear instancia del gestor
gestor = GestorSistema()

# Usar las funcionalidades
exito, mensaje = gestor.crear_usuario("juan")
if exito:
    print(f"Usuario creado: {mensaje}")
```

### Ejemplo Completo
```python
from core import GestorSistema

def ejemplo_uso():
    # Inicializar el sistema
    gestor = GestorSistema()
    
    # Crear usuario administrador
    exito, msg = gestor.crear_usuario_admin("admin", "password123")
    print(f"Admin: {msg}")
    
    # Crear usuario estándar
    exito, msg = gestor.crear_usuario("juan")
    print(f"Usuario: {msg}")
    
    # Crear tarea
    exito, msg = gestor.crear_tarea("Desarrollo", "Desarrollar nueva funcionalidad")
    print(f"Tarea: {msg}")
    
    # Asignar usuario a tarea
    exito, msg = gestor.asignar_usuario_tarea("Desarrollo", "juan")
    print(f"Asignación: {msg}")
    
    # Obtener estadísticas
    stats = gestor.obtener_estadisticas_sistema()
    print(f"Estadísticas: {stats}")

if __name__ == "__main__":
    ejemplo_uso()
```

## 🧪 Tests

Para ejecutar los tests del módulo core:

```bash
# Desde el directorio raíz
python -m pytest core/tests/ -v

# Test específico
python -m pytest core/tests/test_usuario.py -v

# Con cobertura
python -m pytest core/tests/ --cov=core --cov-report=html
```

## 📊 Características

### ✅ Funcionalidades Implementadas
- ✅ Gestión completa de usuarios (CRUD)
- ✅ Sistema de roles (admin/usuario estándar)
- ✅ Gestión de contraseñas con hash seguro
- ✅ Gestión completa de tareas (CRUD)
- ✅ Sistema de comentarios en tareas
- ✅ Asignación de usuarios a tareas
- ✅ Persistencia de datos (JSON/pickle)
- ✅ Estadísticas del sistema
- ✅ Validaciones de integridad
- ✅ Tests unitarios completos

### 🔐 Seguridad
- Contraseñas hasheadas con bcrypt
- Validación de entrada de datos
- Separación de responsabilidades
- Manejo seguro de archivos

### 🏗️ Arquitectura
- Diseño modular y reutilizable
- Separación clara de responsabilidades
- API consistente y documentada
- Fácil extensión para nuevas interfaces

## 🔄 Interfaces Compatibles

Este módulo core está diseñado para ser utilizado por:

- **Consola Rich** (`main.py`) - ✅ Implementado
- **API REST FastAPI** (`api-rest/`) - ✅ Implementado  
- **GUI Tkinter** - 🟡 Planificado
- **Web Flask** - 🟡 Planificado

## 📝 Notas de Desarrollo

- Todas las funciones retornan tuplas `(bool, str)` para consistencia
- Los archivos de datos se almacenan en el directorio raíz
- Las validaciones siguen patrones consistentes
- La documentación sigue estándares de docstring Python

## 🤝 Contribución

Para agregar nuevas funcionalidades al core:

1. Implementar en el módulo correspondiente
2. Agregar tests unitarios
3. Actualizar documentación
4. Mantener compatibilidad con interfaces existentes