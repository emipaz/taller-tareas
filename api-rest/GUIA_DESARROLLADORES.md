# Guía para Desarrolladores - FastAPI + Pydantic

## 📚 Conceptos Fundamentales

### ¿Qué es FastAPI?

FastAPI es un framework web moderno para Python que facilita la creación de APIs REST. Sus principales ventajas son:

- **Automático**: Genera documentación automática
- **Rápido**: Alto rendimiento, comparable a NodeJS y Go  
- **Intuitivo**: Basado en type hints de Python
- **Estándares**: Compatible con OpenAPI y JSON Schema

### ¿Qué es Pydantic?

Pydantic es una librería de validación de datos que usa type hints para:

- **Validar** datos de entrada automáticamente
- **Serializar** objetos Python a JSON
- **Documentar** automáticamente los esquemas de datos
- **Convertir tipos** automáticamente cuando es posible

## 🏗️ Arquitectura del Proyecto

```
Sistema de Gestión de Tareas
├── Lógica de Negocio (gestor_sistema.py)
├── Modelos de Datos (usuario.py, tarea.py)  
├── Utilidades (utils.py)
├── API REST (api_rest.py)
└── Esquemas API (api_models.py)
```

### Separación de Responsabilidades

- **GestorSistema**: Contiene toda la lógica de negocio
- **FastAPI**: Solo maneja HTTP, validación y respuestas
- **Pydantic**: Define contratos de datos entre cliente y servidor

Esta separación permite:
- Reutilizar lógica entre diferentes interfaces (CLI, Web, API)
- Testing independiente de cada capa
- Mantenimiento más fácil

## 🔧 Conceptos Clave de FastAPI

### 1. Decoradores de Endpoints

```python
@app.get("/usuarios")           # GET request a /usuarios
@app.post("/usuarios")          # POST request a /usuarios  
@app.put("/usuarios/{id}")      # PUT request con parámetro
@app.delete("/usuarios/{id}")   # DELETE request
```

### 2. Path Parameters

```python
@app.get("/usuarios/{nombre}")
async def obtener_usuario(nombre: str):
    # FastAPI automáticamente extrae 'nombre' de la URL
    # /usuarios/juan -> nombre = "juan"
```

### 3. Query Parameters

```python
@app.get("/tareas")
async def listar_tareas(incluir_finalizadas: bool = True):
    # /tareas?incluir_finalizadas=false
    # incluir_finalizadas = False
```

### 4. Request Body

```python
@app.post("/usuarios")
async def crear_usuario(usuario_data: UsuarioCreate):
    # FastAPI valida el JSON contra el esquema UsuarioCreate
    # y convierte automáticamente a objeto Python
```

### 5. Response Models

```python
@app.get("/usuarios", response_model=UsuarioListResponse)
async def listar_usuarios():
    # FastAPI serializa la respuesta según UsuarioListResponse
    # y genera documentación automática
```

### 6. Dependency Injection

```python
def get_gestor() -> GestorSistema:
    return gestor

@app.get("/usuarios")
async def listar_usuarios(gestor_sistema: GestorSistema = Depends(get_gestor)):
    # FastAPI ejecuta get_gestor() y pasa el resultado
    # Útil para testing, configuración, autenticación
```

## 🎯 Conceptos Clave de Pydantic

### 1. BaseModel

```python
class Usuario(BaseModel):
    nombre: str
    edad: int
    activo: bool = True  # Valor por defecto
```

### 2. Field Validation

```python
class Usuario(BaseModel):
    nombre: str = Field(
        ...,                    # Campo requerido
        min_length=1,          # Validación: mínimo 1 caracter
        max_length=50,         # Validación: máximo 50 caracteres
        description="Nombre del usuario",  # Para documentación
        example="juan_perez"   # Ejemplo en la documentación
    )
```

### 3. Field Validators

```python
class Usuario(BaseModel):
    email: str
    
    @field_validator('email')
    @classmethod  # Requerido en Pydantic V2
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email debe contener @')
        return v.lower()  # Normalizar a minúsculas
```

### 4. Model Configuration

```python
class Usuario(BaseModel):
    nombre: str
    
    class Config:
        from_attributes = True  # Crear desde objetos Python
        # Permite: Usuario.from_orm(usuario_objeto)
```

## 🚀 Flujo de una Request

1. **Cliente** envía HTTP request
2. **FastAPI** parsea URL y headers
3. **Pydantic** valida datos de entrada
4. **Endpoint** ejecuta lógica de negocio  
5. **Pydantic** serializa respuesta
6. **FastAPI** envía HTTP response

### Ejemplo Completo

```python
# 1. Cliente envía:
POST /usuarios
Content-Type: application/json
{
    "nombre": "juan"
}

# 2. FastAPI extrae datos y los valida con:
class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=1)

# 3. Endpoint procesa:
@app.post("/usuarios", response_model=BaseResponse)
async def crear_usuario(usuario_data: UsuarioCreate):
    exito, mensaje = gestor.crear_usuario(usuario_data.nombre)
    return BaseResponse(success=exito, message=mensaje)

# 4. FastAPI serializa y responde:
{
    "success": true,
    "message": "Usuario creado exitosamente"
}
```

## 🛠️ Mejores Prácticas

### Organización de Código

1. **Separar modelos** (api_models.py) de endpoints (api_rest.py)
2. **Agrupar endpoints** por funcionalidad con comentarios
3. **Usar dependency injection** para compartir estado
4. **Documentar exhaustivamente** con docstrings

### Manejo de Errores

```python
# Usar HTTPException para errores controlados
if not usuario:
    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )

# Capturar excepciones generales
try:
    resultado = operacion_riesgosa()
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

### Validación de Datos

```python
# Validaciones básicas con Field
nombre: str = Field(..., min_length=1, max_length=50)
edad: int = Field(..., ge=0, le=120)  # Entre 0 y 120

# Validaciones complejas con validators
@field_validator('password')
@classmethod
def validate_password(cls, v):
    if len(v) < 8:
        raise ValueError('Password debe tener al menos 8 caracteres')
    return v
```

### Response Models Consistentes

```python
# Todas las operaciones devuelven formato similar
class BaseResponse(BaseModel):
    success: bool
    message: str

# Respuestas de datos extienden la base
class UsuarioResponse(BaseModel):
    usuario: Usuario
    success: bool = True
```

## 🔍 Debugging y Testing

### Documentación Automática

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Logs Útiles

FastAPI logea automáticamente:
- Todas las requests con timestamp
- Status codes de respuesta
- Errores de validación
- Excepciones no controladas

### Testing Manual

```bash
# Health check
curl http://localhost:8000/health

# Crear usuario
curl -X POST http://localhost:8000/usuarios \
     -H "Content-Type: application/json" \
     -d '{"nombre": "test_user"}'

# Login
curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"nombre": "test_user", "contraseña": "test123"}'
```

## ⚡ Tips para Desarrollo

1. **Usar reload=True** en desarrollo para ver cambios automáticamente
2. **Explorar /docs** para entender todos los endpoints disponibles
3. **Leer los logs** para entender errores de validación
4. **Probar edge cases** como datos faltantes o inválidos
5. **Documentar ejemplos** en docstrings para otros desarrolladores

## 📈 Próximos Pasos

Para llevar esta API a producción:

1. **Autenticación**: Implementar JWT tokens reales
2. **Autorización**: Middleware para verificar permisos
3. **Rate Limiting**: Prevenir abuso de la API
4. **Logging estructurado**: Para monitoreo y debugging
5. **Testing automatizado**: Unit tests y integration tests
6. **HTTPS**: Certificados SSL para seguridad
7. **Documentación**: Guides de uso para clientes de la API