from usuario import Usuario
from tarea import Tarea
from utils import cargar_datos, guardar_datos , generar_password, hay_admin, guardar_json
import getpass
import sys
import os

# archivos de datos
USUARIOS = "usuarios.dat"
TAREAS = "tareas.dat"
TAREAS_FINALIZADAS = "tareas_finalizadas.json"

####### funciones de menus #######
def menu_usuario(rol, usuario):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        st = f"\n#{' Menú ':*^88}#" +"\n"
        st += f"{'#':<40}{'Bienvenido: '+usuario.nombre:<49}{'#'}\n"
        st += f"{'#':<40}"+f"{'1. Cambiar Contraseña':<49}"+"#" +"\n"
        st += f"{'#':<40}"+f"{'2. Ver tus Tareas':<49}"+"#" +"\n"
        st += f"{'#':<40}"+f"{'3. Desloguarse':<49}"+"#" +"\n"
        st += f"{'#':<40}"+f"{'4. Salir':<49}"+"#" +"\n"
        if rol == "admin":
            st += f"{'#':<40}"+f"{'Opciones del Administrador':<49}"+"#" +"\n"
            st += f"{'#':<40}"+f"{'5. Crear Usuario':<49}"+"#" +"\n"
            st += f"{'#':<40}"+f"{'6. Ver Usuarios':<49}"+"#" +"\n"
            st += f"{'#':<40}"+f"{'7. Eliminar Usuario':<49}"+"#" +"\n"
            st += f"{'#':<40}"+f"{'8. Crear Tarea':<49}"+"#" +"\n"
        st += f"{'#'*90}"
        print(st)

        opcion = input("Seleccione una opción: ")
        if opcion == '1':
            cambiar_password(usuario)
        elif opcion == '2':
            ver_tareas(usuario)
        elif opcion == '3':
            main()
        elif opcion == '4':
            sys.exit()             
        elif opcion == '5' and rol == 'admin':
            crear_usuario()
        elif opcion == '6' and rol == 'admin':
            menu_usuarios(cargar_datos(USUARIOS))
            input("Presione Enter para continuar...")
        elif opcion == "7" and rol == 'admin':
            eliminar_usuario()
        elif opcion == "8" and rol == 'admin':
            crear_tarea(cargar_datos(TAREAS))
        else:
            pass
            
def menu_usuarios(usuarios):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{'#':<35}"+"**** Lista de Usuarios ****")
    print(f"{'#':<35}"+"| Id |  Nombre  |    Rol  |")
    print(f"{'#':<35}"+"="*27)
    us = {}
    for i, user in enumerate(usuarios, start=1):
        us[str(i)]=user.nombre
        print(f"{'#':<35}"+f"|{i:^4}|{user.nombre:^10}|{user.rol:^9}|")
    print(f"{'#':<35}"+"*"*27)
    return us

def menu_tareas(tareas, usuario):
    os.system('cls' if os.name == 'nt' else 'clear')
    if usuario.rol != 'admin':
        tareas = [tarea for tarea in tareas if usuario.nombre in tarea.usuarios_asignados] 
    print(f"{' Lista de Tareas ':*^90}")
    print(f"| Id  |{'Nombre':^35}|{'Estado':^24}|{'Fecha Creación':^21}|")
    print("="*90)
    tr = {}
    if not tareas:
        print(f'{"No hay tareas disponibles.:":^90}')
    else:
        for i, tarea in enumerate(tareas, start=1):
            tr[str(i)] = tarea
            estado = "*" if tarea.estado == "pendiente" else "X"
            print(f"|{i}. {estado} |{tarea.nombre:^35}| Estado: {tarea.estado:^15}| {tarea.fecha_creacion:>10} |")
    print("*"*90)
    return tr

def asignar_usuario_tarea(tarea):
    usuarios = cargar_datos(USUARIOS)
    us = menu_usuarios(usuarios)
    asignados = input("Ingrese los ids de los usuarios a asignar separados por comas: ").split(',')
    for user_id in asignados:
        user_id = user_id.strip()
        if user_id in us:
            tarea.agregar_usuario(us[user_id])
            # guardar_datos(tareas, TAREAS)
            print(f"Usuario :{us[user_id]} asignado con éxito.")
        elif user_id in (user.nombre for user in usuarios):
            tarea.agregar_usuario(user_id)
            print(f"Usuario :{user_id} asignado con éxito.")
        else:
            print("Usuario no encontrado.")    

def eliminar_usuario_tarea(tarea):
    usuarios_asignados = tarea.usuarios_asignados
    print("Usuarios asignados a la tarea:")
    us = menu_usuarios([x for x in  cargar_datos(USUARIOS) 
                        if x.nombre in usuarios_asignados])
    eliminar = input("Ingrese los nombres o ids de los usuarios a eliminar separados por comas: ").split(',')
    # print(eliminar)
    for usuario in eliminar:
        usuario = usuario.strip()
        if usuario in usuarios_asignados:
            tarea.quitar_usuario(usuario)
            print(f"{usuario} eliminado con éxito de la tarea: {tarea.nombre}")
        elif usuario in us:
            tarea.quitar_usuario(us[usuario])
            print(f"{us[usuario]} eliminado con éxito de la tarea: {tarea.nombre}")
        else:
            print("Usuario no encontrado.")

def ver_tareas(usuario):
    tareas = cargar_datos(TAREAS)
    tarea = menu_tareas(tareas, usuario)
    tarea_id = input("Ingrese el id de la tarea para ver detalles: ")
    if tarea_id in tarea:
        tarea_asignada = tarea[tarea_id]
        print(tarea_asignada.mostrar_info())
        if tarea_asignada.estado == "pendiente":
            comentario = input("Ingrese una Accion (o presione Enter para omitir): ")
            if comentario:
                tarea_asignada.agregar_comentario(comentario, usuario.nombre)
                guardar_datos(tareas, TAREAS)
                print("Acción agregado con éxito.")
        else:
            input("Presione Enter para continuar...")
            if usuario.rol == 'admin' and input("Desea activar la tarea? (s/n): ").lower() == 's':
                tarea_asignada.activar_tarea()
                guardar_datos(tareas, TAREAS)
                print("Tarea activada con éxito.")

        if usuario.rol == 'admin':
            while True:
                print("\nOpciones de administración de tareas:")
                print("1. Asignar usuarios a la tarea")
                print("2. Eliminar usuarios de la tarea")
                print("3. Finalizar tarea")
                print("4. Eliminar Tarea")
                print("5. Volver al menú anterior")
                opcion = input("Seleccione una opción: ")
                
                if opcion == '1':
                    asignar_usuario_tarea(tarea_asignada)
                    guardar_datos(tareas, TAREAS)
                    # input("Presione Enter para continuar...")    
                
                elif opcion == '2':
                    eliminar_usuario_tarea(tarea_asignada)
                    guardar_datos(tareas, TAREAS)
                
                elif opcion == '3':
                    tarea_asignada.finalizar_tarea()
                    guardar_datos(tareas, TAREAS)
                    print("Tarea finalizada con éxito.")
                    break
                
                elif opcion == "4":
                    tareas = [tarea for tarea in tareas if tarea.nombre != tarea_asignada.nombre]
                    guardar_datos(tareas, TAREAS)
                    print(f"Tarea '{tarea_asignada.nombre}' eliminada con éxito.")
                    guardar_json(tarea_asignada.to_json(), TAREAS_FINALIZADAS)
                    break

                elif opcion == '5':
                    break
                
                else:
                    print("Opción no válida. Intente de nuevo.")
    else:
        print("Tarea no encontrada.")
    
def crear_admin(usuarios):
    print("No existe un administrador. Creando uno nuevo...")
    nombre_admin = "admin"
    # password_admin = generar_password()
    password_admin = "1234"
    usuarios.append(Usuario(nombre_admin, password_admin, rol="admin"))
    guardar_datos(usuarios, USUARIOS)
    print(f"Administrador '{nombre_admin}' creado con contraseña: {password_admin}")
    input("Presione Enter para continuar...")

def crear_usuario():
    usuarios = cargar_datos(USUARIOS)   
    nombre = input("Ingrese el nombre del nuevo usuario: ")
    if nombre not in (user.nombre for user in usuarios):
        password = generar_password(6)
        usuarios.append(Usuario(nombre, password))
        guardar_datos(usuarios , USUARIOS)
        print(f"Usuario '{nombre}' creado con contraseña: {password}")
    else:
        print("El usuario ya existe.")
    input("Presione Enter para continuar...")

def eliminar_usuario():
    usuarios = cargar_datos(USUARIOS)
    us = menu_usuarios(usuarios)
    nombre = input("Ingrese el nombre o id del usuario a eliminar: ")
    if nombre in us:
        usuarios = [user for user in usuarios if user.nombre != us[nombre]]
        print(f"Usuario '{us[nombre]}' eliminado con éxito.")
    elif nombre in us.values():
        usuarios = [user for user in usuarios if user.nombre != nombre]
        print(f"Usuario '{nombre}' eliminado con éxito.")
    else:
        print("Usuario Inexsistente")
    guardar_datos(usuarios, USUARIOS)
    input("Presione Enter para continuar...")
    
def cambiar_password(usuario):
    usuarios = cargar_datos(USUARIOS)
    for user in usuarios:
        if user.nombre == usuario.nombre:
            break
    actual_password =  getpass.getpass("Ingrese su contraseña actual: ")
    nueva_password = getpass.getpass("Ingrese su nueva contraseña: ")
    if user.verificar_password(actual_password) and nueva_password != actual_password:
        chek_password = getpass.getpass("Repita su nueva contraseña: ")
        if nueva_password == chek_password:
            user.cambiar_password(nueva_password)
            guardar_datos(usuarios, USUARIOS)
            print("Contraseña cambiada con éxito.")
        else:
            print("Contraseñas no coinciden")
            return
    else:
        print("Contraseña incorrecta o igual a la anterior.")
    input("Presione Enter para continuar...")

def crear_tarea(tareas):
    nombre = input("Ingrese el nombre de la tarea: ")
    if nombre in (tarea.nombre for tarea in tareas):
        print("La tarea ya existe.")
        return
    descripcion = input("Ingrese la descripción de la tarea: ")
    tarea = Tarea(nombre, descripcion)
    tareas.append(tarea)
    guardar_datos(tareas, TAREAS)
    print(f"Tarea '{nombre}' creada con éxito.")
    input("Presione Enter para continuar...")

def login(usuarios):
    nombre = input("Ingrese su nombre de usuario: ")
    intentos = 0
    while intentos < 5:
        contraseña = getpass.getpass("Ingrese su contraseña: ")
        for user in usuarios:
            if user.nombre == nombre and user.verificar_password(contraseña):
                return user
        else:
            print("Usuario o contraseña incorrectos.")
            intentos += 1
            
            if intentos >= 5:
                print("Demasiados intentos fallidos. Cerrando el programa.")
                sys.exit()

def main():
    os.system('cls' if os.name == 'nt' else 'clear') 
    datos = cargar_datos(USUARIOS)
    if hay_admin(datos):
        user = login(datos)
        menu_usuario(user.rol, user)
    else:
        crear_admin(datos)
        input("Presione Enter para continuar...")
        main()

if __name__ == "__main__":
    main()