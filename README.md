"# 🚀 Sistema de Gestión de Tareas

Sistema completo de gestión de tareas con múltiples interfaces: consola Rich, API REST FastAPI, y arquitectura modular para futuras expansiones (GUI Tkinter, Web Flask).

## 🏗️ Arquitectura del Proyecto

```
📁 Sistema de Gestión de Tareas/
├── 🏗️ core/                    # Módulo principal del sistema
│   ├── __init__.py             # Exports del módulo core
│   ├── usuario.py              # Gestión de usuarios
│   ├── tarea.py                # Gestión de tareas
│   ├── gestor_sistema.py       # Coordinador principal
│   ├── utils.py                # Utilidades y persistencia
│   ├── README.md               # Documentación del core
│   └── tests/                  # Tests unitarios del core
│       ├── test_usuario.py
│       └── test_tarea.py
├── 🌐 api-rest/                # API REST con FastAPI
│   ├── __init__.py
│   ├── api_rest.py             # Aplicación FastAPI
│   ├── api_models.py           # Modelos Pydantic
│   ├── jwt_auth.py             # Autenticación JWT
│   ├── test_api_client.py      # Cliente Python para tests
│   ├── test_api_endpoints.ipynb # Notebook de pruebas
│   ├── README.md               # Documentación de la API
│   └── tests/                  # Tests de la API
│       └── test_app.py
├── 📱 main.py                  # Interfaz de consola con Rich
├── 🔗 api.py                   # Punto de entrada API REST
├── 📋 requirements.txt         # Dependencias
├── 📄 tareas_finalizadas.json  # Datos persistidos
└── 📖 README.md                # Este archivo
```

## 🚀 Interfaces Disponibles

### 💻 Consola Rich (`main.py`)
Interfaz de línea de comandos con Rich para una experiencia visual mejorada.

```bash
python main.py
```

**Características:**
- ✅ Interfaz colorida y atractiva
- ✅ Tablas formateadas para datos
- ✅ Menús interactivos
- ✅ Validación de entrada
- ✅ Mensajes con iconos y colores

### 🌐 API REST (`api.py`)
API REST completa con FastAPI, autenticación JWT y documentación automática.

```bash
python api.py
```

**Acceso:**
- 📊 Swagger UI: http://localhost:8000/docs
- 📚 ReDoc: http://localhost:8000/redoc
- 🔍 Health Check: http://localhost:8000/health

**Características:**
- ✅ Autenticación JWT segura
- ✅ Documentación interactiva
- ✅ Validación automática de datos
- ✅ CORS configurado
- ✅ Tests automatizados

### 🖥️ GUI Tkinter (Planificado)
Interfaz gráfica de escritorio multiplataforma.

### 🌍 Web Flask (Planificado)
Interfaz web completa con templates y formularios.

## 🏗️ Módulo Core

El diseño modular permite que todas las interfaces utilicen la misma lógica de negocio:

```python
from core import GestorSistema

gestor = GestorSistema()
exito, mensaje = gestor.crear_usuario("juan")
```

**Componentes del Core:**
- `Usuario`: Gestión de usuarios con roles
- `Tarea`: Gestión de tareas y estados  
- `GestorSistema`: API unificada del sistema
- `utils`: Utilidades y persistencia

## 🔐 Sistema de Autenticación

### Consola
- Autenticación por usuario/contraseña
- Sesión persistente durante la ejecución
- Roles de admin y usuario estándar

### API REST
- Autenticación JWT con tokens seguros
- Access tokens (30 min) + Refresh tokens (7 días)
- Headers de autorización estándar
- Logout para invalidar tokens

## 📊 Funcionalidades

### 👥 Gestión de Usuarios
- ✅ Crear usuarios estándar y administradores
- ✅ Sistema de contraseñas con hash seguro
- ✅ Roles diferenciados (admin/usuario)
- ✅ CRUD completo de usuarios

### 📝 Gestión de Tareas
- ✅ Crear y gestionar tareas
- ✅ Asignar usuarios a tareas
- ✅ Estados (pendiente/finalizada)
- ✅ Sistema de comentarios
- ✅ Timestamps automáticos

### 📊 Reportes y Estadísticas
- ✅ Estadísticas del sistema
- ✅ Tareas por usuario
- ✅ Estados de tareas
- ✅ Métricas de productividad

### 💾 Persistencia
- ✅ Almacenamiento en archivos JSON
- ✅ Backup automático en pickle
- ✅ Carga automática al iniciar

## 🛠️ Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- pip (gestor de paquetes de Python)

### Instalación

```bash
# Clonar o descargar el proyecto
git clone <repository-url>
cd sistema-gestion-tareas

# Instalar dependencias
pip install -r requirements.txt
```

### Dependencias Principales

```
# Interfaz de consola
rich>=13.0.0
getpass (incluido en Python)

# API REST
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
pyjwt>=2.8.0
cryptography>=41.0.0
passlib>=1.7.4
bcrypt>=4.0.0

# Testing
pytest>=7.4.0
requests>=2.31.0
```

## 🚀 Uso Rápido

### 1. Interfaz de Consola

```bash
python main.py
```

- Crear el primer usuario administrador
- Navegar por los menús interactivos
- Gestionar usuarios y tareas

### 2. API REST

```bash
# Iniciar servidor
python api.py

# En otra terminal, probar endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Ver documentación
```

### 3. Cliente Python de la API

```python
from api_rest.test_api_client import TaskAPIClient

client = TaskAPIClient()
result = client.health_check()
print(result)
```

### 4. Tests Interactivos (Jupyter)

```bash
# Abrir notebook
jupyter notebook api-rest/test_api_endpoints.ipynb
```

## 🧪 Testing

### Tests del Core
```bash
python -m pytest core/tests/ -v
```

### Tests de la API
```bash
python -m pytest api-rest/tests/ -v
```

### Cliente de Pruebas Interactivo
```bash
python api-rest/test_api_client.py
```

## 📁 Estructura de Datos

### Archivos Generados
- `usuarios.pkl` - Usuarios del sistema (pickle)
- `tareas.pkl` - Tareas (pickle)  
- `tareas_finalizadas.json` - Backup en JSON
- `jwt_private_key.pem` - Clave privada JWT
- `jwt_public_key.pem` - Clave pública JWT

### Formato de Datos

```json
// tareas_finalizadas.json
{
    "nombre_tarea": {
        "nombre": "Desarrollo API",
        "descripcion": "Implementar API REST",
        "fecha_creacion": "2023-11-23 10:30:00",
        "fecha_finalizacion": "2023-11-23 15:45:00",
        "usuarios_asignados": ["juan", "maria"],
        "comentarios": [...]
    }
}
```

## 🔄 Roadmap

### ✅ Completado
- ✅ Módulo core con lógica de negocio
- ✅ Interfaz de consola con Rich
- ✅ API REST con FastAPI + JWT
- ✅ Tests unitarios y de integración
- ✅ Documentación completa

### 🟡 En Desarrollo
- 🟡 GUI con Tkinter
- 🟡 Interfaz web con Flask
- 🟡 Mejoras de seguridad
- 🟡 Métricas avanzadas

### 🔮 Futuro
- 🔮 Base de datos PostgreSQL
- 🔮 Notificaciones en tiempo real
- 🔮 API GraphQL
- 🔮 Aplicación móvil
- 🔮 Dashboard analítico

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

Sistema de Gestión de Tareas - Proyecto de demostración de arquitectura modular en Python.

## 🆘 Soporte

Para soporte y preguntas:

1. Consultar documentación en cada módulo
2. Revisar tests para ejemplos de uso
3. Usar la documentación interactiva de la API
4. Crear issue en el repositorio

---

⭐ **¡Si este proyecto te resulta útil, considera darle una estrella!**" 
