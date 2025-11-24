"""
Servidor GraphQL para el Sistema de Gestión de Tareas

Implementa un servidor GraphQL usando Strawberry y FastAPI,
integrando con el sistema de autenticación JWT existente.
"""

import sys
import os
from typing import Dict, Any

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi import FastAPI, Request, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from strawberry.fastapi import GraphQLRouter
    import strawberry
    import uvicorn
except ImportError as e:
    print(f"Error importing dependencies: {e}")
    print("Please install: pip install strawberry-graphql[fastapi] uvicorn")
    sys.exit(1)

from schema import schema, get_context
from auth import get_auth_context


def create_graphql_app() -> FastAPI:
    """Crea y configura una aplicación FastAPI con GraphQL integrado.
    
    Esta función configura una aplicación completa de FastAPI con:
    - Router GraphQL de Strawberry
    - Middleware CORS para desarrollo
    - Contexto de autenticación JWT
    - Documentación automática
    
    Returns:
        FastAPI: Aplicación configurada lista para ejecutar con uvicorn.
        La aplicación incluye:
            - Endpoint GraphQL en /graphql
            - GraphQL Playground en /graphql (solo desarrollo)  
            - Documentación automática en /docs
            - Health check endpoint en /health
            
    Example:
        app = create_graphql_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    Note:
        La aplicación está configurada para desarrollo con CORS permisivo.
        En producción se debe ajustar la configuración de CORS y seguridad.
    """
    
    # Crear aplicación FastAPI
    app = FastAPI(
        title="🚀 Sistema de Gestión de Tareas - API GraphQL",
        description="""
        API GraphQL completa para gestión de tareas y usuarios.
        
        **Características:**
        - 🔐 Autenticación JWT
        - 📊 Queries flexibles y eficientes
        - 🔄 Mutations para operaciones de escritura
        - 📈 Estadísticas y dashboards
        - 🎯 Tipado fuerte con Strawberry
        
        **Endpoints:**
        - `/graphql` - Endpoint principal de GraphQL
        - `/docs` - Documentación automática
        - `/health` - Health check
        """,
        version   ="1.0.0",
        docs_url  ="/docs",
        redoc_url ="/redoc"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En producción, especificar orígenes permitidos
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Función para obtener contexto GraphQL con autenticación
    async def get_graphql_context(request: Request) -> Dict[str, Any]:
        """Crea contexto para GraphQL incluyendo datos de autenticación.
        
        Esta función es llamada automáticamente por el router GraphQL
        para cada request y prepara el contexto que estará disponible
        en todos los resolvers.
        
        Args:
            request (Request): Request HTTP de FastAPI conteniendo:
                - Headers con tokens de autenticación
                - Datos de sesión del usuario
                - Información de la petición HTTP
                
        Returns:
            Dict[str, Any]: Diccionario de contexto conteniendo:
                - request: Objeto request para acceso a headers
                - user: Datos del usuario autenticado (si aplica)
                - otros datos de contexto necesarios para resolvers
                
        Example:
            En un resolver:
            def get_usuarios(self, info: Info) -> List[Usuario]:
                request = info.context["request"]
                # Acceso a headers, autenticación, etc.
                
        Note:
            Esta función integra el sistema de autenticación JWT
            con el contexto de GraphQL de manera transparente.
        """
        return get_auth_context(request)
    
    # Crear router GraphQL
    graphql_router = GraphQLRouter(
        schema,
        context_getter=get_graphql_context,
        path="/graphql"
    )
    
    # Incluir router GraphQL
    app.include_router(graphql_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Endpoint de verificación de salud del servidor GraphQL.
        
        Este endpoint proporciona información básica sobre el estado
        del servidor y puede ser usado por herramientas de monitoreo
        y balanceadores de carga.
        
        Returns:
            dict: Diccionario con información de estado conteniendo:
                - status: Estado del servidor ("healthy")
                - message: Mensaje descriptivo
                - service: Nombre del servicio
                - version: Versión actual de la API
                
        Example:
            GET /health
            {
                "status": "healthy",
                "message": "GraphQL API is running! 🚀",
                "service": "Sistema de Gestión de Tareas - GraphQL",
                "version": "1.0.0"
            }
        """
        return {
            "status"  : "healthy",
            "message" : "GraphQL API is running! 🚀",
            "service" : "Sistema de Gestión de Tareas - GraphQL",
            "version" : "1.0.0"
        }
    
    # Endpoint de información
    @app.get("/")
    async def root():
        """Endpoint raíz con información y documentación de la API GraphQL.
        
        Proporciona una vista general de la API, sus endpoints disponibles
        y ejemplos de queries para facilitar la exploración y desarrollo.
        
        Returns:
            dict: Diccionario con información de la API conteniendo:
                - message: Mensaje de bienvenida
                - endpoints: Mapa de endpoints disponibles
                - authentication: Información sobre autenticación requerida
                - example_queries: Ejemplos de GraphQL queries/mutations
                
        Example:
            GET /
            {
                "message": "🚀 Sistema de Gestión de Tareas - API GraphQL",
                "endpoints": {
                    "graphql": "/graphql",
                    "docs": "/docs"
                },
                "example_queries": {...}
            }
            
        Note:
            Este endpoint es público y no requiere autenticación.
            Es útil para descubrimiento de la API y documentación.
        """
        return {
            "message"    : "🚀 Sistema de Gestión de Tareas - API GraphQL",
            "endpoints"  : {
                "graphql"   : "/graphql",
                "playground": "/graphql (GET)",
                "docs"      : "/docs",
                "health"    : "/health"
            },
            "authentication" : "JWT Bearer Token required for most operations",
            "example_queries": {
                "health"    : "query { health }",
                "login"     : "mutation Login($username: String!, $password: String!) { login(input: {username: $username, password: $password}) { access_token usuario { nombre rol } } }",
                "dashboard" : "query { dashboard { estadisticas { total_tareas tareas_pendientes } tareas_recientes { nombre estado } } }"
            }
        }
    
    # Middleware para logging (opcional)
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Middleware para logging de requests HTTP.
        
        Registra información sobre cada request incluyendo método,
        path, código de respuesta y tiempo de procesamiento.
        
        Args:
            request (Request): Request HTTP entrante
            call_next: Función para continuar el procesamiento
            
        Returns:
            Response: Respuesta HTTP procesada
            
        Note:
            Este middleware es opcional y puede deshabilitarse en
            producción si se usa un sistema de logging externo.
        """
        import time
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        print(f"🔗 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        return response
    
    return app


# Crear la aplicación
app = create_graphql_app()


def run_server(
    host: str = "0.0.0.0",
    port: int = 4000,
    reload: bool = True,
    log_level: str = "info"
):
    """Ejecuta el servidor GraphQL con configuración personalizada.
    
    Args:
        host (str)     : Dirección IP del host. Default "0.0.0.0" (todas las interfaces).
        port (int)     : Puerto donde ejecutar el servidor. Default 4000.
        reload (bool)  : Si recargar automáticamente en cambios de código.
            Útil para desarrollo, desactivar en producción.
        log_level (str): Nivel de logging ("debug", "info", "warning", "error").
            
    Example:
        # Desarrollo
        run_server(port=8000, reload=True)
        
        # Producción  
        run_server(host="127.0.0.1", port=80, reload=False, log_level="warning")
        
    Note:
        - En desarrollo usar reload=True para recarga automática
        - En producción usar un servidor ASGI como Gunicorn con uvicorn workers
        - El servidor incluye GraphQL Playground para pruebas interactivas
    """
    print(f"""
🚀 Iniciando Servidor GraphQL - Sistema de Gestión de Tareas

📡 Endpoints disponibles:
   • GraphQL API         : http://{host}:{port}/graphql
   • GraphQL Playground  : http://{host}:{port}/graphql (GET)
   • Documentación       : http://{host}:{port}/docs
   • Health Check: http://{host}:{port}/health

🔐 Autenticación:
   • Usar token JWT en header: Authorization: Bearer <token>
   • Login via mutation para obtener token

📊 Ejemplo de uso:
   1. Abrir GraphQL Playground: http://{host}:{port}/graphql
   2. Ejecutar mutation de login para obtener token
   3. Configurar header Authorization con el token
   4. Ejecutar queries y mutations
    """)
    
    uvicorn.run(
        app,  # Pasar la aplicación directamente en lugar de string
        host       = host,
        port       = port,
        reload     = reload,
        log_level  = log_level,
        access_log = True
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Servidor GraphQL - Sistema de Gestión de Tareas")
    parser.add_argument("--host", default="0.0.0.0",        help="Host del servidor")
    parser.add_argument("--port", type=int, default=4000,   help="Puerto del servidor")
    parser.add_argument("--no-reload", action="store_true", help="Deshabilitar auto-reload")
    parser.add_argument("--log-level", default="info",      help="Nivel de logging")
    
    args = parser.parse_args()
    
    run_server(
        host      = args.host,
        port      = args.port,
        reload    = not args.no_reload,
        log_level = args.log_level
    )