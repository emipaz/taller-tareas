"""Punto de entrada para la API REST del sistema de gestión de tareas.

Este archivo proporciona el punto de entrada principal para la API REST,
importando y configurando la aplicación FastAPI desde el módulo api-rest.

Uso:
    python api.py
    
    O para desarrollo:
    uvicorn api:app --reload
"""

import sys
import os

# Agregar el directorio api-rest al path para las importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api-rest'))

# Importar la aplicación FastAPI
from api_rest import app

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Iniciando API REST del Sistema de Gestión de Tareas")
    print("📊 Documentación disponible en: http://localhost:8000/docs")
    print("🔍 Documentación alternativa: http://localhost:8000/redoc")
    print("❌ Presiona Ctrl+C para detener el servidor")
    print("-" * 60)
    
    # Configuración del servidor
    uvicorn.run(
        "api_rest:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )