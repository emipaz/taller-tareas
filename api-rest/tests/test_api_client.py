"""Script de ejemplo para probar la API REST.

Este script demuestra cómo consumir la API REST del sistema de gestión de tareas
usando requests de Python.
"""

import requests
import json
from typing import Dict, Any


class TaskAPIClient:
    """Cliente para interactuar con la API de gestión de tareas con soporte JWT."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Inicializa el cliente de la API.
        
        Args:
            base_url: URL base de la API.
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Obtiene los headers de autenticación si hay token disponible."""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Maneja la respuesta de la API.
        
        Args:
            response: Respuesta de requests.
            
        Returns:
            Diccionario con los datos de la respuesta.
            
        Raises:
            Exception: Si hay error en la respuesta.
        """
        try:
            data = response.json()
            if response.status_code >= 400:
                if response.status_code == 401:
                    print(f"🔒 Error de autenticación: {data.get('message', 'Token inválido o expirado')}")
                    print("💡 Sugerencia: Hacer login nuevamente")
                else:
                    print(f"❌ Error {response.status_code}: {data.get('message', 'Error desconocido')}")
                return {"success": False, "error": data.get('message')}
            return data
        except json.JSONDecodeError:
            print(f"❌ Error: Respuesta no válida del servidor")
            return {"success": False, "error": "Respuesta inválida"}
    
    # ================================
    # MÉTODOS DE SISTEMA
    # ================================
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica el estado de la API."""
        print("🔍 Verificando estado de la API...")
        response = self.session.get(f"{self.base_url}/health")
        return self._handle_response(response)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema (requiere autenticación)."""
        print("📊 Obteniendo estadísticas del sistema...")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        response = self.session.get(f"{self.base_url}/stats", headers=headers)
        return self._handle_response(response)
    
    # ================================
    # MÉTODOS DE USUARIOS
    # ================================
    
    def listar_usuarios(self) -> Dict[str, Any]:
        """Lista todos los usuarios (requiere autenticación)."""
        print("👥 Listando usuarios...")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        response = self.session.get(f"{self.base_url}/usuarios", headers=headers)
        return self._handle_response(response)
    
    def obtener_usuario(self, nombre: str) -> Dict[str, Any]:
        """Obtiene información de un usuario (requiere autenticación)."""
        print(f"👤 Obteniendo usuario: {nombre}")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        response = self.session.get(f"{self.base_url}/usuarios/{nombre}", headers=headers)
        return self._handle_response(response)
    
    def crear_usuario(self, nombre: str) -> Dict[str, Any]:
        """Crea un nuevo usuario (requiere autenticación)."""
        print(f"➕ Creando usuario: {nombre}")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        data = {"nombre": nombre}
        response = self.session.post(f"{self.base_url}/usuarios", json=data, headers=headers)
        return self._handle_response(response)
    
    def crear_admin(self, nombre: str, contraseña: str) -> Dict[str, Any]:
        """Crea un nuevo administrador."""
        print(f"🔑 Creando administrador: {nombre}")
        data = {"nombre": nombre, "contraseña": contraseña}
        response = self.session.post(f"{self.base_url}/usuarios/admin", json=data)
        return self._handle_response(response)
    
    def eliminar_usuario(self, nombre: str) -> Dict[str, Any]:
        """Elimina un usuario (requiere autenticación de admin)."""
        print(f"🗑️ Eliminando usuario: {nombre}")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        response = self.session.delete(f"{self.base_url}/usuarios/{nombre}", headers=headers)
        return self._handle_response(response)
    
    # ================================
    # MÉTODOS DE AUTENTICACIÓN
    # ================================
    
    def login(self, nombre: str, contraseña: str) -> Dict[str, Any]:
        """Inicia sesión con un usuario y guarda los tokens JWT."""
        print(f"🔐 Iniciando sesión: {nombre}")
        data = {"nombre": nombre, "contraseña": contraseña}
        response = self.session.post(f"{self.base_url}/auth/login", json=data)
        result = self._handle_response(response)
        
        # Si el login es exitoso, guardar los tokens
        if result.get("access_token"):
            self.access_token = result["access_token"]
            self.refresh_token = result.get("refresh_token")
            print(f"✅ Autenticado exitosamente como {nombre}")
            print(f"🔑 Token obtenido (válido por {result.get('expires_in', 'N/A')} segundos)")
        
        return result
    
    def establecer_password(self, nombre: str, contraseña: str) -> Dict[str, Any]:
        """Establece la contraseña inicial de un usuario."""
        print(f"🔒 Estableciendo contraseña para: {nombre}")
        data = {"nombre": nombre, "contraseña": contraseña}
        response = self.session.post(f"{self.base_url}/auth/set-password", json=data)
        return self._handle_response(response)
    
    def cambiar_password(self, nombre: str, contraseña_actual: str, contraseña_nueva: str) -> Dict[str, Any]:
        """Cambia la contraseña de un usuario."""
        print(f"🔄 Cambiando contraseña para: {nombre}")
        data = {
            "nombre": nombre,
            "contraseña_actual": contraseña_actual,
            "contraseña_nueva": contraseña_nueva
        }
        response = self.session.post(f"{self.base_url}/auth/change-password", json=data)
        return self._handle_response(response)
    
    def resetear_password(self, nombre_admin: str, nombre_usuario: str) -> Dict[str, Any]:
        """Resetea la contraseña de un usuario."""
        print(f"🔄 Reseteando contraseña de {nombre_usuario} (admin: {nombre_admin})")
        data = {"nombre_admin": nombre_admin, "nombre_usuario": nombre_usuario}
        response = self.session.post(f"{self.base_url}/auth/reset-password", json=data)
        return self._handle_response(response)
    
    def refresh_token_jwt(self) -> Dict[str, Any]:
        """Renueva el token JWT usando el refresh token."""
        print("🔄 Renovando token JWT...")
        if not self.refresh_token:
            print("⚠️ No hay refresh token disponible. Hacer login primero.")
            return {"success": False, "error": "No hay refresh token"}
        
        data = {"refresh_token": self.refresh_token}
        response = self.session.post(f"{self.base_url}/auth/refresh", json=data)
        result = self._handle_response(response)
        
        # Si el refresh es exitoso, actualizar tokens
        if result.get("access_token"):
            self.access_token = result["access_token"]
            self.refresh_token = result.get("refresh_token", self.refresh_token)
            print("✅ Tokens renovados exitosamente")
        
        return result
    
    def logout(self) -> Dict[str, Any]:
        """Cierra la sesión y limpia los tokens."""
        print("🚪 Cerrando sesión...")
        headers = self._get_auth_headers()
        if headers:
            response = self.session.post(f"{self.base_url}/auth/logout", headers=headers)
            result = self._handle_response(response)
        else:
            result = {"success": True, "message": "No había sesión activa"}
        
        # Limpiar tokens localmente
        self.access_token = None
        self.refresh_token = None
        print("🔐 Tokens eliminados localmente")
        return result
    
    def get_current_user(self) -> Dict[str, Any]:
        """Obtiene información del usuario actual autenticado."""
        print("👤 Obteniendo información del usuario actual...")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        response = self.session.get(f"{self.base_url}/auth/me", headers=headers)
        return self._handle_response(response)
    
    # ================================
    # MÉTODOS DE TAREAS
    # ================================
    
    def listar_tareas(self) -> Dict[str, Any]:
        """Lista todas las tareas (requiere autenticación)."""
        print("📋 Listando tareas...")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        response = self.session.get(f"{self.base_url}/tareas", headers=headers)
        return self._handle_response(response)
    
    def obtener_tarea(self, nombre: str) -> Dict[str, Any]:
        """Obtiene información de una tarea (requiere autenticación)."""
        print(f"📝 Obteniendo tarea: {nombre}")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        response = self.session.get(f"{self.base_url}/tareas/{nombre}", headers=headers)
        return self._handle_response(response)
    
    def obtener_tareas_usuario(self, nombre_usuario: str, incluir_finalizadas: bool = True) -> Dict[str, Any]:
        """Obtiene las tareas de un usuario (requiere autenticación)."""
        print(f"📋 Obteniendo tareas del usuario: {nombre_usuario}")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        params = {"incluir_finalizadas": incluir_finalizadas}
        response = self.session.get(f"{self.base_url}/tareas/usuario/{nombre_usuario}", params=params, headers=headers)
        return self._handle_response(response)
    
    def crear_tarea(self, nombre: str, descripcion: str) -> Dict[str, Any]:
        """Crea una nueva tarea (requiere autenticación)."""
        print(f"➕ Creando tarea: {nombre}")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        data = {"nombre": nombre, "descripcion": descripcion}
        response = self.session.post(f"{self.base_url}/tareas", json=data, headers=headers)
        return self._handle_response(response)
    
    def asignar_usuario_tarea(self, nombre_tarea: str, nombre_usuario: str) -> Dict[str, Any]:
        """Asigna un usuario a una tarea (requiere autenticación)."""
        print(f"👤➡️📝 Asignando {nombre_usuario} a la tarea {nombre_tarea}")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        data = {"nombre_tarea": nombre_tarea, "nombre_usuario": nombre_usuario}
        response = self.session.post(f"{self.base_url}/tareas/asignar", json=data, headers=headers)
        return self._handle_response(response)
    
    def finalizar_tarea(self, nombre_tarea: str) -> Dict[str, Any]:
        """Finaliza una tarea (requiere autenticación)."""
        print(f"✅ Finalizando tarea: {nombre_tarea}")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        data = {"nombre_tarea": nombre_tarea}
        response = self.session.post(f"{self.base_url}/tareas/finalizar", json=data, headers=headers)
        return self._handle_response(response)
    
    def agregar_comentario(self, nombre_tarea: str, comentario: str, nombre_usuario: str) -> Dict[str, Any]:
        """Agrega un comentario a una tarea (requiere autenticación)."""
        print(f"💬 Agregando comentario a la tarea: {nombre_tarea}")
        headers = self._get_auth_headers()
        if not headers:
            print("⚠️ No hay token de autenticación. Hacer login primero.")
            return {"success": False, "error": "No hay token de autenticación"}
        data = {
            "nombre_tarea": nombre_tarea,
            "comentario": comentario,
            "nombre_usuario": nombre_usuario
        }
        response = self.session.post(f"{self.base_url}/tareas/comentario", json=data, headers=headers)
        return self._handle_response(response)


def demo_completa():
    """Ejecuta una demostración completa de la API con autenticación JWT."""
    print("🚀 === DEMO DE LA API DE GESTIÓN DE TAREAS (JWT) ===\n")
    
    # Crear cliente
    client = TaskAPIClient()
    
    # 1. Health check
    print("1️⃣ === VERIFICACIÓN DE ESTADO ===")
    health = client.health_check()
    print(f"Estado: {health}")
    print()
    
    # 2. Crear administrador
    print("2️⃣ === CREACIÓN DE ADMINISTRADOR ===")
    admin_result = client.crear_admin("admin", "admin123")
    print(f"Resultado: {admin_result}")
    print()
    
    # 3. Login como administrador
    print("3️⃣ === AUTENTICACIÓN COMO ADMINISTRADOR ===")
    login_result = client.login("admin", "4321")
    print(f"Login: {login_result}")
    if not login_result.get("access_token"):
        print("❌ No se pudo autenticar. Terminando demo.")
        return
    print()
    
    # 4. Crear usuarios
    print("4️⃣ === CREACIÓN DE USUARIOS ===")
    user1_result = client.crear_usuario("juan")
    print(f"Usuario juan: {user1_result}")
    
    user2_result = client.crear_usuario("maria")
    print(f"Usuario maria: {user2_result}")
    print()
    
    # 5. Establecer contraseñas
    print("5️⃣ === ESTABLECER CONTRASEÑAS ===")
    pass1_result = client.establecer_password("juan", "juan123")
    print(f"Contraseña juan: {pass1_result}")
    
    pass2_result = client.establecer_password("maria", "maria123")
    print(f"Contraseña maria: {pass2_result}")
    print()
    
    # 6. Logout y login como usuario normal
    print("6️⃣ === CAMBIO DE USUARIO ===")
    logout_result = client.logout()
    print(f"Logout: {logout_result}")
    
    login_juan = client.login("juan", "juan123")
    print(f"Login juan: {login_juan}")
    if not login_juan.get("access_token"):
        print("❌ No se pudo autenticar como juan.")
        return
    print()
    
    # 7. Crear tareas
    print("7️⃣ === CREACIÓN DE TAREAS ===")
    task1_result = client.crear_tarea("Desarrollo API", "Desarrollar API REST para el sistema")
    print(f"Tarea 1: {task1_result}")
    
    task2_result = client.crear_tarea("Testing", "Realizar pruebas de la aplicación")
    print(f"Tarea 2: {task2_result}")
    
    task3_result = client.crear_tarea("Documentación", "Escribir documentación técnica")
    print(f"Tarea 3: {task3_result}")
    print()
    
    # 8. Asignar usuarios a tareas
    print("8️⃣ === ASIGNACIÓN DE TAREAS ===")
    asign1_result = client.asignar_usuario_tarea("Desarrollo API", "juan")
    print(f"Asignación 1: {asign1_result}")
    
    asign2_result = client.asignar_usuario_tarea("Testing", "maria")
    print(f"Asignación 2: {asign2_result}")
    
    asign3_result = client.asignar_usuario_tarea("Documentación", "juan")
    print(f"Asignación 3: {asign3_result}")
    print()
    
    # 9. Información del usuario actual
    print("9️⃣ === INFORMACIÓN DEL USUARIO ACTUAL ===")
    current_user = client.get_current_user()
    print(f"Usuario actual: {current_user}")
    print()
    
    # 10. Agregar comentarios
    print("🔟 === COMENTARIOS EN TAREAS ===")
    com1_result = client.agregar_comentario("Desarrollo API", "Iniciando desarrollo con FastAPI", "juan")
    print(f"Comentario 1: {com1_result}")
    
    com2_result = client.agregar_comentario("Testing", "Preparando casos de prueba", "maria")
    print(f"Comentario 2: {com2_result}")
    print()
    
    # 11. Listar todo
    print("1️⃣1️⃣ === LISTADOS ===")
    usuarios = client.listar_usuarios()
    print(f"Usuarios: {usuarios}")
    print()
    
    tareas = client.listar_tareas()
    print(f"Tareas: {tareas}")
    print()
    
    # 12. Tareas de usuario específico
    print("1️⃣2️⃣ === TAREAS POR USUARIO ===")
    tareas_juan = client.obtener_tareas_usuario("juan")
    print(f"Tareas de Juan: {tareas_juan}")
    print()
    
    # 13. Finalizar una tarea
    print("1️⃣3️⃣ === FINALIZAR TAREA ===")
    finalizar_result = client.finalizar_tarea("Testing")
    print(f"Finalizar Testing: {finalizar_result}")
    print()
    
    # 14. Probar refresh token
    print("1️⃣4️⃣ === REFRESH TOKEN ===")
    refresh_result = client.refresh_token_jwt()
    print(f"Refresh token: {refresh_result}")
    print()
    
    # 15. Login como admin para estadísticas
    print("1️⃣5️⃣ === ESTADÍSTICAS (REQUIERE ADMIN) ===")
    client.logout()
    admin_login = client.login("admin", "admin123")
    if admin_login.get("access_token"):
        stats = client.get_stats()
        print(f"Estadísticas: {stats}")
    print()
    
    # 16. Logout final
    print("1️⃣6️⃣ === LOGOUT FINAL ===")
    final_logout = client.logout()
    print(f"Logout final: {final_logout}")
    print()
    
    print("✅ === DEMO COMPLETADA ===")


def demo_interactiva():
    """Demo interactiva donde el usuario puede probar diferentes endpoints."""
    print("🎮 === DEMO INTERACTIVA DE LA API ===\n")
    
    client = TaskAPIClient()
    
    # Verificar que la API está disponible
    health = client.health_check()
    if not health.get("status"):
        print("❌ La API no está disponible. Asegúrate de que esté ejecutándose.")
        return
    
    print("✅ API disponible. ¡Empezemos!\n")
    
    while True:
        print("\n" + "="*50)
        print("MENÚ DE OPCIONES:")
        print("="*50)
        print("👥 USUARIOS:")
        print("  1. Crear administrador")
        print("  2. Crear usuario")
        print("  3. Listar usuarios")
        print("  4. Obtener usuario específico")
        print("  5. Eliminar usuario")
        print()
        print("🔐 AUTENTICACIÓN:")
        print("  6. Establecer contraseña")
        print("  7. Login")
        print("  8. Cambiar contraseña")
        print("  9. Refresh token")
        print(" 10. Obtener usuario actual")
        print(" 11. Logout")
        print()
        print("📋 TAREAS:")
        print(" 12. Crear tarea")
        print(" 13. Listar tareas")
        print(" 14. Obtener tarea específica")
        print(" 15. Asignar usuario a tarea")
        print(" 16. Agregar comentario")
        print(" 17. Finalizar tarea")
        print(" 18. Tareas de usuario")
        print()
        print("📊 SISTEMA:")
        print(" 19. Ver estadísticas")
        print(" 20. Health check")
        print()
        print("  0. Salir")
        print("="*50)
        
        try:
            opcion = input("Selecciona una opción: ").strip()
            
            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            
            elif opcion == "1":
                nombre = input("Nombre del administrador: ")
                contraseña = input("Contraseña: ")
                resultado = client.crear_admin(nombre, contraseña)
                print(f"Resultado: {resultado}")
            
            elif opcion == "2":
                nombre = input("Nombre del usuario: ")
                resultado = client.crear_usuario(nombre)
                print(f"Resultado: {resultado}")
            
            elif opcion == "3":
                resultado = client.listar_usuarios()
                print(f"Usuarios: {resultado}")
            
            elif opcion == "4":
                nombre = input("Nombre del usuario: ")
                resultado = client.obtener_usuario(nombre)
                print(f"Usuario: {resultado}")
            
            elif opcion == "5":
                nombre = input("Nombre del usuario a eliminar: ")
                resultado = client.eliminar_usuario(nombre)
                print(f"Resultado: {resultado}")
            
            elif opcion == "6":
                nombre = input("Nombre del usuario: ")
                contraseña = input("Nueva contraseña: ")
                resultado = client.establecer_password(nombre, contraseña)
                print(f"Resultado: {resultado}")
            
            elif opcion == "7":
                nombre = input("Nombre de usuario: ")
                contraseña = input("Contraseña: ")
                resultado = client.login(nombre, contraseña)
                print(f"Login: {resultado}")
            
            elif opcion == "8":
                nombre = input("Nombre del usuario: ")
                actual = input("Contraseña actual: ")
                nueva = input("Nueva contraseña: ")
                resultado = client.cambiar_password(nombre, actual, nueva)
                print(f"Resultado: {resultado}")
            
            elif opcion == "9":
                resultado = client.refresh_token_jwt()
                print(f"Refresh: {resultado}")
            
            elif opcion == "10":
                resultado = client.get_current_user()
                print(f"Usuario actual: {resultado}")
            
            elif opcion == "11":
                resultado = client.logout()
                print(f"Logout: {resultado}")
            
            elif opcion == "12":
                nombre = input("Nombre de la tarea: ")
                descripcion = input("Descripción: ")
                resultado = client.crear_tarea(nombre, descripcion)
                print(f"Resultado: {resultado}")
            
            elif opcion == "13":
                resultado = client.listar_tareas()
                print(f"Tareas: {resultado}")
            
            elif opcion == "14":
                nombre = input("Nombre de la tarea: ")
                resultado = client.obtener_tarea(nombre)
                print(f"Tarea: {resultado}")
            
            elif opcion == "15":
                tarea = input("Nombre de la tarea: ")
                usuario = input("Nombre del usuario: ")
                resultado = client.asignar_usuario_tarea(tarea, usuario)
                print(f"Resultado: {resultado}")
            
            elif opcion == "16":
                tarea = input("Nombre de la tarea: ")
                comentario = input("Comentario: ")
                usuario = input("Usuario que comenta: ")
                resultado = client.agregar_comentario(tarea, comentario, usuario)
                print(f"Resultado: {resultado}")
            
            elif opcion == "17":
                tarea = input("Nombre de la tarea: ")
                resultado = client.finalizar_tarea(tarea)
                print(f"Resultado: {resultado}")
            
            elif opcion == "18":
                usuario = input("Nombre del usuario: ")
                incluir = input("¿Incluir finalizadas? (s/n): ").lower() == 's'
                resultado = client.obtener_tareas_usuario(usuario, incluir)
                print(f"Tareas: {resultado}")
            
            elif opcion == "19":
                resultado = client.get_stats()
                print(f"Estadísticas: {resultado}")
            
            elif opcion == "20":
                resultado = client.health_check()
                print(f"Health: {resultado}")
            
            else:
                print("❌ Opción no válida")
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    print("🔧 Cliente de la API de Gestión de Tareas")
    print("="*40)
    print("Opciones:")
    print("1. Demo automática completa")
    print("2. Demo interactiva")
    print("0. Salir")
    
    try:
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            demo_completa()
        elif opcion == "2":
            demo_interactiva()
        elif opcion == "0":
            print("👋 ¡Hasta luego!")
        else:
            print("❌ Opción no válida")
    
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {e}")