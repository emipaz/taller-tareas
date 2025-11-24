# 🚀 Guía Completa de GraphQL

## Introducción a GraphQL

GraphQL es un lenguaje de consulta para APIs y un runtime para ejecutar esas consultas usando un sistema de tipos que defines para tus datos. Desarrollado por Facebook en 2012 y liberado como código abierto en 2015.

### ¿Qué es GraphQL?

GraphQL es:
- **Un lenguaje de consulta**: Permite a los clientes solicitar exactamente los datos que necesitan
- **Un runtime del servidor**: Ejecuta consultas contra un esquema definido
- **Agnóstico al transporte**: Puede usar HTTP, WebSockets, o cualquier otro protocolo
- **Independiente de la base de datos**: Puede conectarse a cualquier base de datos o servicio

## 🆚 GraphQL vs REST API

### Ventajas de GraphQL sobre REST

#### 1. **Peticiones más Eficientes**
```graphql
# GraphQL - Una sola petición
query {
  usuario(id: "123") {
    nombre
    email
    tareas {
      id
      nombre
      estado
    }
  }
}
```

```http
# REST - Múltiples peticiones
GET /usuarios/123
GET /usuarios/123/tareas
```

#### 2. **Flexibilidad en las Consultas**
- Los clientes solicitan exactamente los datos que necesitan
- Evita el **over-fetching** (obtener más datos de los necesarios)
- Evita el **under-fetching** (necesitar múltiples requests)

#### 3. **Evolución de la API sin Versiones**
- Nuevos campos se agregan sin afectar clientes existentes
- Campos obsoletos se marcan como deprecated
- Un solo endpoint evoluciona con el tiempo

#### 4. **Introspección**
- El esquema es autodocumentado
- Herramientas pueden generar documentación automáticamente
- Los clientes pueden descubrir capacidades de la API

#### 5. **Tipado Fuerte**
- Schema define tipos exactos para todos los datos
- Validación automática de consultas
- Mejor experiencia de desarrollo con autocompletado

### Cuando Usar GraphQL vs REST

#### Usar GraphQL cuando:
- ✅ Necesitas flexibilidad en las consultas de datos
- ✅ Tienes múltiples clientes (web, móvil, etc.) con diferentes necesidades
- ✅ Quieres reducir el número de peticiones de red
- ✅ Necesitas datos relacionales complejos
- ✅ El equipo puede invertir en configurar el ecosistema GraphQL

#### Usar REST cuando:
- ✅ Necesitas cacheo HTTP simple
- ✅ Tienes operaciones simples CRUD
- ✅ El equipo no tiene experiencia con GraphQL
- ✅ Necesitas compatibilidad con herramientas legacy
- ✅ Las operaciones son principalmente de archivo/binarios

## 🏗️ Arquitectura de GraphQL

### Componentes Principales

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Cliente       │    │   Servidor       │    │   Fuentes de Datos  │
│   GraphQL       │◄──►│   GraphQL        │◄──►│   (DB, APIs, etc.)  │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
│                      │                      │
│ - Queries            │ - Schema             │ - PostgreSQL
│ - Mutations          │ - Resolvers          │ - REST APIs  
│ - Subscriptions      │ - Type System        │ - Microservicios
│                      │ - Validation         │ - Archivos
```

### Schema (Esquema)
Define la estructura de datos y operaciones disponibles:

```graphql
type Query {
  usuarios: [Usuario]
  tareas: [Tarea]
}

type Mutation {
  crearUsuario(input: CrearUsuarioInput!): UsuarioResponse
}

type Usuario {
  id: ID!
  nombre: String!
  email: String
  tareas: [Tarea]
}
```

### Resolvers
Funciones que obtienen los datos para cada campo:

```python
def resolve_usuarios(self, info):
    return get_all_users()

def resolve_tareas(self, parent, info):
    return get_tasks_for_user(parent.id)
```

## 📚 Librerías Utilizadas en el Proyecto

### Backend (Python)

#### 1. **Strawberry GraphQL**
```bash
pip install strawberry-graphql[fastapi]
```

**¿Por qué Strawberry?**
- ✅ Sintaxis moderna con decoradores Python
- ✅ Tipado fuerte con type hints
- ✅ Integración perfecta con FastAPI
- ✅ Soporte para async/await
- ✅ Documentación excelente

```python
import strawberry

@strawberry.type
class Usuario:
    id: strawberry.ID
    nombre: str
    email: str
```

#### 2. **FastAPI**
```bash
pip install fastapi uvicorn
```

**Características:**
- Framework web moderno para Python
- Performance comparable a Node.js y Go
- Documentación automática con OpenAPI
- Validation automática con Pydantic

#### 3. **PyJWT**
```bash
pip install PyJWT cryptography
```

**Para autenticación:**
- Generación y verificación de tokens JWT
- Compatibilidad con múltiples algoritmos
- Integración con FastAPI Security
- Librería ligera y eficiente

### Frontend/Cliente (Python)

#### 1. **gql[all]**
```bash
pip install gql[all]
```

**Cliente GraphQL completo:**
- Transport para HTTP, WebSockets
- Validación de queries
- Soporte para subscriptions
- Cache automático

#### 2. **requests**
```bash
pip install requests
```

**Para HTTP simple:**
- Cliente HTTP sencillo
- Usado en el cliente personalizado
- Ampliamente compatible

### Testing

#### 1. **pytest**
```bash
pip install pytest pytest-asyncio
```

**Framework de testing:**
- Tests para resolvers GraphQL
- Tests de integración con FastAPI
- Fixtures para datos de prueba

## 🎯 Ejemplos Prácticos

### 1. Query Simple
```graphql
query {
  usuarios {
    id
    nombre
    email
  }
}
```

### 2. Query con Variables
```graphql
query GetUsuario($id: ID!) {
  usuario(id: $id) {
    nombre
    tareas {
      nombre
      estado
      fechaCreacion
    }
  }
}
```

Variables:
```json
{
  "id": "123"
}
```

### 3. Mutation
```graphql
mutation CrearTarea($input: CrearTareaInput!) {
  crearTarea(input: $input) {
    success
    message
    tarea {
      id
      nombre
      estado
      usuariosAsignados {
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
    "nombre": "Nueva tarea importante",
    "descripcion": "Descripción detallada",
    "prioridad": "ALTA",
    "usuariosAsignados": ["user1", "user2"]
  }
}
```

### 4. Query Compleja (Dashboard)
```graphql
query Dashboard {
  dashboard {
    estadisticas {
      totalUsuarios
      totalTareas
      tareasCompletadasHoy
      productividadGeneral
    }
    tareasRecientes {
      id
      nombre
      estado
      fechaCreacion
      usuariosAsignados {
        nombre
      }
    }
    usuariosActivos {
      nombre
      estadisticas {
        tareasAsignadas
        productividad
      }
    }
  }
}
```

### 5. Filtros y Paginación
```graphql
query TareasConFiltros {
  tareas(filtro: {
    estado: PENDIENTE,
    prioridad: ALTA,
    textoB usqueda: "importante",
    limite: 10,
    offset: 0
  }) {
    id
    nombre
    prioridad
    fechaCreacion
  }
}
```

## 🔧 Uso del Cliente Python

### Configuración Básica
```python
from api_graphql.client import TaskGraphQLClient

# Inicializar cliente
client = TaskGraphQLClient("http://localhost:4000")

# Autenticarse
auth_data = client.login("admin", "password123")
print(f"Autenticado como: {auth_data['usuario']['nombre']}")
```

### Operaciones Comunes
```python
# Obtener usuarios
usuarios = client.get_usuarios()
for usuario in usuarios:
    print(f"Usuario: {usuario.nombre} - {usuario.email}")

# Crear nueva tarea
nueva_tarea = client.crear_tarea(
    nombre="Implementar nueva funcionalidad",
    descripcion="Desarrollar el módulo de reportes",
    prioridad="ALTA",
    usuarios_asignados=["user1", "user2"]
)

# Obtener dashboard completo
dashboard = client.get_dashboard()
print(f"Total tareas: {dashboard['estadisticas']['totalTareas']}")

# Filtrar tareas
tareas_pendientes = client.get_tareas(
    estado="PENDIENTE",
    limite=20
)
```

### Manejo de Errores
```python
from api_graphql.client import GraphQLError

try:
    usuarios = client.get_usuarios()
except GraphQLError as e:
    print(f"Error GraphQL: {e}")
    for error in e.errors:
        print(f"- {error['message']}")
except Exception as e:
    print(f"Error de conexión: {e}")
```

## 🛠️ Configuración del Servidor

### Ejecutar el Servidor
```python
from api_graphql.server import run_server

# Desarrollo
run_server(host="127.0.0.1", port=4000, reload=True)

# Producción
run_server(host="0.0.0.0", port=80, reload=False, log_level="warning")
```

### Variables de Entorno
```env
# .env
GRAPHQL_HOST=0.0.0.0
GRAPHQL_PORT=4000
JWT_SECRET_KEY=tu_clave_secreta_super_segura
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🔐 Autenticación y Seguridad

### JWT en Headers
```http
POST /graphql
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "query": "query { usuarios { id nombre } }"
}
```

### Niveles de Permisos
```python
# Solo autenticación requerida
@strawberry.field(permission_classes=[IsAuthenticated])
def usuarios(self, info: Info) -> List[Usuario]:
    pass

# Permisos de administrador
@strawberry.field(permission_classes=[IsAdmin])
def crearUsuario(self, input: CrearUsuarioInput) -> UsuarioResponse:
    pass
```

## 🧪 Testing

### Test de Queries
```python
import pytest
from strawberry.test import GraphQLTestClient

def test_get_usuarios():
    client = GraphQLTestClient(schema)
    
    query = """
        query {
            usuarios {
                id
                nombre
            }
        }
    """
    
    result = client.query(query)
    assert result.errors is None
    assert len(result.data["usuarios"]) > 0
```

### Test de Mutations
```python
def test_crear_tarea():
    mutation = """
        mutation CrearTarea($input: CrearTareaInput!) {
            crearTarea(input: $input) {
                success
                tarea {
                    nombre
                }
            }
        }
    """
    
    variables = {
        "input": {
            "nombre": "Test Tarea",
            "descripcion": "Descripción de prueba"
        }
    }
    
    result = client.query(mutation, variable_values=variables)
    assert result.data["crearTarea"]["success"] is True
```

## 🚀 Herramientas de Desarrollo

### 1. GraphQL Playground
Interfaz visual para explorar la API:
- URL: `http://localhost:4000/graphql`
- Autocompletado de queries
- Documentación interactiva
- Historial de queries

### 2. GraphiQL (Alternativo)
Explorador de GraphQL en el navegador:
- Sintaxis highlighting
- Validación en tiempo real
- Explorador de schema

### 3. VS Code Extensions
```
GraphQL: Language Feature Support
GraphQL: Syntax Highlighting
```

## 📊 Monitoreo y Performance

### Métricas Importantes
- Tiempo de respuesta por query
- Profundidad de queries (depth limiting)
- Rate limiting por usuario
- Cache hit rate

### Limitaciones de Seguridad
```python
# En producción, habilitar extensiones de seguridad
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        strawberry.extensions.QueryDepthLimiter(max_depth=10),
        strawberry.extensions.ValidationCache(),
    ]
)
```

## 🎓 Mejores Prácticas

### 1. Diseño de Schema
- ✅ Usar nombres descriptivos
- ✅ Agrupar campos relacionados en tipos
- ✅ Evitar demasiados niveles de anidación
- ✅ Usar tipos escalares apropiados

### 2. Resolvers
- ✅ Mantener resolvers simples y enfocados
- ✅ Usar DataLoaders para evitar N+1 queries
- ✅ Manejar errores apropiadamente
- ✅ Implementar paginación

### 3. Seguridad
- ✅ Validar entrada de usuario
- ✅ Implementar rate limiting
- ✅ Limitar profundidad de queries
- ✅ Usar autenticación y autorización apropiada

### 4. Performance
- ✅ Implementar caching estratégico
- ✅ Usar batch loading para datos relacionados
- ✅ Monitorear queries lentas
- ✅ Optimizar acceso a base de datos

## 🔗 Recursos Adicionales

### Documentación Oficial
- [GraphQL.org](https://graphql.org/) - Especificación oficial
- [Strawberry Docs](https://strawberry.rocks/) - Documentación de Strawberry
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Documentación de FastAPI

### Herramientas Útiles
- [GraphQL Code Generator](https://the-guild.dev/graphql/codegen) - Generación de código
- [Apollo Studio](https://studio.apollographql.com/) - Herramientas de desarrollo
- [Insomnia](https://insomnia.rest/) - Cliente para testing

### Comunidad
- [GraphQL Foundation](https://foundation.graphql.org/)
- [Awesome GraphQL](https://github.com/chentsulin/awesome-graphql)
- [GraphQL Weekly](https://www.graphqlweekly.com/)

---

## ⚡ Comenzar Ahora

1. **Instalar dependencias:**
```bash
cd api-graphql
pip install -r requirements.txt
```

2. **Ejecutar el servidor:**
```bash
python -m api_graphql.server
```

3. **Abrir GraphQL Playground:**
```
http://localhost:4000/graphql
```

4. **Ejecutar tu primera query:**
```graphql
query {
  health
}
```

¡Felicidades! 🎉 Ahora tienes una comprensión completa de GraphQL y cómo implementarlo en Python con Strawberry y FastAPI.