"""Modelos Pydantic para la API REST.

Este módulo define los esquemas de datos para las requests y responses
de la API REST del sistema de gestión de tareas.

Pydantic es una librería de validación de datos que usa type hints de Python
para validar automáticamente los datos de entrada y salida. Cada clase que
hereda de BaseModel se convierte en un esquema que valida y serializa datos.

FastAPI usa estos modelos para:
- Validar automáticamente los datos de entrada
- Generar documentación automática (Swagger/OpenAPI)
- Serializar respuestas JSON
- Proporcionar autocompletado en IDEs

Attributes:
    BaseModel      : Clase base de Pydantic para todos los modelos
    Field          : Función para definir validaciones y metadatos de campos
    field_validator: Decorador para validaciones personalizadas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


# ================================
# MODELOS BASE DE RESPUESTA
# ================================

class BaseResponse(BaseModel):
    """Respuesta base para todas las operaciones de la API.
    
    Este modelo define la estructura estándar de respuesta que utilizan
    todos los endpoints de la API. Proporciona consistencia y facilita
    el manejo de respuestas en el cliente.
    
    Attributes:
        success (bool): Indica si la operación fue exitosa.
        message (str): Mensaje descriptivo del resultado.
        
    Example:
        ```python
        # Respuesta exitosa
        {
            "success": true,
            "message": "Usuario creado exitosamente"
        }
        
        # Respuesta de error
        {
            "success": false,
            "message": "Usuario ya existe"
        }
        ```
    """
    success: bool
    message: str


class ErrorResponse(BaseResponse):
    """Respuesta de error estándar para la API.
    
    Extiende BaseResponse agregando un código de error opcional
    para facilitar el manejo programático de errores específicos.
    
    Attributes:
        success (bool): Siempre False para respuestas de error.
        error_code (str, optional): Código único del error para manejo programático.
        
    Example:
        ```python
        {
            "success": false,
            "message": "Usuario no encontrado",
            "error_code": "USER_NOT_FOUND"
        }
        ```
    """
    success    : bool          = False  # Campo con valor por defecto
    error_code : Optional[str] = None


# ================================
# MODELOS DE USUARIO
# ================================

class UsuarioBase(BaseModel):
    """Esquema base para operaciones con usuarios.
    
    Define los campos comunes que comparten todos los modelos relacionados
    con usuarios. Utiliza el patrón de herencia de Pydantic para evitar
    duplicación de código.
    
    Attributes:
        nombre (str): Nombre único del usuario. Debe tener al menos 1 carácter.
        
    Note:
        Field(...) indica un campo requerido con validaciones adicionales.
        min_length=1 evita strings vacíos.
        description= se muestra en la documentación automática.
    """
    nombre: str = Field(
        ..., 
        min_length  = 1, 
        description = "Nombre único del usuario",
        example     = "juan_perez"
    )


class UsuarioCreate(UsuarioBase):
    """Esquema para crear un nuevo usuario estándar.
    
    Hereda de UsuarioBase y no agrega campos adicionales.
    Los usuarios estándar se crean sin contraseña y deben
    establecerla en su primer login.
    
    Example:
        ```python
        {
            "nombre": "maria_garcia"
        }
        ```
    """
    pass  # No agrega campos adicionales a UsuarioBase


class UsuarioCreateAdmin(UsuarioBase):
    """Esquema para crear un usuario administrador.
    
    Los administradores requieren contraseña desde la creación
    ya que tienen privilegios especiales en el sistema.
    
    Attributes:
        contraseña (str): Contraseña del administrador. Mínimo 3 caracteres.
        
    Example:
        ```python
        {
            "nombre": "admin",
            "contraseña": "admin123"
        }
        ```
    """
    contraseña: str = Field(
        ..., 
        min_length  = 3, 
        description = "Contraseña del administrador",
        example     = "admin123"
    )


class UsuarioResponse(UsuarioBase):
    """Respuesta con información completa del usuario.
    
    Utilizado para devolver información de usuarios en respuestas.
    Nunca incluye la contraseña por seguridad, solo indica si la tiene.
    
    Attributes:
        rol (str): Rol del usuario ('user' o 'admin').
        tiene_password (bool): Indica si el usuario tiene contraseña establecida.
        
    Note:
        Config.from_attributes permite crear instancias desde objetos Python
        que tienen atributos con los mismos nombres.
        
    Example:
        ```python
        {
            "nombre": "juan_perez",
            "rol": "user",
            "tiene_password": true
        }
        ```
    """
    rol           : str  = Field(description = "Rol del usuario", example = "user")
    tiene_password: bool = Field(description = "Indica si tiene contraseña establecida")
    
    # clase interna para configuración adicional
    class Config:
        from_attributes = True  # Permite crear desde objetos Python


class UsuarioListResponse(BaseModel):
    """Respuesta con lista de usuarios.
    
    Encapsula una lista de usuarios para mantener consistencia
    en el formato de respuestas de la API.
    
    Attributes:
        usuarios (List[UsuarioResponse]): Lista de usuarios del sistema.
        
    Example:
        ```python
        {
            "usuarios": [
                {
                    "nombre": "admin",
                    "rol": "admin",
                    "tiene_password": true
                },
                {
                    "nombre": "juan",
                    "rol": "user", 
                    "tiene_password": false
                }
            ]
        }
        ```
    """
    usuarios: List[UsuarioResponse] = Field(
        description = "Lista de usuarios del sistema",
        example     = []
    )


class PaginationMeta(BaseModel):
    """Metadatos de paginación para respuestas con listas.
    
    Proporciona información detallada sobre el estado de la paginación,
    permitiendo a los clientes navegar eficientemente entre páginas.
    
    Attributes:
        current_page   : Página actual (empezando desde 1).
        per_page       : Número de items por página.
        total_items    : Total de items disponibles.
        total_pages    : Total de páginas disponibles.
        has_next       : Si existe una página siguiente.
        has_prev       : Si existe una página anterior.
        next_page      : Número de página siguiente (null si no existe).
        prev_page      : Número de página anterior (null si no existe).
        
    Example:
        ```python
        {
            "current_page": 2,
            "per_page": 10,
            "total_items": 45,
            "total_pages": 5,
            "has_next": true,
            "has_prev": true,
            "next_page": 3,
            "prev_page": 1
        }
        ```
    """
    current_page: int = Field(
        ge          = 1, 
        description = "Página actual",
        example     = 1
    )
    per_page: int = Field(
        ge          = 1, 
        le          = 100, 
        description = "Items por página",
        example     = 10
    )
    total_items: int = Field(
        ge          = 0, 
        description = "Total de items disponibles",
        example     = 45
    )
    total_pages: int = Field(
        ge          = 0, 
        description = "Total de páginas",
        example     = 5
    )
    has_next : bool = Field(
        description = "Indica si hay página siguiente",
        example     = True
    )
    has_prev : bool = Field(
        description = "Indica si hay página anterior",
        example     = False
    )
    next_page: Optional[int] = Field(
        default     = None, 
        description = "Número de página siguiente",
        example     = 2
    )
    prev_page: Optional[int] = Field(
        default     = None, 
        description = "Número de página anterior",
        example     = None
    )


class FilterMeta(BaseModel):
    """Metadatos de filtros aplicados en la consulta.
    
    Documenta qué filtros fueron aplicados para generar los resultados,
    útil para interfaces que necesiten mostrar filtros activos.
    
    Attributes:
        search: Término de búsqueda aplicado (si alguno).
        rol: Filtro por rol aplicado (si alguno).
        
    Example:
        ```python
        {
            "search": "juan",
            "rol": "admin"
        }
        ```
    """
    search: Optional[str] = Field(
        default     =  None,
        description = "Término de búsqueda aplicado",
        example     = "juan"
    )
    rol: Optional[str] = Field(
        default     =  None,
        description = "Filtro por rol aplicado",
        example     = "admin"
    )


class UsuarioListPaginatedResponse(BaseModel):
    """Respuesta con lista paginada de usuarios.
    
    Extiende la respuesta básica de usuarios agregando metadatos
    de paginación y filtros para navegación eficiente.
    
    Attributes:
        usuarios: Lista de usuarios en la página actual.
        pagination: Metadatos de paginación.
        filters_applied: Filtros que fueron aplicados.
        
    Example:
        ```python
        {
            "usuarios": [...],
            "pagination": {
                "current_page": 1,
                "per_page": 10,
                "total_items": 25,
                "total_pages": 3,
                "has_next": true,
                "has_prev": false,
                "next_page": 2,
                "prev_page": null
            },
            "filters_applied": {
                "search": null,
                "rol": "admin"
            }
        }
        ```
    """
    usuarios       : List[UsuarioResponse] = Field(
        description = "Lista de usuarios en la página actual",
        example     = []
    )
    pagination     : PaginationMeta = Field(
        description = "Metadatos de paginación"
    )
    filters_applied: FilterMeta = Field(
        description = "Filtros aplicados en la consulta"
    )


# ================================
# MODELOS DE AUTENTICACIÓN
# ================================

class LoginRequest(BaseModel):
    """Esquema para solicitudes de inicio de sesión.
    
    Define los campos requeridos para autenticar un usuario.
    FastAPI utilizará este esquema para validar automáticamente
    los datos JSON enviados en el body del request.
    
    Attributes:
        nombre (str): Nombre del usuario que intenta autenticarse.
        contraseña (str): Contraseña del usuario.
        
    Example:
        ```python
        # Request body:
        {
            "nombre": "juan_perez",
            "contraseña": "mipassword123"
        }
        ```
    """
    nombre    : str = Field(
        ..., 
        description = "Nombre del usuario",
        example     = "juan_perez"
    )
    contraseña: str = Field(
        ..., 
        description = "Contraseña del usuario",
        example     = "mipassword123"
    )


# NOTA: El modelo de respuesta para /auth/login es TokenResponse (definido en jwt_auth.py)
# que devuelve access_token, refresh_token, token_type y expires_in según el estándar JWT.
# No se necesita un LoginResponse separado ya que TokenResponse cubre las necesidades de autenticación.


class PasswordSetRequest(BaseModel):
    """Esquema para establecer contraseña inicial.
    
    Utilizado cuando un usuario accede por primera vez y debe
    establecer su contraseña inicial.
    
    Attributes:
        nombre (str): Nombre del usuario.
        contraseña (str): Nueva contraseña a establecer.
        
    Example:
        ```python
        {
            "nombre": "nuevo_usuario",
            "contraseña": "miprimerapassword"
        }
        ```
    """
    nombre    : str = Field(..., description = "Nombre del usuario")
    contraseña: str = Field(
        ..., 
        min_length  = 3, 
        description = "  Nueva contraseña a establecer"
    )


class PasswordChangeRequest(BaseModel):
    """Esquema para cambiar contraseña existente.
    
    Requiere la contraseña actual para validar que el usuario
    tiene derecho a cambiarla (autenticación previa).
    
    Attributes:
        nombre (str): Nombre del usuario.
        contraseña_actual (str): Contraseña actual para validación.
        contraseña_nueva (str): Nueva contraseña a establecer.
        
    Example:
        ```python
        {
            "nombre": "juan_perez",
            "contraseña_actual": "password_viejo",
            "contraseña_nueva": "password_nuevo123"
        }
        ```
    """
    nombre            : str = Field(..., description = "Nombre del usuario")
    contraseña_actual : str = Field(..., description = "Contraseña actual")
    contraseña_nueva  : str = Field(
        ..., 
        min_length  = 3, 
        description = "Nueva contraseña"
    )


class PasswordResetRequest(BaseModel):
    """Esquema para resetear contraseña (operación administrativa).
    
    Solo los administradores pueden resetear contraseñas de otros usuarios.
    Esto elimina la contraseña actual, forzando al usuario a establecer una nueva.
    
    Attributes:
        nombre_admin (str)  : Nombre del administrador que ejecuta la operación.
        nombre_usuario (str): Nombre del usuario cuya contraseña se resetea.
        
    Example:
        ```python
        {
            "nombre_admin": "admin",
            "nombre_usuario": "usuario_olvidadizo"
        }
        ```
    """
    nombre_admin   : str = Field(..., description = "Nombre del administrador")
    nombre_usuario : str = Field(..., description = "Nombre del usuario a resetear")


# ================================
# MODELOS DE TAREA
# ================================

class TareaBase(BaseModel):
    """Esquema base para operaciones con tareas.
    
    Define los campos fundamentales que toda tarea debe tener.
    Utilizado como base para modelos de creación y respuesta.
    
    Attributes:
        nombre (str)      : Nombre único identificador de la tarea.
        descripcion (str) : Descripción detallada de lo que implica la tarea.
        
    Note:
        Ambos campos son requeridos y deben tener al menos 1 carácter.
    """
    nombre     : str = Field(
        ..., 
        min_length  = 1, 
        description = "Nombre único de la tarea",
        example     = "Desarrollo de API REST"
    )
    descripcion: str = Field(
        ..., 
        min_length  = 1, 
        description = "Descripción detallada de la tarea",
        example     = "Implementar endpoints para gestión de usuarios y tareas"
    )


class TareaCreate(TareaBase):
    """Esquema para crear nuevas tareas.
    
    Hereda todos los campos de TareaBase sin agregar campos adicionales.
    Las tareas se crean en estado 'pendiente' por defecto y sin usuarios asignados.
    
    Example:
        ```python
        {
            "nombre": "Documentar API",
            "descripcion": "Escribir documentación completa de todos los endpoints"
        }
        ```
    """
    pass  # Hereda todos los campos de TareaBase


class ComentarioResponse(BaseModel):
    """Respuesta para comentarios individuales de tareas.
    
    Representa un comentario específico con su metadata.
    Los comentarios permiten comunicación y seguimiento del progreso.
    
    Attributes:
        comentario (str) : Texto del comentario.
        usuario (str)    : Usuario que realizó el comentario.
        fecha (str)      : Timestamp de cuando se realizó el comentario.
        
    Example:
        ```python
        {
            "comentario": "He completado la primera fase del desarrollo",
            "usuario": "juan_perez",
            "fecha": "2025-11-21 14:30:00"
        }
        ```
    """
    comentario : str = Field(description = "Texto del comentario")
    usuario    : str = Field(description = "Usuario que realizó el comentario") 
    fecha      : str = Field(description = "Fecha y hora del comentario")


class TareaResponse(TareaBase):
    """Respuesta con información completa de una tarea.
    
    Modelo utilizado para devolver toda la información disponible de una tarea,
    incluyendo su estado actual, usuarios asignados y comentarios.
    
    Attributes:
        estado (str)                           : Estado actual ('pendiente' o 'finalizada').
        fecha_creacion (str)                   : Timestamp de creación de la tarea.
        usuarios_asignados (List[str])         : Lista de nombres de usuarios asignados.
        comentarios (List[ComentarioResponse]) : Lista de comentarios de la tarea.
        esta_finalizada (bool)                 : Flag calculado del estado de finalización.
        
    Note:
        El field_validator se ejecuta automáticamente cuando FastAPI
        deserializa los datos, convirtiendo tuplas internas en objetos estructurados.
        
    Example:
        ```python
        {
            "nombre": "Desarrollo de API REST",
            "descripcion": "Implementar endpoints...",
            "estado": "pendiente",
            "fecha_creacion": "2025-11-20 09:00:00",
            "usuarios_asignados": ["juan_perez", "maria_garcia"],
            "comentarios": [
                {
                    "comentario": "Iniciando desarrollo",
                    "usuario": "juan_perez",
                    "fecha": "2025-11-20 10:00:00"
                }
            ],
            "esta_finalizada": false
        }
        ```
    """
    estado             : str                      = Field(description = "Estado de la tarea", example = "pendiente")
    fecha_creacion     : str                      = Field(description = "Fecha de creación")
    usuarios_asignados : List[str]                = Field(description = "Usuarios asignados a la tarea")
    comentarios        : List[ComentarioResponse] = Field(description = "Comentarios de la tarea")
    esta_finalizada    : bool                     = Field(description = "Indica si la tarea está finalizada")
    
    @field_validator('comentarios', mode='before')
    @classmethod
    def parse_comentarios(cls, v):
        """Convierte tuplas de comentarios en objetos ComentarioResponse.
        
        El sistema interno almacena comentarios como tuplas (comentario, usuario, fecha).
        Este validator automáticamente los convierte en objetos estructurados
        para la respuesta de la API.
        
        Args:
            v: Valor del campo comentarios (puede ser lista de tuplas o objetos).
            
        Returns:
            Lista de objetos ComentarioResponse.
            
        Note:
            @field_validator es el nuevo sistema de validación de Pydantic V2.
            mode='before' indica que se ejecuta antes del procesamiento normal.
            @classmethod es requerido en Pydantic V2.
        """
        if v and isinstance(v[0], tuple):
            return [
                ComentarioResponse(
                    comentario = comentario[0],
                    usuario    = comentario[1], 
                    fecha      = comentario[2]
                ) for comentario in v
            ]
        return v


class TareaListResponse(BaseModel):
    """Respuesta con lista de tareas.
    
    Encapsula múltiples tareas para mantener consistencia en el formato
    de respuestas de listados.
    
    Attributes:
        tareas (List[TareaResponse]): Lista de tareas con información completa.
        
    Example:
        ```python
        {
            "tareas": [
                {
                    "nombre": "Tarea 1",
                    "descripcion": "...",
                    "estado": "pendiente",
                    # ... más campos
                },
                {
                    "nombre": "Tarea 2", 
                    "descripcion": "...",
                    "estado": "finalizada",
                    # ... más campos
                }
            ]
        }
        ```
    """
    tareas: List[TareaResponse] = Field(description="Lista de tareas")


class TareaResumenResponse(BaseModel):
    """Respuesta con resumen simplificado de tarea.
    
    Versión condensada de información de tarea, útil para listados
    donde no se necesita información completa como comentarios.
    
    Attributes:
        nombre (str)                   : Nombre de la tarea.
        descripcion (str)              : Descripción de la tarea.
        estado (str)                   : Estado actual.
        fecha_creacion (str)           : Fecha de creación.
        usuarios_asignados (List[str]) : Usuarios asignados.
        total_comentarios (int)        : Número total de comentarios.
        esta_finalizada (bool)         : Estado de finalización.
        
    Example:
        ```python
        {
            "nombre": "Tarea importante",
            "descripcion": "...",
            "estado": "pendiente",
            "fecha_creacion": "2025-11-20 09:00:00",
            "usuarios_asignados": ["juan"],
            "total_comentarios": 3,
            "esta_finalizada": false
        }
        ```
    """
    nombre             : str
    descripcion        : str
    estado             : str
    fecha_creacion     : str
    usuarios_asignados : List[str]
    total_comentarios  : int
    esta_finalizada    : bool


class AsignarUsuarioRequest(BaseModel):
    """Esquema para asignar un usuario a una tarea específica.
    
    Operación que vincula un usuario con una tarea para indicar
    responsabilidad o participación en la realización de la misma.
    
    Attributes:
        nombre_tarea (str): Nombre exacto de la tarea existente.
        nombre_usuario (str): Nombre exacto del usuario existente.
        
    Example:
        ```python
        {
            "nombre_tarea": "Desarrollo de API REST",
            "nombre_usuario": "juan_perez"
        }
        ```
        
    Note:
        Tanto la tarea como el usuario deben existir previamente en el sistema.
        Un usuario puede estar asignado a múltiples tareas.
        Una tarea puede tener múltiples usuarios asignados.
    """
    nombre_tarea    : str = Field(..., description = "Nombre de la tarea")
    nombre_usuario  : str = Field(..., description = "Nombre del usuario")


class ComentarioRequest(BaseModel):
    """Esquema para agregar comentarios a una tarea.
    
    Los comentarios permiten comunicación entre usuarios y seguimiento
    del progreso de las tareas a lo largo del tiempo.
    
    Attributes:
        nombre_tarea (str)   : Nombre de la tarea a comentar.
        comentario (str)     : Texto del comentario a agregar.
        nombre_usuario (str): Usuario que realiza el comentario.
        
    Example:
        ```python
        {
            "nombre_tarea": "Desarrollo de API REST",
            "comentario": "He completado el 50% del desarrollo, faltan pruebas",
            "nombre_usuario": "juan_perez"
        }
        ```
        
    Note:
        Los comentarios se almacenan con timestamp automático.
        No se pueden editar o eliminar una vez creados.
        Se recomienda ser descriptivo en los comentarios.
    """
    nombre_tarea : str = Field(..., description="Nombre de la tarea")
    comentario   : str = Field(
        ..., 
        min_length  = 1, 
        description ="Texto del comentario",
        example     = "Progreso del 50% completado"
    )
    nombre_usuario: str = Field(..., description="Usuario que hace el comentario")


class FinalizarTareaRequest(BaseModel):
    """Esquema para marcar una tarea como finalizada.
    
    Operación que cambia el estado de una tarea de 'pendiente' a 'finalizada'.
    Las tareas finalizadas se guardan también en un archivo JSON separado.
    
    Attributes:
        nombre_tarea (str): Nombre exacto de la tarea a finalizar.
        
    Example:
        ```python
        {
            "nombre_tarea": "Desarrollo de API REST"
        }
        ```
        
    Note:
        Una vez finalizada, una tarea no puede volver al estado pendiente.
        Las tareas finalizadas siguen apareciendo en las consultas.
        Se recomienda agregar un comentario final antes de finalizar.
    """
    nombre_tarea: str = Field(..., description="Nombre de la tarea")


# ================================
# MODELOS DE ESTADÍSTICAS
# ================================

class EstadisticasUsuarios(BaseModel):
    """Estadísticas específicas de usuarios del sistema.
    
    Proporciona métricas útiles para administración y monitoreo
    del estado de los usuarios en el sistema.
    
    Attributes:
        total (int)        : Número total de usuarios registrados.
        admins (int)       : Número de usuarios con rol de administrador.
        users (int)        : Número de usuarios con rol estándar.
        sin_password (int) : Número de usuarios sin contraseña establecida.
        
    Example:
        ```python
        {
            "total": 15,
            "admins": 2,
            "users": 13,
            "sin_password": 3
        }
        ```
        
    Note:
        sin_password indica usuarios que necesitan establecer contraseña inicial.
        total = admins + users (invariante matemática).
    """
    total        : int = Field(description = "Número total de usuarios")
    admins       : int = Field(description = "Número de administradores")
    users        : int = Field(description = "Número de usuarios estándar")
    sin_password : int = Field(description = "Usuarios sin contraseña establecida")


class EstadisticasTareas(BaseModel):
    """Estadísticas específicas de tareas del sistema.
    
    Proporciona métricas sobre el estado y distribución de las tareas
    para análisis de carga de trabajo y productividad.
    
    Attributes:
        total (int)        : Número total de tareas en el sistema.
        pendientes (int)   : Número de tareas en estado pendiente.
        finalizadas (int)  : Número de tareas completadas.
        sin_asignar (int)  : Número de tareas sin usuarios asignados.
        
    Example:
        ```python
        {
            "total": 25,
            "pendientes": 18,
            "finalizadas": 7,
            "sin_asignar": 4
        }
        ```
        
    Note:
        total = pendientes + finalizadas (invariante de estado).
        sin_asignar puede incluir tareas pendientes y finalizadas.
    """
    total        : int = Field(description = "Número total de tareas")
    pendientes   : int = Field(description = "Tareas en estado pendiente")
    finalizadas  : int = Field(description = "Tareas completadas")
    sin_asignar  : int = Field(description = "Tareas sin usuarios asignados")


class EstadisticasResponse(BaseModel):
    """Respuesta con estadísticas completas del sistema.
    
    Combina todas las métricas del sistema en una respuesta unificada.
    Útil para dashboards y reportes administrativos.
    
    Attributes:
        usuarios (EstadisticasUsuarios): Métricas de usuarios.
        tareas (EstadisticasTareas): Métricas de tareas.
        
    Example:
        ```python
        {
            "usuarios": {
                "total": 15,
                "admins": 2,
                "users": 13,
                "sin_password": 3
            },
            "tareas": {
                "total": 25,
                "pendientes": 18,
                "finalizadas": 7,
                "sin_asignar": 4
            }
        }
        ```
    """
    usuarios: EstadisticasUsuarios = Field(description="Estadísticas de usuarios")
    tareas  : EstadisticasTareas   = Field(description="Estadísticas de tareas")


# ================================
# MODELOS DE FILTROS Y CONSULTAS
# ================================

class FiltroTareasRequest(BaseModel):
    """Filtros para consultar tareas con criterios específicos.
    
    Permite filtrar el listado de tareas según diferentes criterios
    para obtener subconjuntos relevantes de información.
    
    Attributes:
        usuario (str, optional)    : Filtrar tareas asignadas a usuario específico.
        estado (str, optional)     : Filtrar por estado ('pendiente' o 'finalizada').
        incluir_finalizadas (bool) : Si incluir tareas finalizadas en el resultado.
        
    Example:
        ```python
        # Todas las tareas pendientes de juan
        {
            "usuario": "juan_perez",
            "estado": "pendiente",
            "incluir_finalizadas": false
        }
        
        # Todas las tareas (sin filtros)
        {
            "usuario": null,
            "estado": null,
            "incluir_finalizadas": true
        }
        ```
        
    Note:
        Todos los campos son opcionales y se pueden combinar.
        Si no se especifica filtro, se devuelven todas las tareas.
    """
    usuario            : Optional[str] = Field(
        None, 
        description="Filtrar por usuario específico"
    )
    estado             : Optional[str] = Field(
        None, 
        description="Filtrar por estado (pendiente/finalizada)"
    )
    incluir_finalizadas: bool          = Field(
        True, 
        description="Incluir tareas finalizadas en resultados"
    )


class BusquedaRequest(BaseModel):
    """Esquema para realizar búsquedas en el sistema.
    
    Permite buscar información tanto en usuarios como en tareas
    utilizando términos de búsqueda flexibles.
    
    Attributes:
        termino (str): Término o frase a buscar.
        tipo (str): Ámbito de búsqueda ('usuarios', 'tareas', 'ambos').
        
    Example:
        ```python
        # Buscar "API" en tareas
        {
            "termino": "API",
            "tipo": "tareas"
        }
        
        # Buscar "juan" en usuarios
        {
            "termino": "juan",
            "tipo": "usuarios"
        }
        
        # Búsqueda general
        {
            "termino": "desarrollo",
            "tipo": "ambos"
        }
        ```
        
    Note:
        La búsqueda es case-insensitive y busca coincidencias parciales.
        tipo='ambos' es el valor por defecto si no se especifica.
    """
    termino: str = Field(
        ..., 
        min_length  = 1, 
        description = "Término de búsqueda",
        example     = "API development"
    )
    tipo   : str = Field(
        "ambos", 
        description = "Ámbito de búsqueda: usuarios, tareas, ambos"
    )
    
    @field_validator('tipo')
    @classmethod
    def validate_tipo(cls, v):
        """Valida que el tipo de búsqueda sea uno de los valores permitidos.
        
        Args:
            v (str): Valor del campo tipo.
            
        Returns:
            str: Valor validado.
            
        Raises:
            ValueError: Si el tipo no es válido.
            
        Note:
            Este validator se ejecuta automáticamente cuando se crea
            una instancia del modelo, garantizando datos válidos.
        """
        if v not in ['usuarios', 'tareas', 'ambos']:
            raise ValueError('tipo debe ser: usuarios, tareas o ambos')
        return v


# ================================
# MODELOS DE SISTEMA
# ================================

class HealthResponse(BaseModel):
    """Respuesta del health check de la API.
    
    Endpoint de monitoreo que indica el estado operativo de la API.
    Útil para sistemas de monitoreo, load balancers y debugging.
    
    Attributes:
        status (str)         : Estado actual del sistema ('online', 'healthy', etc.).
        timestamp (datetime) : Momento exacto de la verificación.
        version (str)        : Versión actual de la API.
        
    Example:
        ```python
        {
            "status": "healthy",
            "timestamp": "2025-11-21T14:30:00.123456",
            "version": "1.0.0"
        }
        ```
        
    Note:
        Este endpoint siempre debe responder rápidamente.
        Se ejecuta sin autenticación para facilitar monitoreo.
        timestamp se genera automáticamente al momento de la consulta.
    """
    status     : str      = Field(description="Estado del sistema", example="healthy")
    timestamp  : datetime = Field(description="Timestamp de la verificación")
    version    : str      = Field(
        "1.0.0", 
        description ="Versión de la API",
        example     = "1.0.0"
    )