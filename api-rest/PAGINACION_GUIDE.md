# 📄 Guía de Implementación de Paginación - API REST

## 🎯 ¿Qué es la Paginación?

La paginación es una técnica que divide grandes conjuntos de datos en **páginas más pequeñas** y manejables. En lugar de devolver 10,000 usuarios de una vez, devuelve 10 usuarios por página.

## 🚀 Beneficios de la Paginación

### ⚡ **Performance**
- **Menos memoria**: Solo carga datos de la página actual
- **Respuestas más rápidas**: Menos datos para transferir
- **Mejor UX**: Las interfaces cargan más rápido

### 📊 **Escalabilidad**
- **Sistemas grandes**: Maneja millones de registros eficientemente
- **Ancho de banda**: Reduce tráfico de red significativamente
- **Recursos del servidor**: Menos carga CPU y memoria

## 🔧 Implementación Completa

### 1. **Query Parameters Estándar**

```python
# Parámetros de paginación típicos
@app.get("/usuarios")
async def listar_usuarios(
    page: int = 1,           # Página actual (empezar desde 1)
    limit: int = 10,         # Items por página  
    search: Optional[str] = None,    # Búsqueda
    sort: str = "nombre",            # Campo de ordenamiento
    order: str = "asc"               # Dirección: asc/desc
):
```

### 2. **Cálculos de Paginación**

```python
def paginate_data(data: List, page: int, limit: int):
    """Función helper para paginación."""
    
    # Calcular totales
    total_items = len(data)
    total_pages = (total_items + limit - 1) // limit  # Ceiling division
    
    # Calcular índices
    start_index = (page - 1) * limit
    end_index = start_index + limit
    
    # Obtener página actual
    page_data = data[start_index:end_index]
    
    return {
        "data": page_data,
        "pagination": {
            "current_page": page,
            "per_page": limit,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
```

### 3. **Validaciones Importantes**

```python
# ✅ Validaciones que debes implementar
if page < 1:
    raise HTTPException(400, "Página debe ser >= 1")

if limit < 1 or limit > 100:
    raise HTTPException(400, "Límite debe estar entre 1-100")

if page > total_pages and total_items > 0:
    raise HTTPException(404, f"Página {page} no existe")
```

## 🌐 Ejemplos de Uso

### **Uso Básico**
```bash
# Primera página, 10 usuarios
curl "http://localhost:8000/usuarios?page=1&limit=10"

# Segunda página, 20 usuarios  
curl "http://localhost:8000/usuarios?page=2&limit=20"
```

### **Con Filtros**
```bash
# Solo administradores, página 1
curl "http://localhost:8000/usuarios?page=1&limit=5&rol=admin"

# Buscar por nombre
curl "http://localhost:8000/usuarios?search=juan&page=1&limit=10"
```

### **Respuesta Típica**
```json
{
    "usuarios": [
        {"nombre": "admin", "rol": "admin", "tiene_password": true},
        {"nombre": "juan", "rol": "user", "tiene_password": false}
    ],
    "pagination": {
        "current_page": 1,
        "per_page": 10, 
        "total_items": 45,
        "total_pages": 5,
        "has_next": true,
        "has_prev": false,
        "next_page": 2,
        "prev_page": null
    },
    "filters_applied": {
        "search": "juan",
        "rol": null
    }
}
```

## 🎨 Frontend Integration

### **JavaScript/React Example**
```javascript
// Estado de paginación
const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total_pages: 0
});

// Función para cambiar página
const changePage = async (newPage) => {
    const response = await fetch(
        `http://localhost:8000/usuarios?page=${newPage}&limit=${pagination.limit}`
    );
    const data = await response.json();
    
    setUsuarios(data.usuarios);
    setPagination(prev => ({
        ...prev,
        page: newPage,
        total_pages: data.pagination.total_pages
    }));
};

// Componente de navegación
function PaginationControls() {
    return (
        <div>
            <button 
                disabled={!pagination.has_prev}
                onClick={() => changePage(pagination.page - 1)}
            >
                Anterior
            </button>
            
            <span>Página {pagination.page} de {pagination.total_pages}</span>
            
            <button
                disabled={!pagination.has_next} 
                onClick={() => changePage(pagination.page + 1)}
            >
                Siguiente
            </button>
        </div>
    );
}
```

## 🔄 Paginación en Otras Entidades

### **Aplicar a Tareas**
```python
@app.get("/tareas", response_model=TareaListPaginatedResponse)
async def listar_tareas(
    page: int = 1,
    limit: int = 10,
    estado: Optional[str] = None,  # pendiente/completada
    usuario_asignado: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None
):
    # Misma lógica de paginación + filtros específicos de tareas
```

### **Aplicar a Comentarios**
```python
@app.get("/tareas/{nombre}/comentarios")
async def listar_comentarios_tarea(
    nombre: str,
    page: int = 1,
    limit: int = 20
):
    # Paginación para comentarios de una tarea específica
```

## 🏆 Mejores Prácticas

### ✅ **Recomendaciones**
- **Límite por defecto**: 10-25 items por página
- **Límite máximo**: No más de 100 items por página
- **Consistencia**: Usar mismo formato en toda la API
- **Metadatos**: Incluir toda la info de navegación
- **Cache**: Cache resultados frecuentes
- **Índices DB**: Para filtros y ordenamiento

### ⚠️ **Evitar**
- **Sin límites**: Nunca devolver datos ilimitados
- **Páginas enormes**: Más de 100 items impacta performance
- **Índices desde 0**: Confuso, usar páginas desde 1
- **Sin validaciones**: Siempre validar parámetros de entrada

## 📊 Performance Tips

### **Para Datasets Grandes (>100K registros)**
```python
# Cursor-based pagination (más eficiente)
@app.get("/usuarios/cursor")
async def listar_usuarios_cursor(
    cursor: Optional[str] = None,
    limit: int = 10
):
    # Usar un campo único (ID, timestamp) como cursor
    # SELECT * FROM usuarios WHERE id > cursor LIMIT limit
```

### **Optimizaciones Database**
```sql
-- Índices para paginación eficiente
CREATE INDEX idx_usuarios_nombre ON usuarios(nombre);
CREATE INDEX idx_usuarios_rol ON usuarios(rol);
CREATE INDEX idx_tareas_fecha ON tareas(fecha_creacion);

-- Query optimizada
SELECT * FROM usuarios 
WHERE rol = ? 
ORDER BY nombre 
LIMIT ? OFFSET ?;
```

## 🧪 Testing de Paginación

```python
def test_pagination():
    # Crear 25 usuarios de prueba
    for i in range(25):
        create_test_user(f"user_{i}")
    
    # Test página 1
    response = client.get("/usuarios?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["usuarios"]) == 10
    assert data["pagination"]["current_page"] == 1
    assert data["pagination"]["total_items"] == 25
    assert data["pagination"]["total_pages"] == 3
    assert data["pagination"]["has_next"] == True
    assert data["pagination"]["has_prev"] == False
    
    # Test última página
    response = client.get("/usuarios?page=3&limit=10")
    data = response.json()
    
    assert len(data["usuarios"]) == 5  # Últimos 5 usuarios
    assert data["pagination"]["has_next"] == False
    assert data["pagination"]["has_prev"] == True
```

¡Con esta implementación tu API puede manejar eficientemente desde cientos hasta millones de registros! 🚀