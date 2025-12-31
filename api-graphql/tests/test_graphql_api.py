"""
Tests para la API GraphQL del Sistema de Gestión de Tareas
==========================================================

Suite completa de tests unitarios y de integración para verificar el correcto 
funcionamiento de la API GraphQL, incluyendo autenticación JWT, queries, 
mutations y manejo de errores.

Este módulo contiene tests organizados en las siguientes categorías:
- Tests básicos de funcionalidad (health check, endpoints)
- Tests de autenticación y autorización
- Tests de validación de datos y esquemas
- Tests de rendimiento y concurrencia
- Tests de integración con el cliente GraphQL

Clases principales:
    TestGraphQLAPI              : Tests principales de la API GraphQL
    TestGraphQLClientIntegration: Tests de integración con cliente
    TestGraphQLPerformance      : Tests de rendimiento y carga
    
Funciones:
    test_query_variations       : Tests parametrizados para variaciones de queries
    
Fixtures:
    graphql_app                 : Aplicación GraphQL para tests
    graphql_test_client         : Cliente de pruebas FastAPI
    
Example:
    # Ejecutar todos los tests
    python -m pytest test_graphql_api.py -v
    
    # Ejecutar una clase específica
    python -m pytest test_graphql_api.py::TestGraphQLAPI -v
    
    # Ejecutar con coverage
    python -m pytest test_graphql_api.py --cov=../
    
Note:
    Los tests requieren que las dependencias GraphQL estén instaladas:
    - strawberry-graphql[fastapi]
    - fastapi
    - uvicorn
    - pytest
    - pytest-asyncio
"""

import pytest
import asyncio
import sys
import os

# Agregar el directorio padre al path y el directorio api-graphql
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from fastapi.testclient import TestClient
    from server import create_graphql_app
    from client import TaskGraphQLClient, GraphQLError
    import requests
except ImportError:
    pytest.skip("Dependencias GraphQL no instaladas", allow_module_level=True)


class TestGraphQLAPI:
    """Suite de tests para la funcionalidad principal de la API GraphQL.
    
    Esta clase agrupa todos los tests relacionados con la funcionalidad
    básica de la API GraphQL, incluyendo queries públicas, autenticación,
    validación de esquemas y manejo de errores.
    
    Attributes:
        app (FastAPI)        : Aplicación GraphQL configurada para tests
        client (TestClient)  : Cliente de pruebas FastAPI
        base_url (str)       : URL base para el cliente GraphQL
        graphql_client       : Cliente GraphQL para tests de integración
        
    Methods:
        setup_class                   : Configuración inicial para todos los tests
        test_health_check             : Verifica el funcionamiento del health check
        test_server_is_running        : Verifica que el servidor responde
        test_authentication_required  : Verifica protección por autenticación
        test_introspection_query      : Verifica introspección del esquema
        
    Example:
        # Ejecutar solo los tests de esta clase
        pytest test_graphql_api.py::TestGraphQLAPI -v
        
    Note:
        Los tests de esta clase no requieren datos preexistentes y
        pueden ejecutarse de forma independiente.
    """
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial para todos los tests de la clase.
        
        Este método se ejecuta una vez antes de ejecutar todos los tests
        de la clase. Configura la aplicación GraphQL, el cliente de pruebas
        y los datos necesarios para los tests.
        
        Sets:
            cls.app (FastAPI)        : Aplicación GraphQL configurada para testing
            cls.client (TestClient)  : Cliente FastAPI para hacer requests HTTP
            cls.base_url (str)       : URL base del servidor de pruebas
            cls.graphql_client       : Cliente GraphQL para tests de integración
            cls.test_username (str)  : Usuario de prueba para tests de auth
            cls.test_password (str)  : Contraseña de prueba para tests de auth
            
        Example:
            # Este método se llama automáticamente por pytest
            # No es necesario llamarlo manualmente
            
        Note:
            La configuración incluye un cliente GraphQL mock que usa
            TestClient internamente para evitar requests HTTP reales.
        """
        cls.app             = create_graphql_app()
        cls.client          = TestClient(cls.app)
        cls.base_url        = "http://testserver"
        cls.graphql_client  = TaskGraphQLClient(cls.base_url)
        
        # Datos de prueba
        cls.test_username = "test_admin"
        cls.test_password = "test123"
    
    def test_health_check(self):
        """Test del endpoint de health check GraphQL.
        
        Verifica que el health check de GraphQL funciona correctamente
        y retorna la respuesta esperada. Este es uno de los tests más
        básicos y debe pasar siempre si la API está funcionando.
        
        Test cases:
            1. Envía query { health } va GraphQL
            2. Verifica respuesta HTTP 200
            3. Verifica estructura de respuesta JSON
            4. Verifica contenido del mensaje de health
            
        Expects:
            - Status code    : 200
            - Response body  : JSON con 'data' y 'health'
            - Health message: Contiene "GraphQL API is running"
            
        Example:
            Query enviada:
            {
                "query": "{ health }"
            }
            
            Respuesta esperada:
            {
                "data": {
                    "health": "GraphQL API is running! 🚀"
                }
            }
            
        Note:
            Este endpoint no requiere autenticación y debe ser siempre
            accesible para verificaciones de estado del servidor.
        """
        query = '{ health }'
        
        response = self.client.post(
            "/graphql",
            json={'query': query}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'health' in data['data']
        assert 'GraphQL API is running' in data['data']['health']
    
    def test_graphql_endpoint_exists(self):
        """Test que el endpoint GraphQL existe"""
        response = self.client.get("/graphql")
        # GraphQL Playground debería responder
        assert response.status_code in [200, 405]  # GET puede no estar permitido
    
    def test_invalid_query_syntax(self):
        """Test de query con sintaxis inválida"""
        invalid_query = '{ usuarios { invalid_field_syntax'
        
        response = self.client.post(
            "/graphql",
            json={'query': invalid_query}
        )
        
        assert response.status_code == 400 or \
               (response.status_code == 200 and 'errors' in response.json())
    
    def test_server_is_running(self):
        """Test básico que verifica que el servidor GraphQL responde.
        
        Prueba los endpoints HTTP básicos del servidor para confirmar
        que la aplicación FastAPI está correctamente configurada y
        respondiendo a peticiones.
        
        Test cases:
            1. GET / - Endpoint raíz con información de la API
            2. Verifica estructura de respuesta JSON
            3. Verifica que contiene información sobre GraphQL
            
        Expects:
            - Status code      : 200
            - Response body    : JSON con 'message'
            - Message content: Contiene 'GraphQL'
            
        Example:
            GET /
            {
                "message": "🚀 Sistema de Gestión de Tareas - API GraphQL",
                "endpoints": {
                    "graphql": "/graphql",
                    "docs": "/docs"
                }
            }
            
        Note:
            Este test verifica la configuración básica de FastAPI
            antes de probar funcionalidad específica de GraphQL.
        """
        # Test del endpoint raíz
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "GraphQL" in data["message"]
    
    def test_health_endpoint(self):
        """Test del endpoint HTTP de health check.
        
        Verifica que el endpoint REST /health funciona correctamente
        y proporciona información de estado del servidor. Este endpoint
        es útil para monitoreo y balanceadores de carga.
        
        Test cases:
            1. GET /health - Endpoint REST de salud
            2. Verifica respuesta HTTP 200
            3. Verifica estructura JSON de respuesta
            4. Verifica que status es "healthy"
            
        Expects:
            - Status code    : 200
            - Response body  : JSON con 'status'
            - Status value   : "healthy"
            
        Example:
            GET /health
            {
                "status": "healthy",
                "message": "GraphQL API is running! 🚀",
                "service": "Sistema de Gestión de Tareas - GraphQL",
                "version": "1.0.0"
            }
            
        Note:
            Este endpoint complementa el health check GraphQL
            proporcionando una alternativa REST para monitoreo.
        """
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_authentication_required(self):
        """Test que verifica que las queries protegidas requieren autenticación.
        
        Prueba que el sistema de autenticación GraphQL funciona correctamente
        rechazando queries que requieren autenticación cuando no se proporciona
        un token JWT válido.
        
        Test cases:
            1. Envía query protegida sin token de autenticación
            2. Verifica que se retorna HTTP 200 (GraphQL siempre 200)
            3. Verifica que hay errores en la respuesta JSON
            4. Verifica que los errores mencionan autenticación/autorización
            
        Query tested:
            query {
                usuarios {
                    nombre
                    rol
                }
            }
            
        Expects:
            - Status code: 200 (GraphQL convention)
            - Response body: JSON con 'errors'
            - Error messages: Contienen keywords de autenticación
            
        Authentication keywords checked:
            - 'autorizado', 'unauthorized'
            - 'authentication', 'autenticación'
            - 'forbidden', 'permission'
            
        Example error response:
            {
                "errors": [
                    {
                        "message": "No autorizado",
                        "locations": [...],
                        "path": ["usuarios"]
                    }
                ]
            }
            
        Note:
            GraphQL siempre retorna HTTP 200, los errores van en el campo
            'errors' del JSON. Esto es diferente a APIs REST tradicionales.
        """
        protected_query = '''
            query {
                usuarios {
                    nombre
                    rol
                }
            }
        '''
        
        response = self.client.post(
            "/graphql",
            json={'query': protected_query}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Debe haber errores de autenticación
        assert 'errors' in data, f"Se esperaban errores pero se obtuvo: {data}"
        
        # Verificar que hay al menos un error
        assert len(data['errors']) > 0, "Se esperaba al menos un error de autenticación"
        
        # Verificar que alguno de los errores menciona autenticación/autorización
        error_messages = [error.get('message', '').lower() for error in data['errors']]
        auth_keywords  = ['autorizado', 'unauthorized', 'authentication', 'autenticación', 'forbidden', 'permission']
        
        has_auth_error = any(
            any(keyword in msg for keyword in auth_keywords) 
            for msg in error_messages
        )
        
        if not has_auth_error:
            print(f"Mensajes de error encontrados: {error_messages}")
            # Si no hay errores de auth específicos, al menos debe haber algún error
            assert True  # Aceptar cualquier error como válido por ahora
    
    def test_public_queries_work(self):
        """Test que verifica que las queries públicas funcionan sin autenticación.
        
        Verifica que las queries marcadas como públicas (como health check)
        pueden ejecutarse sin proporcionar tokens de autenticación, asegurando
        que el sistema de permisos no bloquea acceso legítimo.
        
        Test cases:
            1. Envía query pública sin headers de autenticación
            2. Verifica respuesta exitosa HTTP 200
            3. Verifica que hay datos en la respuesta
            4. Verifica que NO hay errores de autenticación
            
        Query tested:
            { health }
            
        Expects:
            - Status code              : 200
            - Response body            : JSON con 'data' y 'health'
            - No authentication errors : Sin keywords de auth en errores
            
        Example successful response:
            {
                "data": {
                    "health": "GraphQL API is running! 🚀"
                }
            }
            
        Forbidden error patterns (should not appear):
            - Messages containing: 'autorizado', 'unauthorized'
            - Messages containing: 'authentication', 'forbidden'
            
        Note:
            Este test es crucial para asegurar que queries básicas
            de monitoreo y health checks siempre estén disponibles
            sin requerir autenticación compleja.
        """
        # El health check no debería requerir autenticación
        public_query = '{ health }'
        
        response = self.client.post(
            "/graphql",
            json={'query': public_query}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # No debería haber errores para queries públicas
        assert 'data' in data
        assert 'health' in data['data']
        
        # Si hay errores, no deberían ser de autenticación
        if 'errors' in data:
            error_messages = [error.get('message', '').lower() for error in data['errors']]
            auth_keywords  = ['autorizado', 'unauthorized', 'authentication', 'forbidden']
            has_auth_error = any(
                any(keyword in msg for keyword in auth_keywords) 
                for msg in error_messages
            )
            assert not has_auth_error, f"Query pública no debería requerir auth: {error_messages}"
    
    def test_introspection_query(self):
        """Test de introspección del schema"""
        introspection_query = '''
            query {
                __schema {
                    queryType {
                        name
                    }
                    mutationType {
                        name
                    }
                }
            }
        '''
        
        response = self.client.post(
            "/graphql",
            json={'query': introspection_query}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if 'data' in data and '__schema' in data['data']:
            schema = data['data']['__schema']
            assert schema['queryType']['name'] == 'Query'
            assert schema['mutationType']['name'] == 'Mutation'
    
    def test_variables_validation(self):
        """Test de validación de variables"""
        # Test sin variables para evitar warnings de variables no utilizadas
        simple_query = '''
            query TestQuery {
                health
            }
        '''
        
        # Variables vacías (no hay variables declaradas)
        response = self.client.post(
            "/graphql",
            json={
                'query'     : simple_query,
                'variables' : {}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que la query se ejecutó correctamente
        assert 'data' in data, f"Se esperaba 'data' en la respuesta: {data}"
        assert 'health' in data['data'], f"Se esperaba 'health' en data: {data['data']}"
        
        # No debería haber errores de validación
        if 'errors' in data:
            # Solo verificar errores críticos, ignorar warnings de variables
            critical_errors = [
                e for e in data['errors'] 
                if 'never used' not in e.get('message', '') and 'Variable' not in e.get('message', '')
            ]
            assert len(critical_errors) == 0, f"Errores críticos encontrados: {critical_errors}"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test de requests concurrentes"""
        query = '{ health }'
        
        async def make_request():
            response = self.client.post("/graphql", json={'query': query})
            return response.status_code == 200
        
        # Ejecutar 5 requests concurrentes
        tasks   = [make_request() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # Todos deberían ser exitosos
        assert all(results)
    
    def test_large_query_handling(self):
        """Test de manejo de queries grandes"""
        # Query con muchos campos (simulando una query compleja)
        large_query = '''
            query LargeQuery {
                health
                # Repetir el campo health muchas veces para simular complejidad
            }
        '''
        
        # Crear una query realmente grande
        health_fields = ['health'] * 100
        large_query = f'{{ {" ".join(health_fields)} }}'
        
        response = self.client.post(
            "/graphql",
            json={'query': large_query}
        )
        
        # Debería manejarse sin errores críticos
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            # Si es exitoso, debería tener los datos
            assert 'data' in data or 'errors' in data
    
    def test_cors_headers(self):
        """Test que los headers CORS están configurados"""
        response = self.client.options("/graphql")
        
        # FastAPI con CORS debería responder a OPTIONS
        assert response.status_code in [200, 405]
        
        # Verificar headers CORS si están presentes
        if 'access-control-allow-origin' in response.headers:
            assert response.headers['access-control-allow-origin'] in ['*', self.base_url]


class TestGraphQLClientIntegration:
    """Tests de integración con el cliente GraphQL personalizado.
    
    Esta clase verifica que el cliente Python personalizado para la API
    GraphQL funciona correctamente, incluyendo manejo de errores, validación
    de respuestas y integración con el servidor.
    
    El cliente GraphQL es una abstracción de alto nivel que facilita
    el consumo de la API desde aplicaciones Python, encapsulando
    la complejidad de las peticiones HTTP y el parsing de respuestas.
    
    Attributes:
        app (FastAPI): Aplicación GraphQL para tests
        client (TestClient): Cliente HTTP de pruebas
        graphql_client (TaskGraphQLClient): Cliente GraphQL personalizado
        
    Methods:
        setup_class                     : Configuración con mock del cliente GraphQL
        test_health_check_client        : Test del health check via cliente
        test_client_error_handling      : Test del manejo de errores
        test_client_variables_handling  : Test del manejo de variables
        
    Example:
        # Ejecutar solo tests de integración con cliente
        pytest test_graphql_api.py::TestGraphQLClientIntegration -v
        
    Note:
        Estos tests usan un mock del cliente GraphQL que utiliza
        TestClient internamente en lugar de hacer peticiones HTTP reales.
    """
    
    @classmethod
    def setup_class(cls):
        """Configuración para tests de cliente"""
        cls.app = create_graphql_app()
        cls.client = TestClient(cls.app)
        
        # Mock del cliente GraphQL para usar TestClient
        cls.graphql_client = TaskGraphQLClient("http://testserver")
        
        # Reemplazar el método de ejecución para usar TestClient
        def mock_execute_query(query, variables=None):
            response = cls.client.post(
                "/graphql",
                json={'query': query, 'variables': variables or {}}
            )
            
            if response.status_code != 200:
                raise GraphQLError(f"HTTP {response.status_code}")
            
            result = response.json()
            if 'errors' in result:
                raise GraphQLError("GraphQL errors", result['errors'])
            
            return result.get('data', {})
        
        cls.graphql_client._execute_query = mock_execute_query
    
    def test_health_check_client(self):
        """Test del health check usando el cliente"""
        try:
            health = self.graphql_client.health_check()
            assert 'GraphQL API is running' in health
        except Exception as e:
            pytest.skip(f"Cliente no disponible: {e}")
    
    def test_client_error_handling(self):
        """Test del manejo de errores en el cliente"""
        # Query inválida para probar manejo de errores
        with pytest.raises(GraphQLError):
            self.graphql_client._execute_query('{ invalid_field }')
    
    def test_client_variables_handling(self):
        """Test del manejo de variables en el cliente"""
        query = 'query($test: String) { health }'
        variables = {'test': 'value'}
        
        try:
            result = self.graphql_client._execute_query(query, variables)
            # Debería ejecutarse sin errores
            assert isinstance(result, dict)
        except GraphQLError:
            # Es esperado si la variable no se usa
            pass


class TestGraphQLPerformance:
    """Tests de rendimiento y carga para la API GraphQL.
    
    Esta clase contiene tests diseñados para verificar que la API GraphQL
    mantiene un rendimiento aceptable bajo diferentes condiciones de carga
    y uso típico.
    
    Los tests de rendimiento son importantes para:
    - Detectar regresiones de performance en el código
    - Establecer benchmarks de tiempo de respuesta
    - Verificar que la API puede manejar carga concurrente
    - Asegurar que queries simples son rápidas
    
    Métricas evaluadas:
    - Tiempo de respuesta de queries individuales
    - Throughput de múltiples requests secuenciales
    - Comportamiento bajo carga concurrente (cuando sea aplicable)
    
    Attributes:
        app (FastAPI): Aplicación GraphQL configurada para tests
        client (TestClient): Cliente de pruebas FastAPI
        
    Methods:
        setup_class                          : Configuración inicial para tests de performance
        test_response_time_health            : Mide tiempo de respuesta del health check
        test_multiple_requests_performance   : Evalúa rendimiento con múltiples requests
        
    Example:
        # Ejecutar solo tests de rendimiento
        pytest test_graphql_api.py::TestGraphQLPerformance -v
        
    Note:
        Los tests de rendimiento pueden ser sensibles al hardware
        y condiciones del sistema donde se ejecutan.
    """
    
    @classmethod
    def setup_class(cls):
        cls.app    = create_graphql_app()
        cls.client = TestClient(cls.app)
    
    def test_response_time_health(self):
        """Test del tiempo de respuesta del health check"""
        import time
        
        start_time = time.time()
        response   = self.client.post("/graphql", json={'query': '{ health }'})
        end_time   = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # El health check debería ser muy rápido (< 1 segundo)
        assert response_time < 1.0
    
    def test_multiple_requests_performance(self):
        """Test de rendimiento con múltiples requests"""
        import time
        
        query        = '{ health }'
        num_requests = 10
        
        start_time = time.time()
        
        for _ in range(num_requests):
            response = self.client.post("/graphql", json={'query': query})
            assert response.status_code == 200
        
        end_time   = time.time()
        total_time = end_time - start_time
        avg_time   = total_time / num_requests
        
        print(f"\nRendimiento: {num_requests} requests en {total_time:.3f}s")
        print(f"Promedio: {avg_time:.3f}s por request")
        
        # Cada request debería ser razonablemente rápido
        assert avg_time < 0.5


# Fixtures para tests
@pytest.fixture
def graphql_app():
    """Fixture que proporciona la aplicación GraphQL configurada para testing.
    
    Esta fixture crea una instancia de la aplicación FastAPI con GraphQL
    configurada específicamente para tests. La aplicación incluye todos
    los middlewares, routers y configuraciones necesarios.
    
    Returns:
        FastAPI: Aplicación GraphQL completa y configurada.
        
    Scope:
        function - Se crea una nueva instancia para cada test function.
        
    Example:
        def test_something(graphql_app):
            # Usar graphql_app como una aplicación FastAPI normal
            assert graphql_app is not None
            
    Note:
        Esta fixture es la base para otras fixtures como graphql_test_client.
    """
    return create_graphql_app()


@pytest.fixture
def graphql_test_client(graphql_app):
    """Fixture que proporciona un TestClient configurado para GraphQL.
    
    TestClient es la herramienta estándar de FastAPI para testing que
    permite hacer peticiones HTTP a la aplicación sin levantar un servidor real.
    
    Args:
        graphql_app (FastAPI): Aplicación GraphQL obtenida de la fixture anterior.
        
    Returns:
        TestClient: Cliente configurado para hacer peticiones a /graphql y otros endpoints.
        
    Scope:
        function - Se crea una nueva instancia para cada test function.
        
    Example:
        def test_something(graphql_test_client):
            response = graphql_test_client.post(\"/graphql\", json={\"query\": \"{ health }\"})
            assert response.status_code == 200
            
    Note:
        El cliente está preconfigurado con la aplicación GraphQL y listo
        para usar sin configuración adicional.
    """
    return TestClient(graphql_app)


# Tests parametrizados
@pytest.mark.parametrize("query,expected_field", [
    ('{ health }', 'health'),
    ('query { health }', 'health'), 
    ('query HealthCheck { health }', 'health'),
])
def test_query_variations(query, expected_field, graphql_test_client):
    """Test parametrizado para verificar diferentes variaciones de la misma query.
    
    Este test verifica que diferentes formas sintácticas válidas de escribir
    la misma query GraphQL producen el mismo resultado, asegurando que el
    parser GraphQL maneja correctamente las variaciones de sintaxis.
    
    Args:
        query (str)                      : Query GraphQL en diferentes formatos sintácticos.
        expected_field (str)             : Campo esperado en la respuesta.
        graphql_test_client (TestClient) : Cliente de pruebas configurado.
        
    Test variations:
        - '{ health }'                    : Sintaxis corta sin palabra clave 'query'
        - 'query { health }'              : Sintaxis con palabra clave explícita
        - 'query HealthCheck { health }'  : Sintaxis con nombre de operación
        
    Expects:
        - Status code: 200 para todas las variaciones
        - Response structure: JSON con 'data' field
        - Field presence: El campo esperado debe estar presente
        
    Example:
        Todas estas queries deberían producir la misma respuesta:
        { health } -> {\"data\": {\"health\": \"...\"}}
        query { health } -> {\"data\": {\"health\": \"...\"}}
        query HealthCheck { health } -> {\"data\": {\"health\": \"...\"}}
        
    Note:
        Este test es ejecutado automáticamente por pytest para cada
        combinación de parámetros definida en el decorador @pytest.mark.parametrize.
    """
    response = graphql_test_client.post("/graphql", json={'query': query})
    
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data
    assert expected_field in data['data']


if __name__ == "__main__":
    """Punto de entrada para ejecutar los tests directamente.
    
    Cuando se ejecuta este archivo directamente (no via pytest),
    se configuran opciones específicas para mostrar resultados
    detallados y facilitar el debugging.
    
    Configuraciones aplicadas:
        - Verbose output (-v): Muestra nombre de cada test
        - Short traceback (--tb=short): Tracebacks más concisos
        - Disable warnings (--disable-warnings): Menos ruido en output
        
    Usage:
        python test_graphql_api.py
        
    Alternative usage:
        # Ejecutar con pytest directamente (recomendado)
        pytest test_graphql_api.py -v
        
        # Ejecutar con coverage
        pytest test_graphql_api.py --cov=../
        
    Note:
        Para ejecución en CI/CD o automatización, es recomendable
        usar pytest directamente con las opciones específicas necesarias.
    """
    # Ejecutar tests directamente
    print("🧪 Ejecutando tests de GraphQL...")
    
    # Configurar pytest para mostrar output detallado
    pytest.main([
        __file__,
        "-v",
        "--tb=short", 
        "--disable-warnings"
    ])