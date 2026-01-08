@echo off
echo 🚀 Iniciando Servidor GraphQL - Sistema de Gestión de Tareas
echo.
echo 📡 Endpoints disponibles:
echo    • GraphQL API         : http://127.0.0.1:4000/graphql
echo    • GraphQL Playground  : http://127.0.0.1:4000/graphql (GET)
echo    • Documentación       : http://127.0.0.1:4000/docs
echo    • Health Check        : http://127.0.0.1:4000/health
echo.
echo 💡 Para detener el servidor presiona Ctrl+C
echo.

REM Activar el entorno virtual si existe
if exist "C:\entorno\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call "C:\entorno\Scripts\activate.bat"
)

REM Ejecutar el servidor
python graphql_api.py

echo.
echo 👋 Servidor GraphQL detenido
pause