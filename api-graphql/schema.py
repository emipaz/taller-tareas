"""
Schema GraphQL principal para el Sistema de Gestión de Tareas.

Este módulo define el schema completo de GraphQL incluyendo todas las queries,
mutations y subscriptions disponibles. Utiliza Strawberry GraphQL para crear
un schema tipado y moderno que se integra con FastAPI.

Clases principales:
    Query: Define todas las operaciones de consulta (lectura).
    Mutation: Define todas las operaciones de modificación (escritura).
    
Funciones:
    get_context: Crea contexto para operaciones GraphQL.
    
Variables:
    schema: Instancia principal del schema GraphQL.
    EXAMPLE_QUERIES: Diccionario con queries de ejemplo para documentación.

Example:
    from api_graphql.schema import schema
    
    # Usar con FastAPI
    app = FastAPI()
    graphql_router = GraphQLRouter(schema)
    app.include_router(graphql_router, prefix="/graphql")
    
Note:
    Todas las queries y mutations requieren autenticación JWT excepto
    el health check y las operaciones de login.
"""

try:
    import strawberry
    from typing import List, Optional
    from strawberry.types import Info
except ImportError:
    # Para desarrollo sin strawberry instalado
    pass

from graphql_types import (
    Usuario, 
    Tarea, 
    EstadisticasGenerales, 
    DashboardData,
    AuthPayload, 
    UsuarioMutationResponse, 
    TareaMutationResponse,
    CrearUsuarioInput, 
    ActualizarUsuarioInput, 
    CrearTareaInput,
    ActualizarTareaInput, 
    AsignarUsuarioTareaInput, 
    AgregarComentarioInput,
    FiltroTareas, 
    FiltroUsuarios, 
    LoginInput, 
    EstadoTarea
)

from resolvers import resolver
from auth import IsAuthenticated, IsAdmin


@strawberry.type
class Query:
    """Operaciones de consulta (lectura) de la API GraphQL.
    
    Esta clase define todos los endpoints de consulta disponibles en la API.
    Todas las operaciones requieren autenticación JWT excepto health().
    
    Methods:
        usuarios                : Obtiene lista de usuarios con filtros opcionales.
        usuario                 : Obtiene un usuario específico por ID.
        tareas                  : Obtiene lista de tareas con filtros opcionales.
        tarea                   : Obtiene una tarea específica por ID.
        estadisticas_generales  : Obtiene métricas generales del sistema.
        dashboard               : Obtiene datos completos del dashboard en una query.
        health                  : Health check sin autenticación requerida.
        
    Example:
        # Query básica
        query {
            usuarios {
                nombre
                rol
            }
        }
        
        # Query con filtros
        query {
            tareas(filtro: {estado: PENDIENTE, limite: 10}) {
                id
                nombre
                usuarios_asignados { nombre }
            }
        }
    """
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def usuarios(
        self, 
        filtro : Optional[FiltroUsuarios] = None,
        info   : Info                     = strawberry.UNSET
    ) -> List[Usuario]:
        """Obtiene lista de usuarios del sistema con filtros opcionales.
        
        Args:
            filtro (Optional[FiltroUsuarios]) : Filtros de búsqueda y paginación.
            
                - rol             : Filtrar por rol (ADMIN/USUARIO)
                - activo          : Filtrar por estado activo
                - texto_busqueda  : Búsqueda en nombre o email
                - limite          : Número máximo de resultados (default: 50)
                - offset          : Saltar resultados para paginación
            
            info (Info): Contexto de GraphQL con request y usuario actual.
            
        Returns:
            List[Usuario]: Lista de usuarios que cumplen los criterios.
            
        Raises:
            Exception: Si el usuario no está autenticado.
            
        Example:
            query {
                usuarios(filtro: {rol: ADMIN, activo: true}) {
                    nombre
                    rol
                    email
                    tiene_password
                    estadisticas {
                        tareas_asignadas
                        productividad
                    }
                }
            }
        """
        return resolver.get_usuarios(filtro, info)
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def usuario(
        self, 
        nombre : str,
        info   : Info = strawberry.UNSET
    ) -> Optional[Usuario]:
        """Obtiene un usuario específico por nombre.
        
        Args:
            nombre (str)  : Nombre único del usuario a buscar (pk).
            info (Info)   : Contexto de GraphQL con request y usuario actual.
            
        Returns:
            Optional[Usuario]: El usuario solicitado o None si no se encuentra.
            
        Raises:
            Exception: Si el usuario no está autenticado o no tiene permisos.
            
        Example:
            query {
                usuario(nombre: "juan_perez") {
                    nombre
                    rol
                    email
                    tiene_password
                    estadisticas {
                        tareas_asignadas
                        productividad
                    }
                    tareas_asignadas {
                        nombre
                        estado
                        descripcion
                    }
                }
            }
            
        Note:
            Los usuarios regulares solo pueden acceder a su propia información,
            mientras que los administradores pueden consultar cualquier usuario.
        """
        return resolver.get_usuario(nombre, info)
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def tareas(
        self, 
        filtro   : Optional[FiltroTareas] = None,
        info     : Info                   = strawberry.UNSET
    ) -> List[Tarea]:
        """Obtiene lista de tareas con filtros y paginación.
        
        Args:
            filtro (Optional[FiltroTareas]) : Filtros de búsqueda y paginación.
                - estado                    : Filtrar por estado (PENDIENTE/FINALIZADA)
                - usuario_nombre            : Filtrar tareas asignadas a usuario específico
                - texto_busqueda            : Búsqueda en nombre o descripción
                - limite                    : Número máximo de resultados (default: 50)
                - offset                    : Saltar resultados para paginación
            info (Info)                      : Contexto de GraphQL con request y usuario actual.
            
        Returns:
            List[Tarea]: Lista de tareas que cumplen los criterios.
            
        Example:
            query {
                tareas(filtro: {
                    estado: PENDIENTE,
                    texto_busqueda: "importante"
                }) {
                    nombre
                    descripcion
                    estado
                    fecha_creacion
                    usuarios_asignados
                    comentarios {
                        texto
                        autor
                        fecha
                    }
                    esta_finalizada
                }
                }
            }
            
        Note:
            Los filtros se combinan con operador AND. Para búsquedas
            más complejas, use el filtro texto_busqueda que busca
            en nombre y descripción simultáneamente.
        """
        return resolver.get_tareas(filtro, info)
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def tarea(
        self,
        nombre: str,
        info  : Info = strawberry.UNSET
    ) -> Optional[Tarea]:
        """Obtiene una tarea específica por nombre.
        
        Args:
            nombre (str) : Nombre único de la tarea a buscar (pk).
            info (Info)  : Contexto de GraphQL con request y usuario actual.
            
        Returns:
            Optional[Tarea]: La tarea solicitada o None si no se encuentra
            o el usuario no tiene permisos para verla.
            
        Example:
            query {
                tarea(nombre: "Implementar API GraphQL") {
                    nombre
                    descripcion
                    estado
                    fecha_creacion
                    usuarios_asignados
                    comentarios {
                        texto
                        autor
                        fecha
                    }
                    esta_finalizada
                }
            }
            
        Note:
            Los usuarios solo pueden ver tareas en las que están asignados
            o que han creado, excepto los administradores que pueden ver
            todas las tareas.
        """
        return resolver.get_tarea(nombre, info)
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def estadisticas_generales(
        self,
        info: Info = strawberry.UNSET
    ) -> EstadisticasGenerales:
        """Obtiene estadísticas generales completas del sistema.
        
        Args:
            info (Info): Contexto de GraphQL con request y usuario actual.
            
        Returns:
            EstadisticasGenerales   : Métricas del sistema incluyendo :

                - total_usuarios        : Número total de usuarios registrados
                - total_tareas          : Número total de tareas en el sistema
                - tareas_por_estado     : Distribución de tareas por estado
                - usuarios_activos      : Usuarios con actividad reciente
                - productividad_general : Métrica de eficiencia del equipo
                - tendencias_semanales  : Datos para gráficos de tendencias
                
        Example:
            query {
                estadisticas_generales {
                    total_usuarios
                    total_tareas
                    tareas_por_estado {
                        pendientes
                        en_progreso
                        finalizadas
                    }
                    productividad_general
                    usuarios_activos
                    tendencias_semanales {
                        fecha
                        tareas_creadas
                        tareas_completadas
                    }
                }
            }
            
        Note:
            Solo usuarios con rol de administrador pueden acceder a
            estadísticas completas del sistema. Los usuarios regulares
            recibirán estadísticas limitadas.
        """
        return resolver.get_estadisticas_generales(info)
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def dashboard(
        self,
        info: Info = strawberry.UNSET
    ) -> DashboardData:
        """Obtiene todos los datos necesarios para el dashboard en una sola query.
        
        Esta es una de las principales ventajas de GraphQL: obtener datos
        complejos y relacionados en una sola petición HTTP, evitando el
        problema N+1 y optimizando la eficiencia de red.
        
        Args:
            info (Info): Contexto de GraphQL con request y usuario actual.
            
        Returns:
            DashboardData: Objeto que contiene :

                - estadisticas      : Métricas generales del sistema
                - tareas_recientes  : Últimas 5 tareas creadas
                - usuarios_activos  : Usuarios con sesión activa
                - tareas_urgentes   : Tareas pendientes más antiguas
                
        Raises:
            Exception: Si el usuario no está autenticado.
            
        Example:
            query {
                dashboard {
                    estadisticas {
                        total_usuarios
                        total_tareas
                        productividad_general
                    }
                    tareas_recientes {
                        id
                        nombre
                        estado
                        usuarios_asignados { nombre }
                    }
                    usuarios_activos {
                        nombre
                        estadisticas { productividad }
                    }
                }
            }
            
        Note:
            Esta query es más eficiente que hacer múltiples requests
            REST separadas para obtener los mismos datos.
        """
        return resolver.get_dashboard(info)
    
    @strawberry.field
    def health(self) -> str:
        """
        Health check para verificar que la API está funcionando.
        
        Returns:
            Mensaje de estado
        """
        return "GraphQL API is running! 🚀"


@strawberry.type
class Mutation:
    """Mutations GraphQL para operaciones de escritura en el sistema.
    
    Esta clase contiene todas las mutaciones disponibles para modificar
    datos en el sistema, incluyendo autenticación, creación de usuarios,
    tareas y actualizaciones de estado.
    
    Note:
        Las mutaciones requieren autenticación excepto el login.
        Algunas operaciones requieren permisos de administrador.
    """
    
    @strawberry.field
    def login(self, input: LoginInput) -> AuthPayload:
        """Autentica un usuario en el sistema.
        
        Args:
            input (LoginInput): Credenciales de autenticación conteniendo:
                
                - username : Nombre de usuario o email
                - password : Contraseña del usuario
                
        Returns:
            AuthPayload: Resultado de autenticación conteniendo:
                
                - success        : Si la autenticación fue exitosa
                - message        : Mensaje descriptivo del resultado
                - access_token   : JWT token para acceso a la API
                - refresh_token  : Token para renovar el acceso
                - user           : Datos del usuario autenticado
                
        Raises:
            ValueError: Si las credenciales son inválidas.
            
        Example:
            mutation {
                login(input: {
                    username: "admin@example.com",
                    password: "password123"
                }) {
                    success
                    message
                    access_token
                    user {
                        id
                        nombre
                        email
                        rol
                    }
                }
            }
            
        Note:
            Esta es la única mutación que no requiere autenticación previa.
            El token debe incluirse en headers para futuras requests.
        """
        return resolver.login(input)
    
    @strawberry.field(permission_classes=[IsAdmin])
    def crear_usuario(
        self,
        input : CrearUsuarioInput,
        info  : Info = strawberry.UNSET
    ) -> UsuarioMutationResponse:
        """Crea un nuevo usuario en el sistema (solo administradores).
        
        El sistema core es simple: solo requiere el nombre del usuario.
        Todos los usuarios se crean con rol 'user' por defecto.
        
        Args:
            input (CrearUsuarioInput): Datos del nuevo usuario conteniendo:
                
                - nombre : Nombre único del usuario (requerido)
            
            info (Info) : Contexto de GraphQL con usuario actual.
                
        Returns:
            UsuarioMutationResponse: Resultado de la operación conteniendo:
                
                - success : Si la creación fue exitosa
                - message : Mensaje descriptivo
                - usuario : Datos del usuario creado (si exitoso)
                - code    : Código de error (si falla)
                
        Note:
            - Solo administradores pueden crear usuarios
            - Rol siempre es 'user' por defecto
            - No se requiere contraseña inicial
            - No se maneja email en el sistema core
            - El usuario debe configurar su contraseña en el primer login
                
        Raises:
            PermissionDenied : Si el usuario no es administrador.
            
        Example:
            crear_usuario(input: {
                nombre: "nuevo_usuario"
            }) {
                success
                message
                usuario {
                    id
                    nombre
                    rol
                    tiene_password
                }
            }
            
        Example:
            mutation {
                crear_usuario(input: {
                    nombre: "Juan Pérez",
                    email: "juan@example.com",
                    username: "jperez",
                    password: "password123",
                    rol: USUARIO
                }) {
                    success
                    message
                    usuario {
                        id
                        nombre
                        email
                        rol
                        fecha_creacion
                    }
                    errors
                }
            }
            
        Note:
            - Solo usuarios con rol ADMIN pueden crear otros usuarios
            - El email y username deben ser únicos en el sistema
            - La contraseña será automáticamente hasheada
        """
        return resolver.crear_usuario(input, info)
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def crear_tarea(
        self,
        input: CrearTareaInput,
        info: Info = strawberry.UNSET
    ) -> TareaMutationResponse:
        """Crea una nueva tarea en el sistema.
        
        Args:
            input (CrearTareaInput): Datos de la nueva tarea conteniendo:
                - nombre: Título de la tarea
                - descripcion: Descripción detallada (requerido)
                - usuarios_asignados: Lista de nombres de usuarios asignados
            info (Info): Contexto de GraphQL con usuario actual.
                
        Returns:
            TareaMutationResponse: Resultado de la operación conteniendo:
                - success: Si la creación fue exitosa
                - message: Mensaje descriptivo
                - tarea: Datos de la tarea creada (si exitoso)
                - errors: Lista de errores de validación (si falla)
                
        Example:
            mutation {
                crear_tarea(input: {
                    nombre: "Implementar nueva funcionalidad",
                    descripcion: "Desarrollar el módulo de reportes",
                    usuarios_asignados: ["juan_perez", "maria_lopez"]
                }) {
                    success
                    message
                    tarea {
                        nombre
                        descripcion
                        estado
                        usuarios_asignados
                        comentarios {
                            texto
                            autor
                        }
                        comentarios {
                            texto
                            autor
                        }
                    }
                    errors
                }
            }
            
        Note:
            - El estado inicial de la tarea será PENDIENTE
            - El creador de la tarea se asigna automáticamente
            - Los usuarios asignados deben existir en el sistema
        """
        return resolver.crear_tarea(input, info)
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def actualizar_estado_tarea(
        self,
        tarea_nombre: str,
        estado: EstadoTarea,
        info: Info = strawberry.UNSET
    ) -> TareaMutationResponse:
        """Actualiza el estado de una tarea existente.
        
        Args:
            tarea_nombre (str): Nombre único de la tarea a actualizar (pk).
            estado (EstadoTarea): Nuevo estado para la tarea.
                - PENDIENTE: Tarea creada pero sin iniciar
                - FINALIZADA: Tarea completada
            info (Info): Contexto de GraphQL con usuario actual.
                
        Returns:
            TareaMutationResponse: Resultado de la operación conteniendo:
                - success: Si la actualización fue exitosa
                - message: Mensaje descriptivo
                - tarea: Datos de la tarea actualizada (si exitoso)
                - errors: Lista de errores (si falla)
                
        Example:
            mutation {
                actualizar_estado_tarea(
                    tarea_nombre: "Implementar API GraphQL",
                    estado: FINALIZADA
                ) {
                    success
                    message
                    tarea {
                        id
                        nombre
                        estado
                        fecha_actualizacion
                    }
                }
            }
            
        Note:
            - Solo usuarios asignados a la tarea o administradores pueden
              actualizar el estado
            - El cambio de estado se registra en el historial de la tarea
        """
        return resolver.actualizar_estado_tarea(tarea_nombre, estado, info)
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def asignar_usuario_tarea(
        self,
        input: AsignarUsuarioTareaInput,
        info: Info = strawberry.UNSET
    ) -> TareaMutationResponse:
        """Asigna un usuario adicional a una tarea existente.
        
        Args:
            input (AsignarUsuarioTareaInput): Datos para la asignación conteniendo:
                
                - tarea_nombre   : Nombre de la tarea a la que asignar el usuario
                - usuario_nombre : Nombre del usuario a asignar
            
            info (Info): Contexto de GraphQL con usuario actual.
                
        Returns:
            TareaMutationResponse: Resultado de la operación conteniendo:
                
                - success   : Si la asignación fue exitosa
                - message   : Mensaje descriptivo
                - tarea     : Datos de la tarea con usuarios actualizados
                - errors    : Lista de errores (si falla)
                
        Example:
            mutation {
                asignar_usuario_tarea(input: {
                    tarea_nombre: "Implementar API GraphQL",
                    usuario_nombre: "juan_perez"
                }) {
                    success
                    message
                    tarea {
                        nombre
                        descripcion
                        usuarios_asignados
                    }
                    errors
                }
            }
            
        Note:
            - Solo creadores de tareas y administradores pueden asignar usuarios
            - El usuario asignado recibirá una notificación si está habilitada
            - No se puede asignar el mismo usuario múltiples veces
        """
        return resolver.asignar_usuario_tarea(input, info)


# Crear el schema principal de GraphQL
schema = strawberry.Schema(
    query    = Query,
    mutation = Mutation,
    # extensions=[
    #     strawberry.extensions.QueryDepthLimiter(max_depth=10),
    #     strawberry.extensions.ValidationCache(),
    # ]
)

"""Schema principal de GraphQL para el sistema de gestión de tareas.

Este schema define:
- Query        : Operaciones de lectura (usuarios, tareas, dashboard, estadísticas)
- Mutation     : Operaciones de escritura (login, crear usuarios/tareas, actualizar estados)
- Extensiones  : Limitación de profundidad y caché de validación (comentadas)

Note:
    Las extensiones están comentadas para desarrollo. En producción se
    recomienda habilitar QueryDepthLimiter para prevenir queries maliciosos.
"""


# Función para obtener el contexto de GraphQL
def get_context(request=None):
    """Crea el contexto para operaciones GraphQL.
    
    Esta función prepara el contexto que estará disponible en todos
    los resolvers a través del parámetro 'info'.
    
    Args:
        request: Instancia de Request de FastAPI conteniendo:
            - Headers con tokens de autenticación
            - Datos de sesión del usuario
            - Información de la petición HTTP
            
    Returns:
        dict: Diccionario de contexto conteniendo:
            - request: Objeto request de FastAPI para acceso a headers,
              cookies y datos de autenticación
              
    Example:
        En un resolver:
        def get_usuario(self, info: Info) -> Usuario:
            request = info.context["request"]
            auth_header = request.headers.get("Authorization")
            
    Note:
        Este contexto es inyectado automáticamente por el middleware
        de GraphQL y está disponible en todos los resolvers.
    """
    return {
        "request": request,
    }


# Queries de ejemplo para documentación
# Estas pueden ser usadas en herramientas como GraphiQL o Apollo Studio
# Sin objetos de ja
EXAMPLE_QUERIES = {
    "health_check": """
        query HealthCheck {
            health
        }
    """,
    
    "login": """
        mutation Login($username: String!, $password: String!) {
            login(input: {username: $username, password: $password}) {
                access_token
                refresh_token
                expires_in
                usuario {
                    nombre
                    rol
                    tiene_password
                }
            }
        }
    """,
    
    "dashboard": """
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
                    nombre
                    descripcion
                    estado
                    fecha_creacion
                    usuarios_asignados
                }
                usuarios_activos {
                    nombre
                    rol
                    tiene_password
                    activo
                }
            }
        }
    """,
    
    "usuarios_con_tareas": """
        query UsuariosConTareas {
            usuarios {
                nombre
                rol
                tiene_password
                email
                tareas_asignadas {
                    nombre
                    descripcion
                    estado
                    fecha_creacion
                }
                estadisticas {
                    tareas_asignadas
                    tareas_completadas
                    tareas_pendientes
                    productividad
                }
            }
        }
    """,
    
    "tareas_filtradas": """
        query TareasFiltradas($estado: EstadoTarea, $limite: Int) {
            tareas(filtro: {estado: $estado, limite: $limite}) {
                nombre
                descripcion
                estado
                fecha_creacion
                usuarios_asignados
                comentarios {
                    texto
                    autor
                    fecha
                }
                esta_finalizada
            }
        }
    """,
    
    "crear_tarea": """
        mutation CrearTarea($input: CrearTareaInput!) {
            crear_tarea(input: $input) {
                success
                message
                tarea {
                    nombre
                    descripcion
                    estado
                    fecha_creacion
                    usuarios_asignados
                    comentarios {
                        texto
                        autor
                        fecha
                    }
                }
            }
        }
    """,
    
    "actualizar_tarea": """
        mutation ActualizarTarea($tareaNombre: String!, $estado: EstadoTarea!) {
            actualizar_estado_tarea(tarea_nombre: $tareaNombre, estado: $estado) {
                success
                message
                tarea {
                    nombre
                    descripcion
                    estado
                    fecha_creacion
                    usuarios_asignados
                    esta_finalizada
                }
            }
        }
    """,
}