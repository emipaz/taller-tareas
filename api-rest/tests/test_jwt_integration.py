# -*- coding: utf-8 -*-
"""Test básico de integración JWT para verificar que todo funciona.

Este script prueba la funcionalidad básica de JWT sin ejecutar el servidor completo.
Útil para verificar que no hay errores de importación y que el JWT funciona.
"""

import sys
import os
import io

# Configurar la salida para manejar caracteres Unicode
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Añadir el directorio padre para importar desde api-rest y core
current_dir = os.path.dirname(__file__)
api_rest_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(api_rest_dir)

sys.path.insert(0, api_rest_dir)
sys.path.insert(0, root_dir)

def test_jwt_basic_functionality():
    """Prueba básica de funcionalidad JWT."""
    print("🔑 Iniciando prueba de integración JWT...")
    
    try:
        # Test 1: Importar el módulo JWT
        print("📦 Importando jwt_auth...")
        from jwt_auth import create_access_token, verify_token, create_token_response
        print("✅ Importación JWT exitosa")
        
        # Test 2: Crear un token de acceso
        print("🔐 Creando token de prueba...")
        test_token = create_access_token("usuario_test", "user")
        print(f"✅ Token creado: {test_token[:50]}...")
        
        # Test 3: Verificar el token
        print("🔍 Verificando token...")
        token_data = verify_token(test_token)
        print(f"✅ Token verificado - Usuario: {token_data.username}, Rol: {token_data.role}")
        
        # Test 4: Crear respuesta completa de tokens
        print("📋 Creando respuesta completa de tokens...")
        token_response = create_token_response("admin_test", "admin")
        print(f"✅ Tokens creados - Access: {len(token_response.access_token)} chars, "
              f"Refresh: {len(token_response.refresh_token)} chars")
        
        print("\n🎉 ¡Todas las pruebas JWT pasaron exitosamente!")
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en prueba JWT: {e}")
        return False

def test_api_imports():
    """Prueba las importaciones de la API principal."""
    print("\n🚀 Verificando importaciones de API...")
    
    try:
        # Test importaciones principales
        from api_models import BaseResponse, UsuarioResponse
        from jwt_auth import TokenResponse  # TokenResponse está en jwt_auth
        from api_rest import app  # Esto debería importar sin errores
        print("✅ Importaciones de API exitosas")
        return True
        
    except ImportError as e:
        print(f"❌ Error en importaciones de API: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DE INTEGRACION JWT - Sistema de Gestion de Tareas")
    print("=" * 60)
    
    jwt_ok = test_jwt_basic_functionality()
    api_ok = test_api_imports()
    
    print("\n" + "=" * 60)
    if jwt_ok and api_ok:
        print("🎯 RESULTADO: ✅ Integración JWT completamente exitosa")
        print("🚀 La API está lista para ejecutarse con: uvicorn api_rest:app --reload")
    else:
        print("🎯 RESULTADO: ❌ Hay problemas en la integración")
        print("🔧 Revisa los errores anteriores y las dependencias")
    print("=" * 60)