# API GraphQL para el Sistema de Gestión de Tareas

Esta carpeta contiene la implementación completa de la **API GraphQL** para el sistema de gestión de tareas.

## 🏗️ Arquitectura

```
api-graphql/
├── __init__.py              # Módulo API GraphQL
├── types.py                 # Tipos GraphQL con Strawberry
├── schema.py                # Schema principal (Query + Mutation)
├── resolvers.py             # Resolvers que conectan con core
├── auth.py                  # Autenticación y permisos JWT
├── server.py                # Servidor FastAPI + GraphQL
├── client.py                # Cliente Python para consumir API
├── test_graphql_examples.ipynb  # Notebook interactivo
└── tests/                   # Tests unitarios
    ├── test_graphql_api.py  # Tests principales
    └── run_all_tests.py     # Ejecutor de tests
```

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install strawberry-graphql[fastapi] uvicorn gql requests
```

### 2. Iniciar Servidor

```bash
# Desde la raíz del proyecto
python graphql_api.py

# O directamente
python -m api_graphql.server
```

El servidor estará disponible en:
- 📡 GraphQL API: http://localhost:4000/graphql
- 🎮 GraphQL Playground: http://localhost:4000/graphql (GET)
- 📚 Documentación: http://localhost:4000/docs

### 3. Usar Cliente Python

```python
from api_graphql.client import TaskGraphQLClient

client = TaskGraphQLClient()

# Autenticación
auth_data = client.login("admin", "admin123")

# Obtener dashboard
dashboard = client.get_dashboard()
print(dashboard)
```

### 4. Ejemplos Interactivos

```bash
# Abrir notebook con ejemplos completos
jupyter notebook api-graphql/test_graphql_examples.ipynb
```

## 📊 Funcionalidades

### Queries (Consultas)
- ✅ `usuarios` - Lista usuarios con filtros
- ✅ `usuario(id)` - Usuario específico
- ✅ `tareas` - Lista tareas con filtros
- ✅ `tarea(id)` - Tarea específica
- ✅ `estadisticas_generales` - Estadísticas del sistema
- ✅ `dashboard` - Datos completos del dashboard
- ✅ `health` - Health check

### Mutations (Modificaciones)
- ✅ `login` - Autenticación JWT
- ✅ `crear_usuario` - Crear usuario (admin)
- ✅ `crear_tarea` - Crear nueva tarea
- ✅ `actualizar_estado_tarea` - Cambiar estado
- ✅ `asignar_usuario_tarea` - Asignar usuarios

### Tipos GraphQL
- ✅ `Usuario` - Con tareas y estadísticas
- ✅ `Tarea` - Con usuarios asignados y comentarios
- ✅ `EstadisticasGenerales` - Métricas del sistema
- ✅ `DashboardData` - Vista completa del dashboard

## 🔐 Autenticación

La API utiliza **JWT (JSON Web Tokens)** para autenticación:

```python
# Login
mutation {
  login(input: {username: "admin", password: "admin123"}) {
    access_token
    refresh_token
    usuario {
      nombre
      rol
    }
  }
}
```

Luego usar el token en headers:
```
Authorization: Bearer <access_token>
```

## 🎯 Ejemplos de Uso

### Dashboard Completo (Una sola query)

```graphql
query Dashboard {
  dashboard {
    estadisticas {
      total_usuarios
      total_tareas
      tareas_pendientes
      tareas_completadas
      productividad_general
    }
    tareas_recientes {
      id
      nombre
      estado
      fecha_creacion
      usuarios_asignados {
        nombre
      }
    }
    usuarios_activos {
      id
      nombre
      rol
      estadisticas {
        tareas_asignadas
        productividad
      }
    }
  }
}
```

### Crear Tarea

```graphql
mutation CrearTarea($input: CrearTareaInput!) {
  crear_tarea(input: $input) {
    success
    message
    tarea {
      id
      nombre
      estado
      usuarios_asignados {
        nombre
      }
    }
  }
}
```

Variables:
```json
{
  "input": {
    "nombre": "Nueva tarea GraphQL",
    "descripcion": "Tarea creada desde GraphQL",
    "usuarios_ids": ["usuario1", "usuario2"]
  }
}
```

### Consulta con Filtros

```graphql
query TareasFiltradas($filtro: FiltroTareas) {
  tareas(filtro: $filtro) {
    id
    nombre
    estado
    fecha_creacion
    usuarios_asignados {
      nombre
      rol
    }
    duracion_dias
  }
}
```

Variables:
```json
{
  "filtro": {
    "estado": "PENDIENTE",
    "usuario_id": "admin",
    "limite": 10
  }
}
```

## 🔧 Tests

```bash
# Ejecutar todos los tests
python api-graphql/tests/run_all_tests.py

# O con pytest directamente
pytest api-graphql/tests/ -v
```

## 🚀 Ventajas sobre REST

### Una sola request para datos complejos

**REST** (múltiples requests):
```
GET /usuarios
GET /usuarios/1/tareas
GET /usuarios/2/tareas
GET /estadisticas
```

**GraphQL** (una sola request):
```graphql
query {
  usuarios {
    nombre
    tareas_asignadas { nombre estado }
  }
  estadisticas_generales { total_tareas }
}
```

### Control fino de datos

**REST** - Datos fijos:
```json
{
  "id": "1",
  "nombre": "Juan",
  "email": "juan@email.com",
  "telefono": "+1234567890",    // No necesario
  "direccion": "Calle 123",     // No necesario
  "fecha_nacimiento": "1990-01-01" // No necesario
}
```

**GraphQL** - Solo lo que necesitas:
```json
{
  "data": {
    "usuario": {
      "nombre": "Juan",
      "email": "juan@email.com"
    }
  }
}
```

## 🎮 GraphQL Playground

Visita http://localhost:4000/graphql en tu navegador para:

- 🔍 Explorar el schema interactivamente
- ✏️ Escribir y probar queries
- 📚 Ver documentación auto-generada
- 🔧 Debuggear queries complejas

## 🔄 Próximos Pasos

- 🔮 **Subscriptions**: Notificaciones en tiempo real
- ⚡ **DataLoader**: Optimización N+1 queries
- 📊 **Paginación**: Cursors y relay-style
- 🔒 **Rate limiting**: Control de velocidad
- 📈 **Monitoring**: Métricas y logging
- 🌐 **Federation**: Múltiples services GraphQL

## 📚 Recursos

- [Strawberry GraphQL](https://strawberry.rocks/) - Framework usado
- [GraphQL Spec](https://spec.graphql.org/) - Especificación oficial
- [GraphQL Playground](http://localhost:4000/graphql) - Herramienta interactiva
- [Notebook Examples](test_graphql_examples.ipynb) - Ejemplos paso a paso

---

⭐ **GraphQL + Python = 🚀 APIs poderosas y flexibles!**