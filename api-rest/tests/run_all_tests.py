"""Script para ejecutar todos los tests de la API REST.

Este script ejecuta todos los tests disponibles para la API REST,
incluyendo tests de integración JWT y tests unitarios.
"""

import subprocess
import sys
import os

def run_jwt_integration_tests():
    """Ejecuta los tests de integración JWT."""
    print("🔑 Ejecutando tests de integración JWT...")
    try:
        result = subprocess.run([sys.executable, "test_jwt_integration.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        print(result.stdout)
        if result.stderr:
            print("Errores:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando tests JWT: {e}")
        return False

def run_app_tests():
    """Ejecuta los tests unitarios de la aplicación."""
    print("\n📱 Ejecutando tests unitarios de la aplicación...")
    try:
        result = subprocess.run([sys.executable, "test_app.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        print(result.stdout)
        if result.stderr:
            print("Errores:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando tests de app: {e}")
        return False

def main():
    """Función principal que ejecuta todos los tests."""
    print("🧪 EJECUTOR DE TESTS - API REST")
    print("=" * 50)
    
    jwt_ok = run_jwt_integration_tests()
    app_ok = run_app_tests()
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE RESULTADOS:")
    print(f"🔑 Tests JWT: {'✅ PASÓ' if jwt_ok else '❌ FALLÓ'}")
    print(f"📱 Tests App: {'✅ PASÓ' if app_ok else '❌ FALLÓ'}")
    
    if jwt_ok and app_ok:
        print("\n🎉 TODOS LOS TESTS PASARON")
        print("🚀 API lista para producción")
    else:
        print("\n⚠️  ALGUNOS TESTS FALLARON")
        print("🔧 Revisar errores antes de continuar")
        
    return jwt_ok and app_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)