#!/usr/bin/env python3
"""
Punto de entrada para la API GraphQL del Sistema de Gestión de Tareas

Ejecutar con: python graphql_api.py
"""

import sys
import os
import signal

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def signal_handler(sig, frame):
    """Maneja la señal de interrupción (Ctrl+C)"""
    print("\n👋 Deteniendo servidor GraphQL...")
    sys.exit(0)

try:
    # Importar desde el directorio api-graphql (con guión)
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api-graphql'))
    from server import run_server
except ImportError as e:
    print(f"❌ Error importando servidor GraphQL: {e}")
    print("🔧 Asegúrate de instalar las dependencias:")
    print("   pip install strawberry-graphql[fastapi] uvicorn")
    print(f"📁 Verificando directorio api-graphql: {os.path.exists('api-graphql')}")
    sys.exit(1)


if __name__ == "__main__":
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 Iniciando API GraphQL - Sistema de Gestión de Tareas")
    print("📡 El servidor estará disponible en: http://127.0.0.1:4000/graphql")
    print("🎮 GraphQL Playground: http://127.0.0.1:4000/graphql")
    print("📚 Documentación: http://127.0.0.1:4000/docs")
    print("💡 Para detener el servidor presiona Ctrl+C")
    print("")
    
    try:
        run_server(
            host="127.0.0.1",  # Usar localhost específico
            port=4000,
            reload=False  # Desactivar reload para evitar problemas
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)