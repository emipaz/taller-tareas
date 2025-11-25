"""
Test runner para ejecutar todos los tests de GraphQL

Script para ejecutar todos los tests de la API GraphQL de forma organizada.
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """Ejecutar todos los tests de GraphQL"""
    print("🧪 EJECUTANDO TESTS DE GraphQL")
    print("=" * 50)
    
    try:
        import pytest
        
        # Configuración de pytest
        test_args = [
            os.path.dirname(__file__),  # Directorio de tests
            "-v",                       # Verbose output
            "--tb=short",              # Traceback corto
            "--disable-warnings",       # Deshabilitar warnings
            "--durations=10",          # Mostrar tests más lentos
        ]
        
        # Ejecutar tests
        exit_code = pytest.main(test_args)
        
        if exit_code == 0:
            print("\n✅ Todos los tests pasaron exitosamente!")
        else:
            print(f"\n❌ Algunos tests fallaron (código: {exit_code})")
        
        return exit_code
        
    except ImportError:
        print("❌ pytest no está instalado")
        print("🔧 Instalar con: pip install pytest")
        return 1
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)