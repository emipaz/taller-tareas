"""
Cliente GraphQL para el Sistema de Gestión de Tareas

Cliente Python para consumir la API GraphQL de forma sencilla,
con métodos de alto nivel para todas las operaciones disponibles.
"""

import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Usuario:
    """Representación local de un usuario del sistema.
    
    Esta clase dataclass encapsula los datos de un usuario
    obtenidos desde la API GraphQL para facilitar su uso
    en aplicaciones cliente.
    
    Attributes:
        id (str)              : Identificador único del usuario
        nombre (str)          : Nombre completo del usuario
        email (Optional[str]) : Email del usuario (puede ser None)
        rol (str)             : Rol del usuario ("admin" o "usuario")
        fecha_registro (str)  : Fecha de registro en formato ISO
        activo (bool)         : Si el usuario está activo en el sistema
        
    Example:
        usuario = Usuario(
            id="123",
            nombre="Juan Pérez",
            email="juan@example.com",
            rol="usuario",
            fecha_registro="2024-01-01T00:00:00Z",
            activo=True
        )
    """
    id              : str
    nombre          : str
    email           : Optional[str]
    rol             : str
    fecha_registro  : str
    activo          : bool


@dataclass
class Tarea:
    """Representación local de una tarea del sistema.
    
    Esta clase dataclass encapsula los datos de una tarea
    obtenidos desde la API GraphQL, incluyendo usuarios asignados
    y cálculos derivados como duración.
    
    Attributes:
        id (str)                           : Identificador único de la tarea
        nombre (str)                       : Título o nombre de la tarea
        descripcion (str)                  : Descripción detallada de la tarea
        estado (str)                       : Estado actual ("PENDIENTE", "EN_PROGRESO", "FINALIZADA")
        fecha_creacion (str)               : Fecha de creación en formato ISO
        fecha_finalizacion (Optional[str]) : Fecha de finalización (si aplica)
        usuarios_asignados (List[Usuario]) : Lista de usuarios asignados
        duracion_dias (Optional[int])      : Duración calculada en días
        
    Example:
        tarea = Tarea(
            id="456",
            nombre="Implementar nueva funcionalidad",
            descripcion="Desarrollar el módulo de reportes",
            estado="EN_PROGRESO",
            fecha_creacion="2024-01-01T00:00:00Z",
            usuarios_asignados=[usuario1, usuario2]
        )
    """
    id                   : str
    nombre               : str
    descripcion          : str
    estado               : str
    fecha_creacion       : str
    fecha_finalizacion   : Optional[str] = None
    usuarios_asignados   : List[Usuario] = None
    duracion_dias        : Optional[int] = None
    
    def __post_init__(self):
        """Inicializa la lista de usuarios asignados si no se proporciona."""
        if self.usuarios_asignados is None:
            self.usuarios_asignados = []


class GraphQLError(Exception):
    """Excepción específica para errores de GraphQL.
    
    Esta excepción encapsula los errores devueltos por la API GraphQL,
    incluyendo tanto el mensaje principal como los errores detallados.
    
    Attributes:
        message (str)       : Mensaje principal del error
        errors (List[Dict]) : Lista detallada de errores de GraphQL
        
    Example:
        try:
            client.get_usuarios()
        except GraphQLError as e:
            print(f"Error GraphQL: {e}")
            for error in e.errors:
                print(f"Detalle: {error.get('message')}")
                
    Note:
        Los errores de GraphQL pueden incluir información detallada
        sobre validación, autenticación, o errores de lógica de negocio.
    """
    def __init__(self, message: str, errors: List[Dict] = None):
        """Inicializa la excepción con mensaje y errores detallados.
        
        Args:
            message (str)                 : Mensaje principal del error
            errors (List[Dict], optional) : Lista de errores GraphQL detallados
        """
        super().__init__(message)
        self.errors = errors or []


class TaskGraphQLClient:
    """Cliente GraphQL para el Sistema de Gestión de Tareas.
    
    Esta clase proporciona una interfaz Python de alto nivel para
    interactuar con la API GraphQL del sistema de gestión de tareas.
    Incluye métodos para autenticación, gestión de usuarios y tareas.
    
    Attributes:
        base_url (str)                : URL base del servidor GraphQL
        graphql_url (str)             : URL completa del endpoint GraphQL
        headers (dict)                : Headers HTTP por defecto
        access_token (Optional[str])  : Token JWT de acceso actual
        refresh_token (Optional[str]) : Token JWT de refresh  
        current_user (Optional[dict]) : Datos del usuario autenticado
        
    Example:
        # Inicializar cliente
        client = TaskGraphQLClient("http://localhost:4000")
        
        # Autenticarse
        client.login("admin", "password123")
        
        # Obtener datos
        usuarios = client.get_usuarios()
        tareas = client.get_tareas()
        
    Note:
        El cliente maneja automáticamente la autenticación JWT
        y la incluye en todas las requests que lo requieran.
    """
    
    def __init__(self, base_url: str = "http://localhost:4000"):
        """Inicializa el cliente GraphQL.
        
        Args:
            base_url (str) : URL base del servidor GraphQL.
                Default es "http://localhost:4000" para desarrollo local.
                
        Example:
            # Cliente local
            client = TaskGraphQLClient()
            
            # Cliente en servidor específico
            client = TaskGraphQLClient("https://api.midominio.com")
        """
        self.base_url    = base_url
        self.graphql_url = f"{base_url}/graphql"
        self.headers     = {
            'Content-Type': 'application/json',
            'Accept'      : 'application/json'
        }
        self.access_token  = None
        self.refresh_token = None
        self.current_user  = None
    
    def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Ejecuta una query o mutation GraphQL en el servidor.
        
        Este es el método base que maneja toda la comunicación HTTP
        con el servidor GraphQL, incluyendo autenticación automática.
        
        Args:
            query (str)                 : Query o mutation GraphQL en formato string
            variables (Optional[Dict])  : Diccionario de variables para la query
            
        Returns:
            Dict: Respuesta JSON del servidor conteniendo:
                - data: Datos solicitados (si exitoso)
                - errors: Lista de errores GraphQL (si los hay)
                
        Raises:
            GraphQLError: Si hay errores en la respuesta GraphQL
            requests.RequestException: Si falla la comunicación HTTP
            
        Example:
            query = '''
                query GetUsuarios($limite: Int) {
                    usuarios(filtro: {limite: $limite}) {
                        id
                        nombre
                    }
                }
            '''
            resultado = client._execute_query(query, {"limite": 10})
            
        Note:
            - Método privado, usar los métodos públicos específicos
            - Maneja automáticamente la inclusión del token JWT
            - Convierte errores HTTP y GraphQL en excepciones apropiadas
        """
        payload = {
            'query'    : query,
            'variables': variables or {}
        }
        
        try:
            response = requests.post(
                self.graphql_url,
                json    = payload,
                headers = self.headers,
                timeout = 30
            )
            
            if response.status_code != 200:
                raise GraphQLError(
                    f"HTTP {response.status_code}: {response.text}"
                )
            
            result = response.json()
            
            if 'errors' in result:
                error_messages = [error.get('message', 'Unknown error') 
                                for error in result['errors']]
                raise GraphQLError(
                    f"GraphQL errors: {'; '.join(error_messages)}",
                    result['errors']
                )
            
            return result.get('data', {})
            
        except requests.RequestException as e:
            raise GraphQLError(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise GraphQLError(f"Invalid JSON response: {str(e)}")
    
    def _set_auth_token(self, token: str):
        """Configurar token de autenticación"""
        self.access_token = token
        self.headers['Authorization'] = f'Bearer {token}'
    
    # =====================
    # AUTENTICACIÓN
    # =====================
    
    def login(self, username: str, password: str) -> Dict:
        """Autentica un usuario y obtiene tokens de acceso.
        
        Ejecuta la mutation de login y almacena automáticamente
        los tokens y datos del usuario para uso en futuras requests.
        
        Args:
            username (str)  : Nombre de usuario o email
            password (str)  : Contraseña del usuario
            
        Returns:
            Dict: Datos completos de autenticación conteniendo:
                - access_token   : Token JWT para acceso a la API
                - refresh_token  : Token para renovar el acceso
                - expires_in     : Tiempo de expiración en segundos
                - usuario        : Datos del usuario autenticado
                
        Raises:
            GraphQLError: Si las credenciales son inválidas
            
        Example:
            try:
                auth_data = client.login("admin", "password123")
                print(f"Bienvenido {auth_data['usuario']['nombre']}")
                
                # Ahora se pueden hacer requests autenticadas
                usuarios = client.get_usuarios()
            except GraphQLError as e:
                print(f"Error de login: {e}")
                
        Note:
            - Los tokens se almacenan automáticamente en el cliente
            - Futuras requests incluirán automáticamente el token
            - El usuario actual se guarda en client.current_user
        """
        mutation = """
            mutation Login($username: String!, $password: String!) {
                login(input: {username: $username, password: $password}) {
                    access_token
                    refresh_token
                    expires_in
                    usuario {
                        id
                        nombre
                        email
                        rol
                        fecha_registro
                        activo
                    }
                }
            }
        """
        
        variables = {'username': username, 'password': password}
        result    = self._execute_query(mutation, variables)
        
        auth_data          = result['login']
        self.access_token  = auth_data['access_token']
        self.refresh_token = auth_data['refresh_token']
        self.current_user = Usuario(**auth_data['usuario'])
        
        # Configurar header de autorización
        self._set_auth_token(self.access_token)
        
        return auth_data
    
    def logout(self):
        """Cerrar sesión y limpiar tokens"""
        self.access_token  = None
        self.refresh_token = None
        self.current_user  = None
        self.headers.pop('Authorization', None)
    
    # =====================
    # HEALTH CHECK
    # =====================
    
    def health_check(self) -> str:
        """Verificar estado de la API"""
        query   = "query { health }"
        result  = self._execute_query(query)
        return result['health']
    
    # =====================
    # USUARIOS
    # =====================
    
    def get_usuarios(self, 
                    rol            : Optional[str]  = None,
                    activo         : Optional[bool] = None,
                    texto_busqueda : Optional[str]  = None,
                    limite         : int            = 50,
                    offset         : int            = 0) -> List[Usuario]:
        """
        Obtener lista de usuarios con filtros.
        
        Args:
            rol            : Filtrar por rol (admin/usuario)
            activo         : Filtrar por estado activo
            texto_busqueda : Buscar en nombre o email
            limite         : Número máximo de resultados
            offset         : Saltar resultados
            
        Returns:
            List[Usuario]: Lista de usuarios
        """
        query = """
            query GetUsuarios($filtro: FiltroUsuarios) {
                usuarios(filtro: $filtro) {
                    id
                    nombre
                    email
                    rol
                    fecha_registro
                    activo
                    estadisticas {
                        tareas_asignadas
                        tareas_completadas
                        productividad
                    }
                }
            }
        """
        
        filtro = {}
        if rol:
            filtro['rol'] = rol.upper()
        if activo is not None:
            filtro['activo'] = activo
        if texto_busqueda:
            filtro['texto_busqueda'] = texto_busqueda
        filtro['limite'] = limite
        filtro['offset'] = offset
        
        variables = {'filtro': filtro} if filtro else None
        result    = self._execute_query(query, variables)
        
        return [Usuario(**user) for user in result['usuarios']]
    
    def get_usuario(self, user_id: str) -> Optional[Usuario]:
        """
        Obtener usuario específico.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Usuario o None si no existe
        """
        query = """
            query GetUsuario($id: String!) {
                usuario(id: $id) {
                    id
                    nombre
                    email
                    rol
                    fecha_registro
                    activo
                    tareas_asignadas {
                        id
                        nombre
                        estado
                    }
                    estadisticas {
                        tareas_asignadas
                        tareas_completadas
                        productividad
                    }
                }
            }
        """
        
        result    = self._execute_query(query, {'id': user_id})
        user_data = result.get('usuario')
        
        return Usuario(**user_data) if user_data else None
    
    def crear_usuario(self, 
                     nombre   : str, 
                     password : str,
                     rol      : str           = "USUARIO",
                     email    : Optional[str] = None) -> Dict:
        """
        Crear nuevo usuario (requiere permisos admin).
        
        Args:
            nombre: Nombre del usuario
            password: Contraseña
            rol: Rol del usuario (ADMIN/USUARIO)
            email: Email opcional
            
        Returns:
            dict: Respuesta de la creación
        """
        mutation = """
            mutation CrearUsuario($input: CrearUsuarioInput!) {
                crear_usuario(input: $input) {
                    success
                    message
                    usuario {
                        id
                        nombre
                        email
                        rol
                        activo
                    }
                }
            }
        """
        
        input_data = {
            'nombre'  : nombre,
            'password': password,
            'rol'     : rol
        }
        if email:
            input_data['email'] = email
        
        result = self._execute_query(mutation, {'input': input_data})
        return result['crear_usuario']
    
    # =====================
    # TAREAS
    # =====================
    
    def get_tareas(self,
                  estado         : Optional[str] = None,
                  usuario_id     : Optional[str] = None,
                  texto_busqueda : Optional[str] = None,
                  fecha_desde    : Optional[str] = None,
                  fecha_hasta    : Optional[str] = None,
                  limite         : int            = 50,
                  offset         : int            = 0) -> List[Tarea]:
        """
        Obtener lista de tareas con filtros.
        
        Args:
            estado           : Filtrar por estado (PENDIENTE/FINALIZADA)
            usuario_id       : Filtrar por usuario asignado
            texto_busqueda   : Buscar en título o descripción
            fecha_desde      : Filtrar desde fecha (ISO string)
            fecha_hasta      : Filtrar hasta fecha (ISO string)
            limite           : Número máximo de resultados
            offset           : Saltar resultados
            
        Returns:
            List[Tarea]: Lista de tareas
        """
        query = """
            query GetTareas($filtro: FiltroTareas) {
                tareas(filtro: $filtro) {
                    id
                    nombre
                    descripcion
                    estado
                    fecha_creacion
                    fecha_finalizacion
                    duracion_dias
                    usuarios_asignados {
                        id
                        nombre
                        rol
                    }
                }
            }
        """
        
        filtro = {}
        if estado:
            filtro['estado'] = estado.upper()
        if usuario_id:
            filtro['usuario_id'] = usuario_id
        if texto_busqueda:
            filtro['texto_busqueda'] = texto_busqueda
        if fecha_desde:
            filtro['fecha_desde'] = fecha_desde
        if fecha_hasta:
            filtro['fecha_hasta'] = fecha_hasta
        filtro['limite'] = limite
        filtro['offset'] = offset
        
        variables = {'filtro': filtro} if filtro else None
        result = self._execute_query(query, variables)
        
        tareas = []
        for tarea_data in result['tareas']:
            usuarios = [Usuario(**u) for u in tarea_data.get('usuarios_asignados', [])]
            tarea = Tarea(
                id                 = tarea_data['id'],
                nombre             = tarea_data['nombre'],
                descripcion        = tarea_data['descripcion'],
                estado             = tarea_data['estado'],
                fecha_creacion     = tarea_data['fecha_creacion'],
                fecha_finalizacion = tarea_data.get('fecha_finalizacion'),
                duracion_dias      = tarea_data.get('duracion_dias'),
                usuarios_asignados = usuarios
            )
            tareas.append(tarea)
        
        return tareas
    
    def get_tarea(self, tarea_id: str) -> Optional[Tarea]:
        """
        Obtener tarea específica.
        
        Args:
            tarea_id: ID de la tarea
            
        Returns:
            Tarea o None si no existe
        """
        query = """
            query GetTarea($id: String!) {
                tarea(id: $id) {
                    id
                    nombre
                    descripcion
                    estado
                    fecha_creacion
                    fecha_finalizacion
                    duracion_dias
                    usuarios_asignados {
                        id
                        nombre
                        email
                        rol
                    }
                    comentarios {
                        id
                        texto
                        autor
                        fecha
                    }
                }
            }
        """
        
        result = self._execute_query(query, {'id': tarea_id})
        tarea_data = result.get('tarea')
        
        if not tarea_data:
            return None
        
        usuarios = [Usuario(**u) for u in tarea_data.get('usuarios_asignados', [])]
        return Tarea(
            id                 = tarea_data['id'],
            nombre             = tarea_data['nombre'],
            descripcion        = tarea_data['descripcion'],
            estado             = tarea_data['estado'],
            fecha_creacion     = tarea_data['fecha_creacion'],
            fecha_finalizacion = tarea_data.get('fecha_finalizacion'),
            duracion_dias      = tarea_data.get('duracion_dias'),
            usuarios_asignados = usuarios
        )
    
    def crear_tarea(self,
                   nombre       : str,
                   descripcion  : str,
                   usuarios_ids : Optional[List[str]] = None) -> Dict:
        """
        Crear nueva tarea.
        
        Args:
            nombre           : Nombre de la tarea
            descripcion      : Descripción de la tarea
            usuarios_ids     : Lista de IDs de usuarios a asignar
            
        Returns:
            dict: Respuesta de la creación
        """
        mutation = """
            mutation CrearTarea($input: CrearTareaInput!) {
                crear_tarea(input: $input) {
                    success
                    message
                    tarea {
                        id
                        nombre
                        descripcion
                        estado
                        fecha_creacion
                        usuarios_asignados {
                            nombre
                        }
                    }
                }
            }
        """
        
        input_data = {
            'nombre'       : nombre,
            'descripcion'  : descripcion,
            'usuarios_ids' : usuarios_ids or []
        }
        
        result = self._execute_query(mutation, {'input': input_data})
        return result['crear_tarea']
    
    def actualizar_estado_tarea(self, tarea_id: str, estado: str) -> Dict:
        """
        Actualizar estado de tarea.
        
        Args:
            tarea_id   : ID de la tarea
            estado     : Nuevo estado (PENDIENTE/FINALIZADA)
            
        Returns:
            dict: Respuesta de la actualización
        """
        mutation = """
            mutation ActualizarEstadoTarea($tareaId: String!, $estado: EstadoTarea!) {
                actualizar_estado_tarea(tarea_id: $tareaId, estado: $estado) {
                    success
                    message
                    tarea {
                        id
                        nombre
                        estado
                        fecha_finalizacion
                        duracion_dias
                    }
                }
            }
        """
        
        variables = {
            'tareaId': tarea_id,
            'estado' : estado.upper()
        }
        
        result = self._execute_query(mutation, variables)
        return result['actualizar_estado_tarea']
    
    def asignar_usuario_tarea(self, tarea_id: str, usuario_id: str) -> Dict:
        """
        Asignar usuario a tarea.
        
        Args:
            tarea_id   : ID de la tarea
            usuario_id : ID del usuario
            
        Returns:
            dict: Respuesta de la asignación
        """
        mutation = """
            mutation AsignarUsuarioTarea($input: AsignarUsuarioTareaInput!) {
                asignar_usuario_tarea(input: $input) {
                    success
                    message
                    tarea {
                        id
                        nombre
                        usuarios_asignados {
                            nombre
                        }
                    }
                }
            }
        """
        
        input_data = {
            'tarea_id'   : tarea_id,
            'usuario_id' : usuario_id
        }
        
        result = self._execute_query(mutation, {'input': input_data})
        return result['asignar_usuario_tarea']
    
    # =====================
    # ESTADÍSTICAS Y DASHBOARD
    # =====================
    
    def get_estadisticas_generales(self) -> Dict:
        """Obtener estadísticas generales del sistema"""
        query = """
            query EstadisticasGenerales {
                estadisticas_generales {
                    total_usuarios
                    usuarios_activos
                    total_tareas
                    tareas_pendientes
                    tareas_completadas
                    tareas_por_usuario_promedio
                    productividad_general
                }
            }
        """
        
        result = self._execute_query(query)
        return result['estadisticas_generales']
    
    def get_dashboard(self) -> Dict:
        """
        Obtener datos completos del dashboard.
        
        Returns:
            dict: Datos del dashboard
        """
        query = """
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
                    tareas_urgentes {
                        id
                        nombre
                        fecha_creacion
                        usuarios_asignados {
                            nombre
                        }
                    }
                }
            }
        """
        
        result = self._execute_query(query)
        return result['dashboard']


# Función de conveniencia para crear cliente
def create_client(base_url: str = "http://localhost:4000") -> TaskGraphQLClient:
    """
    Crear cliente GraphQL configurado.
    
    Args:
        base_url: URL del servidor GraphQL
        
    Returns:
        TaskGraphQLClient: Cliente configurado
    """
    return TaskGraphQLClient(base_url)


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo básico de uso del cliente
    print("🚀 Cliente GraphQL - Sistema de Gestión de Tareas")
    
    # Crear cliente
    client = create_client()
    
    try:
        # Health check
        health = client.health_check()
        print(f"✅ Health check: {health}")
        
        # Login (reemplazar con credenciales reales)
        print("\n🔐 Intentando login...")
        # auth_data = client.login("admin", "admin123")
        # print(f"✅ Login exitoso: {auth_data['usuario']['nombre']}")
        
        print("\n📖 Para usar el cliente:")
        print("1. client = create_client()")
        print("2. client.login('usuario', 'password')")
        print("3. client.get_dashboard()")
        
    except GraphQLError as e:
        print(f"❌ Error GraphQL: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")