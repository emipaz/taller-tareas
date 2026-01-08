"""
Tipos GraphQL para el Sistema de Gestión de Tareas.

Este módulo define todos los tipos GraphQL que representan las entidades del sistema
utilizando Strawberry GraphQL. Incluye tipos de datos, enums, inputs para mutations
y responses estructuradas.

Clases principales:
    Usuario                 : Representa un usuario del sistema con sus propiedades y relaciones.
    Tarea                   : Representa una tarea con estado, asignaciones y metadata.
    Comentario              : Representa comentarios asociados a las tareas.
    EstadisticasGenerales   : Métricas y estadísticas del sistema.
    EstadisticasUsuario     : Métricas específicas por usuario.
    
Enums:
    RolUsuario  : Roles disponibles (ADMIN, USUARIO).
    EstadoTarea : Estados de las tareas (PENDIENTE, FINALIZADA).
    
Inputs:
    CrearUsuarioInput : Datos necesarios para crear un usuario.
    CrearTareaInput   : Datos necesarios para crear una tarea.
    FiltroTareas      : Filtros para consultas de tareas.
    FiltroUsuarios    : Filtros para consultas de usuarios.

Example:
    from api_graphql.types import Usuario, Tarea, CrearTareaInput
    
    # Crear input para nueva tarea
    input_tarea = CrearTareaInput(
        nombre="Nueva tarea",
        descripcion="Descripción de la tarea",
        usuarios_ids=["user1", "user2"]
    )
"""

import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum

import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum


@strawberry.enum
class RolUsuario(Enum):
    """Enum que define los roles disponibles en el sistema.
    
    Attributes:
        ADMIN : Usuario con permisos administrativos completos.
        USER  : Usuario estándar con permisos limitados.
        
    Note:
        Los valores coinciden con los roles definidos en core.usuario.Usuario.
    """
    ADMIN = "admin"
    USER  = "user"


@strawberry.enum
class EstadoTarea(Enum):
    """Enum que define los estados posibles de una tarea.
    
    Attributes:
        PENDIENTE  : Tarea creada pero no completada.
        FINALIZADA : Tarea completada exitosamente.
        
    Note:
        Los valores coinciden con los estados definidos en core.tarea.Tarea.
    """
    PENDIENTE  = "pendiente"
    FINALIZADA = "finalizada"


@strawberry.type
class Comentario:
    """Representa un comentario asociado a una tarea.
    
    Este tipo mapea con las tuplas de comentarios en core.tarea.Tarea.comentarios
    que tienen el formato (comentario: str, usuario: str, fecha: str).
    
    Attributes:
        texto (str) : Contenido del comentario.
        autor (str) : Nombre del usuario que escribió el comentario.
        fecha (str) : Timestamp de creación en formato string.
        
    Note:
        En core.tarea.Tarea los comentarios se almacenan como:
        List[Tuple[str, str, str]] = [(comentario, usuario, fecha), ...]
        
    Example:
        comentario = Comentario(
            texto="Este es un comentario de prueba",
            autor="juan_perez", 
            fecha="2024-01-01 10:00:00"
        )
    """
    id    : Optional[int] = None
    texto : str
    autor : str
    fecha : str


@strawberry.type
class Usuario:
    """Representa un usuario del sistema de gestión de tareas.
    
    Este tipo GraphQL mapea directamente con la clase core.usuario.Usuario
    y refleja exactamente los campos que maneja el sistema core.
    
    Attributes:
        id (str)              : Identificador único (mismo que nombre).
        nombre (str)          : Nombre único del usuario.
        rol (RolUsuario)      : Rol del usuario (ADMIN o USER).
        tiene_password (bool) : Indica si el usuario tiene contraseña configurada.
        activo (bool)         : Siempre True (campo para compatibilidad GraphQL).
        
    Methods:
        tareas_asignadas : Retorna las tareas asignadas a este usuario.
        estadisticas     : Retorna estadísticas del usuario.
        
    Note:
        - No incluye email (no existe en el core)
        - No incluye fecha_registro (no existe en el core)
        - activo siempre es True (el core no maneja usuarios inactivos)
        
    Example:
        usuario = Usuario(
            id="juan_perez",
            nombre="juan_perez",
            rol=RolUsuario.USER,
            tiene_password=False,
            activo=True
        )
    """
    id              : str                 # Identificador único (mismo que nombre)
    nombre          : str
    rol             : RolUsuario
    tiene_password  : bool                = False
    activo          : bool                = True
    
    # Campos que se resuelven dinámicamente
    @strawberry.field
    def tareas_asignadas(self) -> List["Tarea"]:
        """Obtiene las tareas asignadas a este usuario.
        
        Returns:
            List[Tarea]: Lista de tareas asignadas al usuario.
            
        Note:
            Este campo se resuelve dinámicamente a través de los resolvers.
            El valor por defecto es una lista vacía.
        """
        # Se resolverá en el resolver
        return []
    
    @strawberry.field
    def estadisticas(self) -> "EstadisticasUsuario":
        """Obtiene estadísticas del usuario.
        
        Returns:
            EstadisticasUsuario: Objeto con métricas del usuario.
            
        Note:
            Este campo se resuelve dinámicamente a través de los resolvers.
            Incluye tareas asignadas, completadas, pendientes y productividad.
        """
        # Se resolverá en el resolver
        return EstadisticasUsuario(
            tareas_asignadas   = 0,
            tareas_completadas = 0,
            tareas_pendientes  = 0,
            productividad      = 0.0
        )


@strawberry.type
class Tarea:
    """Representa una tarea en el sistema de gestión.
    
    Este tipo GraphQL mapea directamente con la clase core.tarea.Tarea
    y expone sus propiedades principales.
    
    Attributes:
        nombre (str)             : Nombre único de la tarea (pk).
        descripcion (str)        : Descripción detallada de la tarea.
        estado (EstadoTarea)     : Estado actual (PENDIENTE o FINALIZADA).
        fecha_creacion (str)     : Fecha y hora de creación en formato string.
        
    Methods:
        usuarios_asignados : Retorna nombres de usuarios asignados (List[str] en core).
        comentarios        : Retorna comentarios de la tarea.
        esta_finalizada    : Indica si la tarea está finalizada.
        
    Note:
        Los campos coinciden exactamente con core.tarea.Tarea:
        - nombre, descripcion, estado, fecha_creacion son campos directos
        - usuarios_asignados y comentarios son listas que se resuelven dinámicamente
        
    Example:
        tarea = Tarea(
            nombre="Implementar API",
            descripcion="Desarrollar endpoints REST",
            estado=EstadoTarea.PENDIENTE,
            fecha_creacion="2024-01-01 10:00:00"
        )
    """
    id              : str             # Identificador único
    nombre          : str
    descripcion     : str
    estado          : EstadoTarea
    fecha_creacion  : str
    
    # Campos que se resuelven dinámicamente
    @strawberry.field
    def fecha_finalizacion(self) -> Optional[str]:
        """Fecha de finalización de la tarea (si está finalizada).
        
        Returns:
            Optional[str]: Fecha de finalización si la tarea está finalizada, None en caso contrario.
            
        Note:
            Este campo se calcula dinámicamente. Si la tarea está finalizada, 
            se podría calcular o almacenar la fecha de finalización.
        """
        # Se resolverá en el resolver
        return None
    
    # Campos que se resuelven dinámicamente
    @strawberry.field
    def usuarios_asignados(self) -> List[str]:
        """Obtiene nombres de usuarios asignados a esta tarea.
        
        Returns:
            List[str]: Lista de nombres de usuarios asignados.
            
        Note:
            En core.tarea.Tarea esto es una lista de strings (nombres de usuario).
            Este campo se resuelve dinámicamente a través de los resolvers.
        """
        # Se resolverá en el resolver
        return []
    
    @strawberry.field
    def comentarios(self) -> List[Comentario]:
        """Obtiene comentarios de la tarea.
        
        Returns:
            List[Comentario]: Lista de comentarios asociados.
            
        Note:
            En core.tarea.Tarea esto es una List[Tuple[str, str, str]] con formato:
            (comentario, usuario, fecha). Este resolver convierte a objetos Comentario.
        """
        # Se resolverá en el resolver
        return []
    
    @strawberry.field
    def esta_finalizada(self) -> bool:
        """Indica si la tarea está finalizada.
        
        Returns:
            bool: True si la tarea está finalizada, False en caso contrario.
            
        Note:
            Mapea directamente al método esta_finalizada() de core.tarea.Tarea.
        """
        return self.estado == EstadoTarea.FINALIZADA


@strawberry.type
class EstadisticasUsuario:
    """Estadísticas y métricas de un usuario específico.
    
    Attributes:
        tareas_asignadas (int)     : Número total de tareas asignadas.
        tareas_completadas (int)   : Número de tareas finalizadas.
        tareas_pendientes (int)    : Número de tareas aún pendientes.
        productividad (float)      : Porcentaje de tareas completadas (0-100).
        
    Example:
        stats = EstadisticasUsuario(
            tareas_asignadas=10,
            tareas_completadas=7,
            tareas_pendientes=3,
            productividad=70.0
        )
    """
    tareas_asignadas   : int
    tareas_completadas : int
    tareas_pendientes  : int
    productividad      : float  # Porcentaje de tareas completadas


@strawberry.type
class EstadisticasGenerales:
    """Estadísticas generales del sistema completo.
    
    Proporciona una vista consolidada de todas las métricas importantes
    del sistema de gestión de tareas.
    
    Attributes:
        total_usuarios    (int)             : Número total de usuarios registrados.
        usuarios_activos  (int)             : Número de usuarios activos.
        total_tareas      (int)             : Número total de tareas creadas.
        tareas_pendientes (int)             : Número de tareas sin completar.
        tareas_completadas (int)            : Número de tareas finalizadas.
        tareas_por_usuario_promedio (float) : Promedio de tareas por usuario.
        productividad_general (float)       : Porcentaje general de finalización.
        
    Example:
        stats = EstadisticasGenerales(
            total_usuarios=25,
            usuarios_activos=20,
            total_tareas=100,
            tareas_pendientes=30,
            tareas_completadas=70,
            tareas_por_usuario_promedio=4.0,
            productividad_general=70.0
        )
    """
    total_usuarios               : int
    usuarios_activos             : int
    total_tareas                 : int
    tareas_pendientes            : int
    tareas_completadas           : int
    tareas_por_usuario_promedio  : float
    productividad_general        : float


@strawberry.type
class DashboardData:
    """Datos completos del dashboard en una sola estructura.
    
    Agrupa toda la información necesaria para mostrar un dashboard
    completo, optimizando las consultas GraphQL al obtener todo
    en una sola petición.
    
    Attributes:
        estadisticas (EstadisticasGenerales) : Métricas generales del sistema.
        tareas_recientes (List[Tarea])       : Últimas tareas creadas.
        usuarios_activos (List[Usuario])     : Usuarios activos en el sistema.
        tareas_urgentes (List[Tarea])        : Tareas pendientes más antiguas.
        
    Example:
        dashboard = DashboardData(
            estadisticas=stats_generales,
            tareas_recientes=ultimas_5_tareas,
            usuarios_activos=usuarios_conectados,
            tareas_urgentes=tareas_atrasadas
        )
        
    Note:
        Esta estructura permite obtener todos los datos del dashboard
        con una sola query GraphQL, evitando múltiples requests HTTP.
    """
    estadisticas      : EstadisticasGenerales
    tareas_recientes  : List[Tarea]
    usuarios_activos  : List[Usuario]
    tareas_urgentes   : List[Tarea]


# Input Types para Mutations
@strawberry.input
class CrearUsuarioInput:
    """Input para crear un nuevo usuario en el sistema.
    
    El sistema core es simple: solo requiere el nombre del usuario.
    Todos los usuarios se crean con rol 'user' por defecto y deben
    configurar su contraseña en el primer login.
    
    Attributes:
        nombre (str): Nombre único del usuario (requerido).
        
    Note:
        - Rol siempre es 'user' por defecto
        - No se requiere contraseña inicial
        - No se maneja email en el core
        - Solo el admin puede crear nuevos usuarios
        
    Example:
        input_usuario = CrearUsuarioInput(
            nombre="juan_perez"
        )
        
    Note:
        El usuario deberá configurar su contraseña al loguearse por primera vez.
    """
    nombre: str


@strawberry.input
class ActualizarUsuarioInput:
    """Input para actualizar un usuario"""
    nombre : Optional[str]  = None
    email  : Optional[str]  = None
    activo : Optional[bool] = None


@strawberry.input
class CrearTareaInput:
    """Input para crear una nueva tarea en el sistema.
    
    Attributes:
        nombre (str)              : Título de la tarea (requerido).
        descripcion (str)         : Descripción detallada de la tarea (requerido).
        usuarios_asignados (Optional[List[str]]) : Lista de nombres de usuarios a asignar.
        
    Note:
        Los campos coinciden con el constructor de core.tarea.Tarea:
        - nombre: str
        - descripcion: str  
        - usuarios_asignados: Optional[List[str]] = None
        
    Example:
        input_tarea = CrearTareaInput(
            nombre="Desarrollar feature X",
            descripcion="Implementar nueva funcionalidad del módulo",
            usuarios_asignados=["juan_perez", "maria_lopez"]
        )
    """
    nombre              : str
    descripcion         : str
    usuarios_asignados  : Optional[List[str]] = None


@strawberry.input
class ActualizarTareaInput:
    """Input para actualizar una tarea existente.
    
    Permite modificar los campos de una tarea existente de manera parcial.
    """
    nombre       : Optional[str]         = None
    descripcion  : Optional[str]         = None
    estado       : Optional[EstadoTarea] = None


@strawberry.input
class AsignarUsuarioTareaInput:
    """Input para asignar/desasignar usuarios a tareas.
    
    Attributes:
        tarea_nombre   : Nombre de la tarea (pk).
        usuario_nombre : Nombre del usuario (pk).
        
    Note:
        Usa nombres como primary keys para coincidir con core.
    """
    tarea_nombre   : str
    usuario_nombre : str

@strawberry.input
class AgregarComentarioInput:
    """Input para agregar comentario a tarea.
    
    Attributes:
        tarea_nombre : Nombre de la tarea (pk).
        texto        : Contenido del comentario.
        
    Note:
        El autor se obtiene del usuario autenticado.
        Usa nombre de tarea como pk para coincidir con core.
    """
    tarea_nombre : str
    texto        : str


@strawberry.input
class FiltroTareas:
    """Filtros para búsqueda de tareas.
    
    Attributes:
        estado         : Filtrar por estado de la tarea.
        usuario_nombre : Filtrar tareas asignadas a usuario específico.
        textoBusqueda  : Búsqueda en nombre y descripción.
        limite         : Número máximo de resultados.
        offset         : Saltar resultados para paginación.
    """
    estado          : Optional[EstadoTarea] = None
    usuario_nombre  : Optional[str]         = None
    textoBusqueda   : Optional[str]         = None
    limite          : int                   = 50
    offset          : int                   = 0


@strawberry.input
class FiltroUsuarios:
    """Filtros para búsqueda de usuarios"""
    rol           : Optional[RolUsuario]  = None
    activo        : Optional[bool]        = None
    textoBusqueda : Optional[str]         = None
    limite        : int                   = 50
    offset        : int                   = 0

# Response Types
@strawberry.type
class AuthPayload:
    """Respuesta de autenticación"""
    access_token  : str
    refresh_token : str
    token_type    : str = "Bearer"
    expires_in    : int
    usuario       : Usuario


@strawberry.type
class MutationResponse:
    """Respuesta genérica para mutations"""
    success : bool
    message : str
    code    : Optional[str] = None


@strawberry.type
class UsuarioMutationResponse(MutationResponse):
    """Respuesta para mutations de usuario"""
    usuario : Optional[Usuario] = None


@strawberry.type
class TareaMutationResponse(MutationResponse):
    """Respuesta para mutations de tarea"""
    tarea : Optional[Tarea] = None


@strawberry.input
class LoginInput:
    """Input para login"""
    username : str
    password : str