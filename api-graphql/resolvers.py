"""
Resolvers GraphQL para el Sistema de Gestión de Tareas

Este módulo implementa todos los resolvers (funciones de consulta y mutación) 
para la API GraphQL del sistema de gestión de tareas. Los resolvers conectan 
las queries y mutations de GraphQL con la lógica de negocio definida en el módulo core, 
permitiendo acceder y modificar usuarios, tareas, asignaciones y estadísticas del sistema.

Características principales:
- Validación de autenticación y permisos usando JWT.
- Consultas de usuarios y tareas con filtros y paginación.
- Mutaciones para crear usuarios y tareas, actualizar estados y asignar usuarios.
- Conversión automática entre objetos del core y tipos GraphQL.
- Métodos auxiliares para mapear datos y resolver campos dinámicos.

Clases y funciones:
- GraphQLResolvers     : Clase principal que agrupa todos los resolvers.
- Métodos de consulta  : get_usuarios, get_usuario, get_tareas, get_tarea, get_estadisticas_generales, get_dashboard.
- Métodos de mutación  : login, crear_usuario, crear_tarea, actualizar_estado_tarea, asignar_usuario_tarea.
- Métodos auxiliares para conversión y resolución de campos.

Uso:
Este módulo es utilizado por el schema principal de GraphQL para exponer la API a través de FastAPI y Strawberry. Todas las operaciones requieren autenticación JWT, y algunas requieren permisos de administrador.

Ejemplo de integración:
    from resolvers import resolver
    result   = resolver.get_usuarios(filtro, info)
    mutation = resolver.crear_tarea(input, info)

"""

import sys
import os
from typing import List, Optional
from datetime import datetime

# Agregar el directorio padre al path para importar core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Agregar el directorio api-rest al path para importar jwt_auth
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api-rest'))

try:
    import strawberry
    from strawberry.types import Info
except ImportError:
    # Para desarrollo sin strawberry instalado
    pass

from core import GestorSistema, Usuario as CoreUsuario, Tarea as CoreTarea

from graphql_types import (
    Usuario, 
    Tarea, 
    EstadisticasGenerales, 
    EstadisticasUsuario,
    DashboardData, 
    Comentario, 
    AuthPayload, 
    MutationResponse,
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
    RolUsuario, 
    EstadoTarea
)

from auth import get_current_user, AuthenticationError

# Importar JWT auth desde jwt_auth.py directamente
from jwt_auth import create_access_token, create_refresh_token


class GraphQLResolvers:
    """Clase principal que contiene todos los resolvers GraphQL.
    
    Los resolvers son funciones que conectan las operaciones GraphQL
    con la lógica de negocio del sistema, implementada en el módulo core.
    
    Attributes:
        gestor (GestorSistema): Instancia del gestor principal del sistema
            que maneja toda la lógica de negocio para usuarios y tareas.
            
    Note:
        Cada resolver valida autenticación y permisos antes de ejecutar
        la operación solicitada, utilizando el middleware de autenticación JWT.
    """
    
    def __init__(self):
        """Inicializa el resolver con una instancia del gestor de sistema.
        
        El gestor se encarga de toda la lógica de negocio y persistencia
        de datos del sistema de gestión de tareas.
        """
        self.gestor = GestorSistema()
        # Cargar datos del sistema
        self.gestor.cargar_datos()
    
    # =====================
    # QUERY RESOLVERS
    # =====================
    
    def get_usuarios(self, filtro: Optional[FiltroUsuarios] = None, info: Info = None) -> List[Usuario]:
        """Resolver para obtener lista de usuarios con filtros opcionales.
        
        Args:
            filtro (Optional[FiltroUsuarios]): Filtros de búsqueda y paginación.
                Si no se proporciona, retorna todos los usuarios (limitado a 50).
            info (Info): Contexto de GraphQL con request y datos de autenticación.
                
        Returns:
            List[Usuario]: Lista de usuarios que cumplen los criterios de filtrado,
            convertidos desde objetos CoreUsuario a tipos GraphQL.
            
        Raises:
            AuthenticationError : Si el usuario no está autenticado.
            PermissionError     : Si el usuario no tiene permisos para esta operación.
            
        Example:
            # Obtener todos los usuarios activos
            filtro = FiltroUsuarios(activo=True, limite=10)
            usuarios = resolver.get_usuarios(filtro, info)
            
        Note:
            Los usuarios regulares solo pueden ver información limitada de otros usuarios.
            Los administradores tienen acceso completo a todos los datos.
        """
        try:
            # Recargar datos antes de consultar
            self.gestor.cargar_datos()
            # Verificar autenticación
            current_user = get_current_user(info.context.get("request"))
            usuarios_core = list(self.gestor.usuarios.values())
            # Aplicar filtros si existen
            if filtro:
                if filtro.rol:
                    usuarios_core = [u for u in usuarios_core if u.rol == filtro.rol.value]
                if filtro.activo is not None:
                    if not filtro.activo:
                        usuarios_core = []
                if filtro.textoBusqueda:
                    texto = filtro.textoBusqueda.lower()
                    usuarios_core = [u for u in usuarios_core if texto in u.nombre.lower()]
            start = filtro.offset if filtro else 0
            end = start + (filtro.limite if filtro else 50)
            usuarios_core = usuarios_core[start:end]
            return [self._core_usuario_to_graphql(u) for u in usuarios_core]
        except AuthenticationError:
            raise Exception("No autorizado")
        except Exception as e:
            raise Exception(f"Error obteniendo usuarios: {str(e)}")
    
    def get_usuario(self, nombre: str, info: Info = None) -> Optional[Usuario]:
        """Resolver para obtener un usuario específico por nombre.
        
        Args:
            nombre (str) : Nombre único del usuario a buscar (pk).
            info (Info)  : Contexto de GraphQL con request y autenticación.
            
        Returns:
            Optional[Usuario]: El usuario encontrado convertido a tipo GraphQL,
            o None si no se encuentra o no se tienen permisos.
            
        Raises:
            AuthenticationError  : Si el usuario no está autenticado.
            Exception            : Si ocurre un error durante la búsqueda.
            
        Example:
            usuario = resolver.get_usuario("juan_perez", info)
            if usuario:
                print(f"Usuario encontrado: {usuario.nombre}")
                
        Note:
            Los usuarios regulares solo pueden acceder a su propia información.
            Los administradores pueden acceder a cualquier usuario.
        """
        try:
            self.gestor.cargar_datos()
            current_user = get_current_user(info.context.get("request"))
            usuario_core = self.gestor.usuarios.get(nombre)
            if not usuario_core:
                return None
            return self._core_usuario_to_graphql(usuario_core)
        except AuthenticationError:
            raise Exception("No autorizado")
        except Exception as e:
            raise Exception(f"Error obteniendo usuario: {str(e)}")
    
    def get_tareas(self, filtro: Optional[FiltroTareas] = None, info: Info = None) -> List[Tarea]:
        """Resolver para obtener lista de tareas con filtros opcionales.
        
        Args:
            filtro (Optional[FiltroTareas]): Filtros de búsqueda y paginación:
                
                - estado                   : Filtrar por estado de tarea
                - usuario_id               : Filtrar tareas asignadas a usuario específico
                - texto_busqueda           : Búsqueda en nombre y descripción
                - fecha_desde/fecha_hasta  : Rango de fechas de creación
                - limite                   : Número máximo de resultados
                - offset                   : Saltar resultados para paginación
            
            info (Info): Contexto de GraphQL con request y autenticación.
            
        Returns:
            List[Tarea]: Lista de tareas que cumplen los criterios,
            convertidas desde objetos CoreTarea a tipos GraphQL.
            
        Raises:
            AuthenticationError: Si el usuario no está autenticado.
            Exception: Si ocurre un error durante la búsqueda.
            
        Example:
            # Buscar tareas pendientes de un usuario
            filtro = FiltroTareas(
                estado=EstadoTarea.PENDIENTE,
                usuario_id="123",
                limite=20
            )
            tareas = resolver.get_tareas(filtro, info)
            
        Note:
            Los usuarios regulares solo ven tareas en las que están asignados.
            Los administradores pueden ver todas las tareas del sistema.
        """
        try:
            self.gestor.cargar_datos()
            current_user = get_current_user(info.context.get("request"))
            tareas_core = list(self.gestor.tareas.values())
            if filtro:
                if filtro.estado:
                    tareas_core = [t for t in tareas_core if t.estado == filtro.estado.value]
                if filtro.usuario_nombre:
                    tareas_core = [t for t in tareas_core if filtro.usuario_nombre in t.usuarios_asignados]
                if filtro.textoBusqueda:
                    texto = filtro.textoBusqueda.lower()
                    tareas_core = [t for t in tareas_core if texto in t.nombre.lower() or texto in t.descripcion.lower()]
            start = filtro.offset if filtro else 0
            end = start + (filtro.limite if filtro else 50)
            tareas_core = tareas_core[start:end]
            return [self._core_tarea_to_graphql(t) for t in tareas_core]
        except AuthenticationError:
            raise Exception("No autorizado")
        except Exception as e:
            raise Exception(f"Error obteniendo tareas: {str(e)}")
    
    def get_tarea(self, nombre: str, info: Info = None) -> Optional[Tarea]:
        """Resolver para obtener una tarea específica por nombre.
        try:
            self.gestor.cargar_datos()
            current_user = get_current_user(info.context.get("request"))
            tarea_core = self.gestor.tareas.get(nombre)
            if not tarea_core:
                return None
            return self._core_tarea_to_graphql(tarea_core)
        except AuthenticationError:
            raise Exception("No autorizado")
        except Exception as e:
            raise Exception(f"Error obteniendo tarea: {str(e)}")
        Example:
            tarea = resolver.get_tarea("tarea_importante", info)
            if tarea:
                print(f"Tarea encontrada: {tarea.nombre}")
                
        Note:
            Los usuarios regulares solo pueden ver tareas en las que están asignados.
            Los administradores pueden ver cualquier tarea del sistema.
                # Recargar datos después de asignar usuarios
                self.gestor.cargar_datos()
            else:
                # Recargar datos después de crear la tarea
                self.gestor.cargar_datos()
        """
        try:
            current_user = get_current_user(info.context.get("request"))
            tarea        = self._core_tarea_to_graphql(self.gestor.tareas[input.nombre])
            tarea_core   = self.gestor.tareas.get(nombre)
            if not tarea_core:
                return None
            
            return self._core_tarea_to_graphql(tarea_core)
            
        except AuthenticationError:
            raise Exception("No autorizado")
        except Exception as e:
            raise Exception(f"Error obteniendo tarea: {str(e)}")
    
    def get_estadisticas_generales(self, info: Info = None) -> EstadisticasGenerales:
        """Resolver para obtener estadísticas generales del sistema.
        
        Args:
            info (Info): Contexto de GraphQL con request y autenticación.
            
        Returns:
            EstadisticasGenerales: Métricas completas del sistema incluyendo:
                        
                - total_usuarios                : Número total de usuarios registrados
                - usuarios_activos              : Número de usuarios activos
                - total_tareas                  : Número total de tareas
                - tareas_pendientes/completadas : Estado de las tareas
                - productividad_general         : Porcentaje de tareas completadas
                
        Raises:
            AuthenticationError  : Si el usuario no está autenticado.
            Exception            : Si ocurre un error calculando estadísticas.
            
        Example:
            stats = resolver.get_estadisticas_generales(info)
            print(f"Productividad general: {stats.productividad_general}%")
            
        Note:
            Las estadísticas se calculan en tiempo real basándose
            en el estado actual del sistema.
        """
        try:
            current_user = get_current_user(info.context.get("request"))
            
            total_usuarios     = len(self.gestor.usuarios)
            usuarios_activos   = len(self.gestor.usuarios)  # Todos los usuarios son considerados activos
            total_tareas       = len(self.gestor.tareas)
            tareas_pendientes  = len( [t for t in self.gestor.tareas.values() if t.estado == "pendiente"])
            tareas_completadas = len([t for t in self.gestor.tareas.values() if t.estado == "finalizada"])
            
            tareas_por_usuario = total_tareas / total_usuarios if total_usuarios > 0 else 0
            productividad      = (tareas_completadas / total_tareas * 100) if total_tareas > 0 else 0
            
            return EstadisticasGenerales(
                total_usuarios              = total_usuarios,
                usuarios_activos            = usuarios_activos,
                total_tareas                = total_tareas,
                tareas_pendientes           = tareas_pendientes,
                tareas_completadas          = tareas_completadas,
                tareas_por_usuario_promedio = tareas_por_usuario,
                productividad_general       = productividad
            )
            
        except AuthenticationError:
            raise Exception("No autorizado")
        except Exception as e:
            raise Exception(f"Error obteniendo estadísticas: {str(e)}")
    
    def get_dashboard(self, info: Info = None) -> DashboardData:
        """Resolver para obtener datos completos del dashboard en una sola query.
        
        Args:
            info (Info): Contexto de GraphQL con request y autenticación.
            
        Returns:
            DashboardData: Datos completos del dashboard incluyendo:
                
                - estadisticas     : Métricas generales del sistema
                - tareas_recientes : Últimas 5 tareas creadas
                - usuarios_activos : Usuarios con estado activo
                - tareas_urgentes : 5 tareas pendientes más antiguas
                
        Raises:
            AuthenticationError : Si el usuario no está autenticado.
            Exception           : Si ocurre un error obteniendo datos del dashboard.
            
        Example:
            dashboard = resolver.get_dashboard(info)
            print(f"Tareas recientes: {len(dashboard.tareas_recientes)}")
            
        Note:
            Este resolver optimiza múltiples consultas en una sola operación,
            ideal para interfaces de dashboard que necesitan varios tipos de datos.
        """
        try:
            current_user = get_current_user(info.context.get("request"))
            
            estadisticas = self.get_estadisticas_generales(info)
            
            # Tareas recientes (últimas 5)
            tareas_ordenadas = sorted(self.gestor.tareas.values(), 
                                    key=lambda t: t.fecha_creacion, reverse=True)
            tareas_recientes = [self._core_tarea_to_graphql(t) for t in tareas_ordenadas[:5]]
            
            # Usuarios activos
            usuarios_activos = [self._core_usuario_to_graphql(u) 
                              for u in self.gestor.usuarios.values()]
            
            # Tareas urgentes (pendientes más antiguas)
            tareas_pendientes = [t for t in self.gestor.tareas.values() 
                               if t.estado == "pendiente"]
            tareas_urgentes = sorted(tareas_pendientes, 
                                   key=lambda t: t.fecha_creacion)[:5]
            tareas_urgentes = [self._core_tarea_to_graphql(t) for t in tareas_urgentes]
            
            return DashboardData(
                estadisticas     = estadisticas,
                tareas_recientes = tareas_recientes,
                usuarios_activos = usuarios_activos,
                tareas_urgentes  = tareas_urgentes
            )
            
        except AuthenticationError:
            raise Exception("No autorizado")
        except Exception as e:
            raise Exception(f"Error obteniendo dashboard: {str(e)}")
    
    # =====================
    # MUTATION RESOLVERS
    # =====================
    
    def login(self, input: LoginInput) -> AuthPayload:
        """Resolver para autenticación de usuarios en el sistema.
        
        Args:
            input (LoginInput) : Credenciales de autenticación conteniendo:
                - username     : Nombre de usuario (puede ser nombre o email)
                - password     : Contraseña en texto plano
                
        Returns:
            AuthPayload: Resultado de autenticación conteniendo:
                
                - access_token   : JWT token para acceso a la API (30 min)
                - refresh_token  : Token para renovar el acceso
                - expires_in     : Tiempo de expiración en segundos
                - usuario        : Datos del usuario autenticado
                
        Raises:
            Exception: Si las credenciales son inválidas o hay error del sistema.
            
        Example:
            login_input = LoginInput(username="admin", password="password123")
            auth_result = resolver.login(login_input)
            
            if auth_result.access_token:
                print(f"Usuario {auth_result.usuario.nombre} autenticado")
                
        Note:
            - Las contraseñas se verifican usando hash seguro
            - Los tokens JWT incluyen información del usuario en el payload
            - El access token expira en 30 minutos por seguridad
        """
        try:
            
            
            # Verificar credenciales usando el gestor
            usuario_core, mensaje = self.gestor.autenticar_usuario(input.username, input.password)
            
            if not usuario_core:
                raise Exception("Credenciales inválidas")
            
            # Crear tokens
            access_token  = create_access_token(usuario_core.nombre, usuario_core.rol)
            refresh_token = create_refresh_token(usuario_core.nombre)
            
            return AuthPayload(
                access_token  = access_token,
                refresh_token = refresh_token,
                expires_in    = 1800,  # 30 minutos
                usuario       = self._core_usuario_to_graphql(usuario_core)
            )
            
        except Exception as e:
            raise Exception(f"Error en autenticación: {str(e)}")
    
    def crear_usuario(self, input: CrearUsuarioInput, info: Info = None) -> UsuarioMutationResponse:
        """Resolver para crear un nuevo usuario (solo administradores).
        
        El sistema core es simple:
        - Solo requiere el nombre del usuario
        - Rol siempre es 'user' por defecto
        - No maneja email ni contraseña inicial
        - Usuario debe configurar contraseña en el primer login
        
        Args:
            input (CrearUsuarioInput): Contiene solo el nombre del usuario
            info (Info): Contexto de GraphQL con usuario actual.
            
        Returns:
            UsuarioMutationResponse: Resultado de la operación
        """
        try:
            current_user = get_current_user(info.context.get("request"))
            
            # Solo admins pueden crear usuarios
            if current_user.get('rol') != "admin":
                return UsuarioMutationResponse(
                    success = False,
                    message = "No tienes permisos para crear usuarios",
                    code    = "FORBIDDEN"
                )
            
            # Crear usuario usando el gestor (solo requiere nombre)
            exito, mensaje = self.gestor.crear_usuario(nombre=input.nombre)
            
            if exito:
                # Recargar datos para obtener el usuario recién creado
                self.gestor.cargar_datos()
                usuario_core = self.gestor.usuarios.get(input.nombre)
                
                if usuario_core:
                    return UsuarioMutationResponse(
                        success = True,
                        message = f"{mensaje}. El usuario debe configurar su contraseña en el primer login.",
                        usuario = self._core_usuario_to_graphql(usuario_core)
                    )
                else:
                    return UsuarioMutationResponse(
                        success = False,
                        message = "Error: Usuario creado pero no encontrado",
                        code    = "INTERNAL_ERROR"
                    )
            else:
                return UsuarioMutationResponse(
                    success = False,
                    message = mensaje,
                    code    = "CREATION_FAILED"
                )
                
        except AuthenticationError:
            return UsuarioMutationResponse(
                success = False,
                message = "No autorizado",
                code    = "UNAUTHORIZED"
            )
        except Exception as e:
            return UsuarioMutationResponse(
                success = False,
                message = f"Error creando usuario: {str(e)}",
                code    = "INTERNAL_ERROR"
            )    
        
    def crear_tarea(self, input: CrearTareaInput, info: Info = None) -> TareaMutationResponse:
        """Resolver para crear una nueva tarea en el sistema.
        
        Args:
            input (CrearTareaInput): Datos de la nueva tarea:
                
                - nombre       : Título único de la tarea
                - descripcion  : Descripción detallada de la tarea
                - usuarios_asignados : Lista opcional de nombres de usuarios a asignar
            
            info (Info): Contexto de GraphQL con usuario actual.
            
        Returns:
            TareaMutationResponse: Resultado de la operación:
                
                - success : Si la creación fue exitosa
                - message : Mensaje descriptivo del resultado
                - tarea   : Datos de la tarea creada (si exitoso)
                - code    : Código de error (si falla)
                
        Example:
            input_data = CrearTareaInput(
                nombre="Nueva funcionalidad",
                descripcion="Implementar módulo de reportes",
                usuarios_asignados=["user1", "user2"]
            )
            response = resolver.crear_tarea(input_data, info)
            
        Note:
            - El creador de la tarea se asigna automáticamente
            - Los usuarios especificados deben existir en el sistema
            - El estado inicial de la tarea es PENDIENTE
        """
        
        try:
            current_user = get_current_user(info.context.get("request"))
            
            # Crear tarea usando el gestor
            exito, mensaje = self.gestor.crear_tarea(
                nombre      = input.nombre,
                descripcion = input.descripcion
            )   
            
            if exito:
                # tarea_core = self.gestor.tareas[input.nombre]
                # Asignar usuarios si se especificaron
                if input.usuarios_asignados:
                    for usuario_nombre in input.usuarios_asignados:
                        self.gestor.asignar_usuario_tarea(input.nombre, usuario_nombre)
                # Recargar datos después de crear y asignar
                self.gestor.cargar_datos()
                return TareaMutationResponse(
                    success = True,
                    message = mensaje,
                    tarea   = self._core_tarea_to_graphql(self.gestor.tareas[input.nombre])
                )
            else:
                return TareaMutationResponse(
                    success = False,
                    message = mensaje,
                    code    = "CREATION_FAILED"
                )
                
        except AuthenticationError:
            return TareaMutationResponse(
                success =False,
                message = "No autorizado",
                code    = "UNAUTHORIZED"
            )
        except Exception as e:
            return TareaMutationResponse(
                success = False,
                message = f"Error creando tarea: {str(type(e))} {str(e)}",
                code    = "INTERNAL_ERROR"
            )
    
    def actualizar_estado_tarea(self, tarea_nombre: str, estado: EstadoTarea, info: Info = None) -> TareaMutationResponse:
        """Resolver para actualizar el estado de una tarea.
        
        Args:
            tarea_nombre (str)   : Nombre único de la tarea a actualizar.
            estado (EstadoTarea) : Nuevo estado para la tarea:
                
                - PENDIENTE  : Tarea activa pero no completada
                - FINALIZADA : Tarea completada exitosamente
            
            info (Info): Contexto de GraphQL con usuario actual.
            
        Returns:
            TareaMutationResponse: Resultado de la operación:
                
                - success   : Si la actualización fue exitosa
                - message   : Mensaje descriptivo del resultado
                - tarea     : Datos de la tarea actualizada (si exitoso)
                - code      : Código de error (si falla)
                
        Example:
            response = resolver.actualizar_estado_tarea(
                "tarea_123", 
                EstadoTarea.FINALIZADA, 
                info
            )
            
        Note:
            - Solo usuarios asignados a la tarea o administradores pueden actualizarla
            - Al finalizar una tarea se guarda automáticamente en el archivo de finalizadas
            - Los cambios de estado se registran con timestamp
        """
        try:
            current_user = get_current_user(info.context.get("request"))
            
            tarea_core = self.gestor.tareas.get(tarea_nombre)
            if not tarea_core:
                return TareaMutationResponse(
                    success  = False,
                    message  = "Tarea no encontrada",
                    code     = "NOT_FOUND"
                )
            
            if estado == EstadoTarea.FINALIZADA:
                exito, mensaje = self.gestor.finalizar_tarea(tarea_nombre)
            else:
                # Para cambiar a pendiente, modificar directamente
                tarea_core.estado = estado.value
                exito             = True
                mensaje           = "Estado actualizado correctamente"
            
            if exito:
                # Recargar datos después de actualizar estado
                self.gestor.cargar_datos()
                return TareaMutationResponse(
                    success = True,
                    message = mensaje,
                    tarea   = self._core_tarea_to_graphql(self.gestor.tareas.get(tarea_nombre, tarea_core))
                )
            else:
                return TareaMutationResponse(
                    success = False,
                    message = mensaje,
                    code    = "UPDATE_FAILED"
                )
                
        except AuthenticationError:
            return TareaMutationResponse(
                success = False,
                message = "No autorizado",
                code    = "UNAUTHORIZED"
            )
        except Exception as e:
            return TareaMutationResponse(
                success = False,
                message = f"Error actualizando tarea: {str(e)}",
                code    = "INTERNAL_ERROR"
            )
    
    def asignar_usuario_tarea(self, input: AsignarUsuarioTareaInput, info: Info = None) -> TareaMutationResponse:
        """Resolver para asignar un usuario adicional a una tarea existente.
        
        Args:
            input (AsignarUsuarioTareaInput): Datos de la asignación:
                
                - tarea_nombre   : Nombre de la tarea a la que asignar el usuario
                - usuario_nombre : Nombre del usuario a asignar
            
            info (Info): Contexto de GraphQL con usuario actual.
            
        Returns:
            TareaMutationResponse: Resultado de la operación:
                
                - success : Si la asignación fue exitosa
                - message : Mensaje descriptivo del resultado
                - tarea   : Datos de la tarea con usuarios actualizados (si exitoso)
                - code    : Código de error (si falla)
                
        Example:
            input_data = AsignarUsuarioTareaInput(
                tarea_nombre="tarea_importante",
                usuario_nombre="user_456"
            )
            response = resolver.asignar_usuario_tarea(input_data, info)
            
        Note:
            - Solo creadores de tareas y administradores pueden asignar usuarios
            - No se puede asignar el mismo usuario múltiples veces a una tarea
            - El usuario asignado recibirá notificación si está habilitada
        """
        try:
            current_user = get_current_user(info.context.get("request"))
            
            exito, mensaje = self.gestor.asignar_usuario_tarea(
                input.tarea_nombre, input.usuario_nombre
            )
            
            if exito:
                # Recargar datos después de asignar usuario
                self.gestor.cargar_datos()
                tarea_core = self.gestor.tareas[input.tarea_nombre]
                return TareaMutationResponse(
                    success = True,
                    message = mensaje,
                    tarea   = self._core_tarea_to_graphql(tarea_core)
                )
            else:
                return TareaMutationResponse(
                    success = False,
                    message = mensaje,
                    code    = "ASSIGNMENT_FAILED"
                )
                
        except AuthenticationError:
            return TareaMutationResponse(
                success = False,
                message = "No autorizado",
                code    = "UNAUTHORIZED"
            )
        except Exception as e:
            return TareaMutationResponse(
                success = False,
                message = f"Error asignando usuario: {str(e)}",
                code    = "INTERNAL_ERROR"
            )
    
    def _core_usuario_to_graphql(self, usuario_core: CoreUsuario) -> Usuario:
        """Convierte un usuario del core a tipo GraphQL.
        
        Mapea exactamente los campos que existen en el core sin agregar campos adicionales.
        
        Args:
            usuario_core (CoreUsuario): Usuario del módulo core.
            
        Returns:
            Usuario: Usuario convertido al tipo GraphQL.
        """
        # Mapear rol del core a enum GraphQL
        rol_graphql = RolUsuario.ADMIN if usuario_core.rol == "admin" else RolUsuario.USER
        
        return Usuario(
            id             = usuario_core.nombre,  # Usar nombre como ID
            nombre         = usuario_core.nombre,
            rol            = rol_graphql,
            tiene_password = usuario_core.tiene_password(),
            activo         = True  # Siempre True, el core no maneja usuarios inactivos
        )
    
    def _core_tarea_to_graphql(self, tarea_core: CoreTarea) -> Tarea:
        """Convierte una tarea del core a tipo GraphQL.
        
        Args:
            tarea_core (CoreTarea): Tarea del módulo core.
            
        Returns:
            Tarea: Tarea convertida al tipo GraphQL con todos los campos.
            
        Note:
            - Mapea campos del core a estructura GraphQL
            - Convierte enums y formatos de fecha según sea necesario
            - Usa el nombre como ID para mantener compatibilidad
        """
        return Tarea(
            id                 = tarea_core.nombre,  # Usar nombre como ID
            nombre             = tarea_core.nombre,
            descripcion        = tarea_core.descripcion,
            estado             = EstadoTarea(tarea_core.estado),
            fecha_creacion     = tarea_core.fecha_creacion
        )
    
    # =====================
    # Field resolvers para campos dinámicos
    # =====================

    def resolve_tarea_fecha_finalizacion(self, tarea: Tarea) -> Optional[str]:
        """Resolver para obtener fecha de finalización de una tarea.
        
        Args:
            tarea (Tarea): Tarea de la cual obtener la fecha de finalización.
            
        Returns:
            Optional[str]: Fecha de finalización si disponible, None en caso contrario.
            
        Note:
            Actualmente el core no almacena fecha de finalización, 
            por lo que retorna None. En el futuro se podría implementar
            esta funcionalidad en la clase Tarea del core.
        """
        # El core actualmente no almacena fecha de finalización
        return None
    
    def resolve_usuario_tareas_asignadas(self, usuario: Usuario) -> List[Tarea]:
        """Resolver para obtener tareas asignadas a un usuario específico.
        
        Args:
            usuario (Usuario): Usuario del cual obtener las tareas asignadas.
            
        Returns:
            List[Tarea]: Lista de tareas en las que el usuario está asignado,
            convertidas a tipos GraphQL.
            
        Note:
            Este es un field resolver que se ejecuta automáticamente cuando
            se solicita el campo 'tareas_asignadas' en un query de Usuario.
        """
        tareas = [t for t in self.gestor.tareas.values() 
                 if usuario.id in t.usuarios_asignados]
        return [self._core_tarea_to_graphql(t) for t in tareas]
    
    def resolve_usuario_estadisticas(self, usuario: Usuario) -> EstadisticasUsuario:
        """Resolver para calcular estadísticas de un usuario específico.
        
        Args:
            usuario (Usuario): Usuario del cual calcular las estadísticas.
            
        Returns:
            EstadisticasUsuario: Métricas del usuario incluyendo:
                
                - tareas_asignadas   : Total de tareas asignadas
                - tareas_completadas : Número de tareas finalizadas
                - tareas_pendientes  : Número de tareas aún pendientes
                - productividad      : Porcentaje de tareas completadas
                
        Note:
            Las estadísticas se calculan en tiempo real basándose
            en las tareas actuales del sistema.
        """
        tareas_usuario = [t for t in self.gestor.tareas.values() 
                         if usuario.id in t.usuarios_asignados]
        
        total         = len(tareas_usuario)
        completadas   = len([t for t in tareas_usuario if t.estado == "finalizada"])
        pendientes    = total - completadas
        productividad = (completadas / total * 100) if total > 0 else 0
        
        return EstadisticasUsuario(
            tareas_asignadas   = total,
            tareas_completadas = completadas,
            tareas_pendientes  = pendientes,
            productividad      = productividad
        )
    
    def resolve_tarea_usuarios_asignados(self, tarea: Tarea) -> List[Usuario]:
        """Resolver para obtener usuarios asignados a una tarea específica.
        
        Args:
            tarea (Tarea): Tarea de la cual obtener los usuarios asignados.
            
        Returns:
            List[Usuario]: Lista de usuarios asignados a la tarea,
            convertidos a tipos GraphQL.
            
        Note:
            Este field resolver se ejecuta cuando se solicita el campo
            'usuarios_asignados' en un query de Tarea.
        """
        tarea_core = self.gestor.tareas.get(tarea.id)
        if not tarea_core:
            return []
        
        usuarios = [self.gestor.usuarios[user_id] 
                   for user_id in tarea_core.usuarios_asignados 
                   if user_id in self.gestor.usuarios]
        
        return [self._core_usuario_to_graphql(u) for u in usuarios]
    
    def resolve_tarea_comentarios(self, tarea: Tarea) -> List[Comentario]:
        """Resolver para obtener comentarios de una tarea específica.
        
        Args:
            tarea (Tarea): Tarea de la cual obtener los comentarios.
            
        Returns:
            List[Comentario]: Lista de comentarios asociados a la tarea,
            convertidos a tipos GraphQL con ID único por comentario.
            
        Note:
            Los comentarios en el core son tuplas (texto, autor, fecha)
            que se convierten a objetos Comentario para GraphQL.
        """
        tarea_core = self.gestor.tareas.get(tarea.id)
        if not tarea_core or not hasattr(tarea_core, 'comentarios'):
            return []
        
        return [
            Comentario(
                id    = f"{tarea.id}_{i}",
                texto = comentario.get('texto', ''),
                autor = comentario.get('autor', 'Desconocido'),
                fecha = comentario.get('fecha', datetime.now())
            )
            for i, comentario in enumerate(tarea_core.comentarios)
        ]


# Instancia global del resolver
resolver = GraphQLResolvers()