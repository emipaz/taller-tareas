"""Interfaz de consola mejorada para el sistema de gestión de tareas.

Este módulo contiene la interfaz de usuario por consola con Rich,
proporcionando una experiencia visual mejorada con colores, estilos
y elementos interactivos para la gestión de tareas.

La aplicación utiliza Rich para:
    - Interfaces coloridas y atractivas
    - Tablas formateadas para mostrar datos
    - Mensajes con iconos y colores semánticos
    - Paneles informativos y alertas
    - Barras de progreso y elementos interactivos

Author:
    Sistema de Gestión de Tareas
    
Dependencies:
    - rich           : Para interfaz visual mejorada
    - getpass        : Para entrada segura de contraseñas
    - gestor_sistema : Lógica de negocio del sistema

Note: 
    Toda la lógica de negocio está delegada al GestorSistema,
    manteniendo la separación de responsabilidades.
"""
# importaciones estándar
import os
import sys
import getpass
from typing import Optional, List

# Rich imports para interfaz mejorada
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.align import Align
from rich import box
from rich.padding import Padding
from rich.columns import Columns

# Imports del sistema
from core import GestorSistema
from core import Usuario
from core import Tarea


class InterfazConsola:
    """Interfaz de consola mejorada para interactuar con el sistema de tareas.
    
    Esta clase proporciona una interfaz visual rica y colorida usando
    la biblioteca Rich, mejorando significativamente la experiencia
    del usuario con elementos visuales modernos.
    
    Attributes:
        console (Console)                  : Instancia de Rich Console para output mejorado.
        gestor (GestorSistema)             : Gestor del sistema de tareas.
        usuario_actual (Optional[Usuario]) : Usuario actualmente logueado.
        
    Color Scheme:
        - Verde    : Éxito, confirmaciones positivas
        - Rojo     : Errores, advertencias críticas  
        - Azul     : Información, títulos principales
        - Amarillo : Advertencias, información importante
        - Cyan     : Elementos interactivos, menús
        - Magenta  : Datos del usuario, elementos destacados
    """
    
    def __init__(self):
        """Inicializa la interfaz de consola con Rich.
        
        Configura Rich Console y el gestor del sistema,
        estableciendo los componentes necesarios para
        la interfaz visual mejorada.
        """
        # Configurar consola Rich con ancho apropiado
        self.console = Console(width=120)
        
        # Inicializar sistema
        self.gestor = GestorSistema()
        self.usuario_actual: Optional[Usuario] = None
        
        # Configurar colores del tema
        self.colors = {
            'success'  : 'green',
            'error'    : 'red', 
            'info'     : 'blue',
            'warning'  : 'yellow',
            'accent'   : 'cyan',
            'user'     : 'magenta',
            'muted'    : 'dim white'
        }
    
    ###########################
    # UTILIDADES BÁSICAS
    ###########################

    def limpiar_pantalla(self) -> None:
        """Limpia la pantalla de la consola.
        
        Utiliza comandos del sistema operativo para limpiar
        la pantalla, manteniendo compatibilidad multiplataforma.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def mostrar_titulo(self, titulo: str, subtitulo: str = "") -> None:
        """Muestra un título principal con estilo Rich centrado.
        
        Args:
            titulo    : Texto del título principal.
            subtitulo : Texto opcional del subtítulo.
            
        Note:
            Limpia la pantalla y muestra un panel centrado
            con el título en estilo destacado.
        """
        self.limpiar_pantalla()
        
        # Crear contenido del título
        if subtitulo:
            content = f"[bold blue]{titulo}[/bold blue]\n[dim]{subtitulo}[/dim]"
        else:
            content = f"[bold blue]{titulo}[/bold blue]"
            
        # Mostrar panel centrado
        panel = Panel(
            Align.center(content),
            border_style = "blue",
            padding      = (1, 2)
        )
        self.console.print("\n")
        self.console.print(Align.center(panel))
        self.console.print("\n")
    
    def mostrar_mensaje(self, mensaje: str, tipo: str = "info", icono: bool = True) -> None:
        """Muestra un mensaje con estilo y color según el tipo.
        
        Args:
            mensaje    : Texto del mensaje a mostrar.
            tipo       : Tipo de mensaje ('success', 'error', 'warning', 'info').
            icono      : Si mostrar icono según el tipo de mensaje.
            
        Examples:
            >>> interfaz.mostrar_mensaje("Operación exitosa", "success")
            >>> interfaz.mostrar_mensaje("Error crítico", "error")
        """
        # Definir iconos y estilos por tipo
        config = {
            'success' : {'icon': '✅', 'style': 'green'},
            'error'   : {'icon': '❌', 'style': 'red'},
            'warning' : {'icon': '⚠️', 'style': 'yellow'},
            'info'    : {'icon': 'ℹ️', 'style': 'blue'}
        }
        
        estilo = config.get(tipo, config['info'])
        icono_text = f"{estilo['icon']} " if icono else ""
        
        self.console.print(f"{icono_text}[{estilo['style']}]{mensaje}[/{estilo['style']}]")
    
    def esperar_enter(self, mensaje: str = "Presione [cyan]Enter[/cyan] para continuar...") -> None:
        """Espera que el usuario presione Enter con mensaje estilizado.
        
        Args:
            mensaje    : Mensaje personalizado a mostrar.
        """
        self.console.print(f"\n[dim]{mensaje}[/dim]")
        input()

    ###########################
    # AUTENTICACIÓN Y SESIÓN
    ###########################

    def iniciar_sesion(self) -> None:
        """Proceso mejorado de inicio de sesión con interfaz Rich.
        
        Proporciona una experiencia de login moderna con validaciones
        visuales, mensajes informativos y manejo de casos especiales
        como primer inicio de sesión.
        """
        self.mostrar_titulo('🔐 Inicio de Sesión', 'Acceso al Sistema de Gestión de Tareas')
        
        # Panel de bienvenida centrado
        bienvenida_panel = Panel(
            Align.center(
                "[blue]🏠 Bienvenido al Sistema de Gestión de Tareas[/blue]\n\n"
                "[dim]• Ingrese sus credenciales para acceder\n"
                "• Si es su primera vez, se le pedirá configurar una contraseña\n"
                "• Contacte al administrador si tiene problemas de acceso[/dim]"
            ),
            title="Sistema de Autenticación",
            border_style="blue"
        )
        self.console.print(Align.center(bienvenida_panel))
        
        # Solicitar nombre de usuario
        nombre = Prompt.ask(
            "\n[cyan]👤 Nombre de usuario[/cyan]",
            default="",
            show_default=False
        )
        
        if not nombre:
            self.mostrar_mensaje("Nombre de usuario requerido", "error")
            self.esperar_enter()
            return
        
        # Verificar si el usuario existe
        usuarios = self.gestor.cargar_usuarios()
        usuario_temp = None
        for u in usuarios:
            if u.nombre == nombre:
                usuario_temp = u
                break
        
        if not usuario_temp:
            self.mostrar_mensaje(f"Usuario '{nombre}' no encontrado", "error")
            self.esperar_enter()
            return
        
        # Caso especial: primer inicio de sesión (sin contraseña)
        if not usuario_temp.tiene_password():
            # Panel de bienvenida para primer usuario centrado
            primer_login_panel = Panel(
                Align.center(
                    f"[green]🎉 ¡Hola {nombre}![/green]\n\n"
                    "[blue]Es tu primera vez iniciando sesión.[/blue]\n"
                    "[yellow]Debes establecer una contraseña segura.[/yellow]\n\n"
                    "[dim]Requisitos de contraseña:\n"
                    "• Mínimo 4 caracteres\n"
                    "• Recomendado: usar letras, números y símbolos[/dim]"
                ),
                title="[bold green]🔐 Configuración Inicial[/bold green]",
                border_style="green"
            )
            self.console.print(Align.center(primer_login_panel))
            
            while True:
                nueva_password = getpass.getpass("🆕 Ingrese su nueva contraseña: ")
                
                if len(nueva_password) < 4:
                    self.mostrar_mensaje("La contraseña debe tener al menos 4 caracteres", "error")
                    continue
                
                confirmar_password = getpass.getpass("✅ Confirme su nueva contraseña: ")
                
                if nueva_password == confirmar_password:
                    exito, mensaje = self.gestor.establecer_password_inicial(nombre, nueva_password)
                    
                    if exito:
                        self.mostrar_mensaje(mensaje, "success")
                        self.usuario_actual = usuario_temp
                        self.esperar_enter()
                        return
                    else:
                        self.mostrar_mensaje(mensaje, "error")
                        self.esperar_enter()
                        return
                else:
                    self.mostrar_mensaje("Las contraseñas no coinciden. Inténtelo de nuevo", "warning")
        
        # Login normal con Rich
        self.console.print("\n[cyan]🔐 Autenticación de Usuario[/cyan]")
        intentos = 0
        while intentos < 5:
            contraseña = getpass.getpass("🔑 Ingrese su contraseña: ")
            
            usuario, mensaje = self.gestor.autenticar_usuario(nombre, contraseña)
            
            if usuario:
                self.usuario_actual = usuario
                # Mensaje de bienvenida exitoso centrado
                welcome_panel = Panel(
                    Align.center(
                        f"[green]🎉 ¡Bienvenido {usuario.nombre}![/green]\n\n"
                        f"[dim]Rol: {usuario.rol}\n"
                        f"Acceso autorizado exitosamente[/dim]"
                    ),
                    title="[bold green]✅ Acceso Concedido[/bold green]",
                    border_style="green"
                )
                self.console.print(Align.center(welcome_panel))
                self.esperar_enter()
                return
            else:
                self.mostrar_mensaje(mensaje, "error")
                intentos += 1
                
                if intentos >= 5:
                    # Panel de bloqueo por intentos centrado
                    bloqueo_panel = Panel(
                        Align.center(
                            "[red]🚫 Demasiados intentos fallidos[/red]\n\n"
                            "[yellow]Por seguridad, el sistema se cerrará.[/yellow]\n\n"
                            "[dim]Para mayor seguridad:\n"
                            "• Verifique sus credenciales\n"
                            "• Contacte al administrador si olvidó su contraseña[/dim]"
                        ),
                        title="[bold red]⚠️ Sistema Bloqueado[/bold red]",
                        border_style="red"
                    )
                    self.console.print(Align.center(bloqueo_panel))
                    sys.exit()
                else:
                    intentos_restantes = 5 - intentos
                    self.console.print(f"[yellow]Intentos restantes: {intentos_restantes}[/yellow]\n")

    def crear_admin_inicial(self) -> None:
        """Interfaz mejorada para crear el administrador inicial del sistema.
        
        Este proceso es crítico ya que establece el primer usuario
        administrador que podrá gestionar el sistema completo.
        """
        self.mostrar_titulo('⚙️ Configuración Inicial', 'Creación del administrador del sistema')
        
        # Panel de información crítica centrado
        setup_panel = Panel(
            Align.center(
                "[red]🚨 CONFIGURACIÓN INICIAL REQUERIDA[/red]\n\n"
                "[yellow]El sistema no tiene administradores registrados.[/yellow]\n\n"
                "[dim]• Este será el usuario principal del sistema\n"
                "• Tendrá permisos completos de administración\n"
                "• Podrá crear y gestionar otros usuarios\n"
                "• Es responsable de la gestión de tareas\n\n"
                "⚠️  Asegúrese de recordar estas credenciales[/dim]"
            ),
            title="[bold red]⛔ Sistema Sin Administradores[/bold red]",
            border_style="red"
        )
        self.console.print(Align.center(setup_panel))
        
        # Formulario de creación del admin
        self.console.print("\n[cyan]📝 Configuración del Administrador Principal[/cyan]")
        
        nombre = Prompt.ask(
            "[white]👑 Nombre del administrador[/white]",
            default="admin",
            show_default=True
        )
        
        if not nombre or not nombre.strip():
            self.mostrar_mensaje("El nombre del administrador es requerido", "error")
            self.esperar_enter()
            return
            
        # Solicitar contraseña usando getpass para mayor seguridad
        self.console.print("\n[dim]🔐 Configure una contraseña segura para el administrador:[/dim]")
        contraseña = getpass.getpass("🔑 Contraseña del administrador: ")
        
        if not contraseña or len(contraseña) < 4:
            self.mostrar_mensaje("La contraseña debe tener al menos 4 caracteres", "error")
            self.esperar_enter()
            return
        
        # Confirmar contraseña
        confirmar_contraseña = getpass.getpass("🔒 Confirme la contraseña: ")
        
        if contraseña != confirmar_contraseña:
            self.mostrar_mensaje("Las contraseñas no coinciden", "error")
            self.esperar_enter()
            return
        
        # Preview de la configuración
        preview_panel = Panel(
            f"[bold]👑 Administrador:[/bold] {nombre}\n"
            f"[bold]🔐 Contraseña:[/bold] {'*' * len(contraseña)}\n"
            f"[bold]🎯 Rol:[/bold] Administrador Principal\n"
            f"[bold]🚀 Permisos:[/bold] Completos",
            title="[bold green]✨ Configuración del Administrador[/bold green]",
            border_style="green"
        )
        self.console.print(preview_panel)
        
        if Confirm.ask("\n[green]¿Crear administrador con esta configuración?"):
            exito, mensaje = self.gestor.crear_admin(nombre, contraseña)
            
            if exito:
                self.mostrar_mensaje(mensaje, "success")
                self.console.print(
                    "\n[bold green]🎉 ¡Sistema configurado exitosamente![/bold green]\n"
                    "[dim]Ya puede iniciar sesión con las credenciales del administrador.[/dim]"
                )
            else:
                self.mostrar_mensaje(f"Error en la configuración: {mensaje}", "error")
        else:
            self.mostrar_mensaje("Configuración cancelada", "warning")
            self.console.print("[red]El sistema no puede funcionar sin un administrador.[/red]")
            
        self.esperar_enter()

    def cambiar_password_interfaz(self) -> None:
        """Interfaz mejorada para cambiar contraseña del usuario actual.
        
        Proporciona una experiencia visual mejorada con confirmaciones
        claras, validaciones en tiempo real y mensajes informativos
        usando Rich para mejor usabilidad.
        """
        self.mostrar_titulo('🔑 Cambiar Contraseña', 'Actualización de credenciales de seguridad')
        
        # Panel de confirmación centrado
        confirmacion_panel = Panel(
            Align.center(
                "[yellow]! Esta acción cambiará tu contraseña actual ¡[/yellow]\n\n"
                "¿Estás seguro de que deseas continuar?"
            ),
            title        ="[bold red]Confirmación Requerida[/bold red]",
            border_style = "yellow"
        )
        self.console.print(Align.center(confirmacion_panel))
        
        # Usar Rich Confirm para mejor UX
        if not Confirm.ask("\n[cyan]Proceder con el cambio de contraseña"):
            self.mostrar_mensaje("Operación cancelada por el usuario", "warning")
            self.esperar_enter()
            return
        
        self.console.print("\n[blue]Iniciando proceso de cambio de contraseña...[/blue]\n")
        
        # Solicitar contraseña actual
        actual_password = getpass.getpass("🔐 Ingrese su contraseña actual: ")
        
        if not actual_password:
            self.mostrar_mensaje("Operación cancelada - contraseña requerida", "error")
            self.esperar_enter()
            return
        
        # Solicitar nueva contraseña
        nueva_password = getpass.getpass("🆕 Ingrese su nueva contraseña: ")
        
        if not nueva_password:
            self.mostrar_mensaje("Operación cancelada - nueva contraseña requerida", "error")
            self.esperar_enter()
            return
        
        # Confirmar nueva contraseña
        confirmar_password = getpass.getpass("✅ Confirme su nueva contraseña: ")
        
        if nueva_password != confirmar_password:
            self.mostrar_mensaje("Las contraseñas no coinciden", "error")
            self.esperar_enter()
            return
        
        # Procesar cambio
        exito, mensaje = self.gestor.cambiar_password(
            self.usuario_actual.nombre, actual_password, nueva_password
        )
        
        # Mostrar resultado
        if exito:
            self.mostrar_mensaje(mensaje, "success")
        else:
            self.mostrar_mensaje(mensaje, "error")
            
        self.esperar_enter()

    ###########################
    # MENÚ PRINCIPAL
    ###########################

    def mostrar_pantalla_inicio(self) -> None:
        """Muestra una pantalla de inicio atractiva con Rich.
        
        Presenta el sistema con un diseño moderno que incluye
        título, versión y información básica del sistema.
        """
        self.limpiar_pantalla()
        
        # Crear panel de bienvenida principal
        titulo_arte = """
    ╔═══════════════════════════════════════════════════════════╗
    ║              🎯 SISTEMA DE GESTIÓN DE TAREAS              ║
    ║                                                           ║
    ║        Una solución moderna para organizar tu trabajo     ║
    ╚═══════════════════════════════════════════════════════════╝
        """
        
        inicio_panel = Panel(
            Align.center(titulo_arte),
            title        = "[bold blue]🚀 Bienvenido[/bold blue]",
            subtitle     = "[dim]v1.0 - Desarrollado con Rich[/dim]",
            border_style = "blue"
        )
        
        self.console.print("\n" * 2)
        self.console.print(inicio_panel)
        
        # Información del sistema
        info_texto = Text.assemble(
            ("💼 ", "bold yellow"), ("Gestión eficiente de tareas\n", "white"),
            ("👥 ", "bold cyan"), ("Control de usuarios y permisos\n", "white"),
            ("📊 ", "bold green"), ("Reportes y estadísticas\n", "white"),
            ("🔐 ", "bold red"), ("Autenticación segura\n", "white")
        )
        
        info_panel = Panel(
            Align.center(info_texto),
            title        = "[bold green]✨ Características[/bold green]",
            border_style = "green"
        )
        
        self.console.print("\n")
        self.console.print(info_panel)
        self.esperar_enter("\n[cyan]Presione [bold]Enter[/bold] para comenzar...[/cyan]")

    def mostrar_menu_principal(self, usuario: Usuario) -> str:
        """Muestra el menú principal con tabla Rich estilizada.
        
        Args:
            usuario: Usuario actual logueado.
            
        Returns:
            Opción seleccionada por el usuario.
            
        Note:
            Crea una tabla interactiva con opciones diferenciadas
            por colores según el tipo de usuario (admin/regular).
        """
        self.mostrar_titulo('🏠 Menú Principal', f'Sesión activa: {usuario.nombre} ({usuario.rol})')
        
        # Crear tabla del menú
        tabla = Table(title="Opciones Disponibles", box = box.ROUNDED)
        
        tabla.add_column("Opción",      style = "cyan", width = 8, justify="center")
        tabla.add_column("Descripción", style = "white", width = 35)
        tabla.add_column("Estado",      style = "green", width = 15, justify="center")
        
        # Opciones básicas para todos los usuarios
        tabla.add_row("1", "🔑 Cambiar Contraseña", "Disponible")
        tabla.add_row("2", "📋 Ver tus Tareas", "Disponible")
        tabla.add_row("3", "🚪 Desloguearse", "Disponible")
        tabla.add_row("4", "❌ Salir", "Disponible")
        
        # Opciones de administrador
        if usuario.es_admin():
            tabla.add_row("---", "[bold yellow]ADMINISTRADOR[/bold yellow]", "[dim]---[/dim]")
            tabla.add_row("5", "👤 Crear Usuario", "[green]Admin Only[/green]")
            tabla.add_row("6", "📊 Ver Usuarios", "[green]Admin Only[/green]")
            tabla.add_row("7", "🚮 Eliminar Usuario", "[green]Admin Only[/green]")
            tabla.add_row("8", "🔄 Resetear Contraseña", "[green]Admin Only[/green]")
            tabla.add_row("9", "➕ Crear Tarea", "[green]Admin Only[/green]")
            tabla.add_row("10", "📈 Estadísticas", "[green]Admin Only[/green]")
        
        self.console.print(Align.center(tabla))
        
        # Prompt estilizado para selección
        return Prompt.ask(
            "\n[cyan]Seleccione una opción[/cyan]", 
            default      = "2",
            show_default = False
        )
    
    def manejar_menu_principal(self, usuario: Usuario) -> None:
        """Maneja el bucle del menú principal.
        
        Args:
            usuario: Usuario actual logueado.
        """
        while True:
            opcion = self.mostrar_menu_principal(usuario)
            
            if opcion == '1':
                self.cambiar_password_interfaz()
            elif opcion == '2':
                self.ver_tareas_interfaz()
            elif opcion == '3':
                self.iniciar_sesion()
                return
            elif opcion == '4':
                self.mostrar_despedida()
            
            elif usuario.es_admin():
                if opcion == '5':
                    self.crear_usuario_interfaz()
                elif opcion == '6':
                    self.mostrar_usuarios_interfaz()
                elif opcion == '7':
                    self.eliminar_usuario_interfaz()
                elif opcion == '8':
                    self.resetear_password_interfaz()
                elif opcion == '9':
                    self.crear_tarea_interfaz()
                elif opcion == '10':
                    self.mostrar_estadisticas_interfaz()
                else:
                    self.mostrar_mensaje("Opción inválida", "error")
                    self.esperar_enter()
            else:
                self.mostrar_mensaje("Opción inválida", "error")
                self.esperar_enter()
    
    def mostrar_despedida(self) -> None:
        """Muestra mensaje de despedida elegante."""
        self.limpiar_pantalla()
        
        despedida_panel = Panel(
            Align.center(
                "[bold blue]👋 ¡Hasta luego![/bold blue]\n\n"
                "[dim]Gracias por usar el Sistema de Gestión de Tareas\n"
                "Que tengas un excelente día 🌟[/dim]"
            ),
            title        = "[bold yellow]Despedida[/bold yellow]",
            border_style = "yellow"
        )
        
        self.console.print("\n" * 3)
        self.console.print(despedida_panel)
        self.console.print("\n")
        self.esperar_enter("\n[cyan]Presione [bold]Enter[/bold] para salir...[/cyan]")
        sys.exit()

    def mostrar_error_critico(self, error: str) -> None:
        """Muestra un error crítico con formato Rich.
        
        Args:
            error: Descripción del error ocurrido.
        """
        self.limpiar_pantalla()
        
        error_panel = Panel(
            f"[red]💥 Error Crítico del Sistema[/red]\n\n"
            f"[yellow]Descripción:[/yellow] {error}\n\n"
            "[dim]Por favor:\n"
            "• Tome una captura de pantalla de este error\n"
            "• Contacte al administrador del sistema\n"
            "• Proporcione los pasos que llevaron al error[/dim]",
            title        = "[bold red]⚠️  ERROR CRÍTICO[/bold red]",
            border_style = "red"
        )
        
        self.console.print("\n" * 2)
        self.console.print(error_panel)
        self.console.print("\n")
        self.console.print("[red]La aplicación se cerrará por seguridad.[/red]")

    ###########################
    # GESTIÓN DE USUARIOS (Admin)
    ###########################

    def crear_usuario_interfaz(self) -> None:
        """Interfaz mejorada para crear un nuevo usuario.
        
        Proporciona una experiencia visual mejorada para la creación
        de usuarios con validaciones en tiempo real y mensajes claros.
        """
        self.mostrar_titulo('👤 Crear Usuario', 'Registro de nuevo usuario en el sistema')
        
        # Panel informativo centrado
        info_panel = Panel(
            Align.center(
                "[blue]! Información importante:[/blue]\n\n"
                "[dim]• El usuario deberá establecer su contraseña en el primer inicio\n"
                "• Por defecto se asigna rol 'user' (no administrador)\n"
                "• El nombre debe ser único en el sistema[/dim]"
            ),
            title        = "Creación de Usuario",
            border_style = "blue"
        )
        self.console.print(Align.center(info_panel))
        
        # Solicitar nombre del usuario
        nombre = Prompt.ask(
            "\n[cyan]Ingrese el nombre del nuevo usuario[/cyan]",
            default="",
            show_default=False
        )
        
        if not nombre or not nombre.strip():
            self.mostrar_mensaje("El nombre no puede estar vacío", "error")
            self.esperar_enter()
            return
        
        # Procesar creación
        exito, mensaje = self.gestor.crear_usuario(nombre.strip())
        
        if exito:
            self.mostrar_mensaje(mensaje, "success")
            self.console.print(
                "\n[dim]💡 El usuario deberá establecer su contraseña en el primer inicio de sesión.[/dim]"
            )
        else:
            self.mostrar_mensaje(mensaje, "error")
        
        self.esperar_enter()

    def mostrar_usuarios_interfaz(self) -> None:
        """Interfaz mejorada para mostrar la lista de usuarios del sistema.
        
        Muestra una tabla elegante con información detallada de todos
        los usuarios registrados, incluyendo roles y estado de contraseñas.
        """
        self.mostrar_titulo('👥 Lista de Usuarios', 'Gestión de usuarios del sistema')
        
        usuarios = self.gestor.cargar_usuarios()
        
        if not usuarios:
            # Panel cuando no hay usuarios
            no_usuarios_panel = Panel(
                "[yellow]🚫 No hay usuarios registrados en el sistema[/yellow]\n\n"
                "[dim]Esto es inusual. Debería existir al menos un administrador.[/dim]",
                title        = "Sin Usuarios",
                border_style ="yellow"
            )
            self.console.print(no_usuarios_panel)
            self.esperar_enter()
            return
        
        # Crear tabla de usuarios
        tabla_usuarios = Table(title=f"👤 {len(usuarios)} Usuario(s) Registrado(s)", box=box.ROUNDED)
        tabla_usuarios.add_column("ID",              style = "cyan"    , width = 4)
        tabla_usuarios.add_column("Nombre",          style = "white"   , width = 20)
        tabla_usuarios.add_column("Rol",             style = "yellow"  , width = 12)
        tabla_usuarios.add_column("Estado Password", style = "green"   , width = 15)
        tabla_usuarios.add_column("Permisos",        style = "magenta" , width = 15)
        
        # Llenar tabla con datos
        for i, usuario in enumerate(usuarios, start=1):
            # Determinar estado de contraseña
            estado_pass  = "🔐 Configurada" if usuario.tiene_password() else "⚠️  Pendiente"
            estado_style = "green" if usuario.tiene_password() else "yellow"
            
            # Determinar rol y permisos
            if usuario.es_admin():
                rol_display      = "[red]🔑 Admin[/red]"
                permisos_display = "[red]Completos[/red]"
            else:
                rol_display      = "[blue]👤 User[/blue]"
                permisos_display = "[blue]Limitados[/blue]"
            
            tabla_usuarios.add_row(
                str(i),
                usuario.nombre,
                rol_display,
                f"[{estado_style}]{estado_pass}[/{estado_style}]",
                permisos_display
            )
        
        self.console.print(tabla_usuarios)
        
        # Mostrar estadísticas
        total_admins = sum(1 for u in usuarios if u.es_admin())
        total_users  = len(usuarios) - total_admins
        sin_password = sum(1 for u in usuarios if not u.tiene_password())
        
        stats_panel = Panel(
            f"[blue]📊 Estadísticas:[/blue]\n"
            f"[dim]• Administradores: [yellow]{total_admins}[/yellow]\n"
            f"• Usuarios regulares: [cyan]{total_users}[/cyan]\n"
            f"• Sin contraseña: [red]{sin_password}[/red][/dim]",
            border_style="dim white"
        )
        self.console.print(stats_panel)
        
        self.esperar_enter()
    
    def eliminar_usuario_interfaz(self) -> None:
        """Interfaz mejorada para eliminar un usuario del sistema.
        
        Proporciona una experiencia segura para la eliminación de usuarios
        con confirmaciones visuales y validaciones apropiadas.
        """
        self.mostrar_titulo('🗑️ Eliminar Usuario', 'Eliminación segura de usuarios del sistema')
        
        # Mostrar lista de usuarios primero
        usuarios = self.gestor.cargar_usuarios()
        if len(usuarios) <= 1:
            self.mostrar_mensaje(
                "No se pueden eliminar usuarios: debe existir al menos un administrador", 
                "error"
            )
            self.esperar_enter()
            return
            
        self.mostrar_usuarios_interfaz()
        
        # Panel de advertencia centrado
        advertencia_panel = Panel(
            Align.center(
                "[red]⚠️  ADVERTENCIA: Esta acción es irreversible[/red]\n\n"
                "[yellow]Consideraciones importantes:[/yellow]\n"
                "[dim]• No se pueden eliminar administradores\n"
                "• Se perderán todas las asignaciones de tareas\n"
                "• La acción no se puede deshacer[/dim]"
            ),
            title="[bold red]Zona de Peligro[/bold red]",
            border_style="red"
        )
        self.console.print(Align.center(advertencia_panel))
        
        nombre = Prompt.ask(
            "\n[red]Nombre del usuario a eliminar[/red]",
            default="",
            show_default=False
        )
        
        if not nombre:
            self.mostrar_mensaje("Operación cancelada por el usuario", "warning")
            self.esperar_enter()
            return
        
        # Confirmación con Rich
        confirmacion = Confirm.ask(
            f"\n[red]¿CONFIRMA que desea eliminar al usuario '[bold]{nombre}[/bold]'?"
        )
        
        if confirmacion:
            exito, mensaje = self.gestor.eliminar_usuario(nombre)
            if exito:
                self.mostrar_mensaje(mensaje, "success")
            else:
                self.mostrar_mensaje(mensaje, "error")
        else:
            self.mostrar_mensaje("Operación cancelada por el usuario", "info")
        
        self.esperar_enter()

    def resetear_password_interfaz(self) -> None:
        """Interfaz mejorada para resetear contraseña de usuario.
        
        Permite a los administradores resetear contraseñas de usuarios,
        forzándolos a configurar una nueva en el próximo inicio de sesión.
        """
        self.mostrar_titulo('🔄 Resetear Contraseña', 'Restablecimiento de credenciales de usuario')
        
        # Mostrar información de la operación
        info_panel = Panel(
            "[blue]ℹ️  Información del reseteo:[/blue]\n\n"
            "[dim]• Solo administradores pueden resetear contraseñas\n"
            "• La contraseña actual se eliminará completamente\n"
            "• El usuario deberá configurar una nueva en el próximo login\n"
            "• No se puede resetear contraseñas de administradores[/dim]",
            title="Reseteo de Contraseñas",
            border_style="blue"
        )
        self.console.print(info_panel)
        
        # Mostrar usuarios disponibles
        usuarios = self.gestor.cargar_usuarios()
        usuarios_no_admin = [u for u in usuarios if not u.es_admin()]
        
        if not usuarios_no_admin:
            self.mostrar_mensaje(
                "No hay usuarios regulares para resetear contraseñas", 
                "warning"
            )
            self.esperar_enter()
            return
            
        # Crear tabla de usuarios elegibles
        tabla_usuarios = Table(title = "👤 Usuarios Elegibles para Reseteo", box = box.ROUNDED)
        tabla_usuarios.add_column("Nombre",            style = "white"  , width = 20)
        tabla_usuarios.add_column("Estado Contraseña", style = "yellow" , width = 20)
        
        for usuario in usuarios_no_admin:
            estado = "🔐 Configurada" if usuario.tiene_password() else "⚠️ Pendiente"
            tabla_usuarios.add_row(usuario.nombre, estado)
            
        self.console.print(tabla_usuarios)
        
        nombre = Prompt.ask(
            "\n[cyan]Nombre del usuario para resetear[/cyan]",
            default="",
            show_default=False
        )
        
        if not nombre:
            self.mostrar_mensaje("Operación cancelada", "warning")
            self.esperar_enter()
            return
        
        # Confirmación
        confirmacion = Confirm.ask(
            f"\n[yellow]¿Resetear la contraseña del usuario '[bold]{nombre}[/bold]'?"
        )
        
        if confirmacion:
            exito, mensaje = self.gestor.resetear_password_usuario(
                self.usuario_actual.nombre, nombre
            )
            
            if exito:
                self.mostrar_mensaje(mensaje, "success")
                self.console.print(
                    "\n[dim]💡 El usuario deberá configurar una nueva contraseña en su próximo inicio de sesión.[/dim]"
                )
            else:
                self.mostrar_mensaje(mensaje, "error")
        else:
            self.mostrar_mensaje("Operación cancelada", "info")
        
        self.esperar_enter()
    
    ###########################
    # GESTIÓN DE TAREAS
    ###########################

    def mostrar_menu_acciones_tareas(self, tareas: List[Tarea]) -> None:
        """Muestra menú de acciones para tareas con Rich.
        
        Args:
            tareas: Lista de tareas disponibles para acciones.
        """
        # Panel de acciones
        acciones_panel = Panel(
            "[cyan]1.[/cyan] 📄 Ver detalles de tarea\n"
            "[cyan]2.[/cyan] 💬 Agregar comentario\n" +
            ("[cyan]3.[/cyan] ✅ Finalizar/Activar tarea\n"
             "[cyan]4.[/cyan] 👤 Asignar usuario\n"
             "[cyan]5.[/cyan] 🚮 Eliminar tarea (solo finalizadas)\n" if self.usuario_actual.es_admin() else "") +
            "[cyan]0.[/cyan] 🔙 Volver al menú principal",
            title        ="Acciones Disponibles",
            border_style ="cyan"
        )
        self.console.print(acciones_panel)
        
        opcion = Prompt.ask(
            "\n[cyan]Seleccione una acción[/cyan]", 
            choices=["0", "1", "2"] + (["3", "4", "5"] if self.usuario_actual.es_admin() else []),
            default="0"
        )
        
        # Procesar opciones
        if opcion == '1':
            self.ver_detalle_tarea(tareas)
        elif opcion == '2':
            self.agregar_comentario_interfaz(tareas)
        elif opcion == '3' and self.usuario_actual.es_admin():
            self.cambiar_estado_tarea(tareas)
        elif opcion == '4' and self.usuario_actual.es_admin():
            self.asignar_usuario_interfaz(tareas)
        elif opcion == '5' and self.usuario_actual.es_admin():
            self.eliminar_tarea_interfaz(tareas)
        # Opción 0 no necesita acción, regresa automáticamente
    
    def ver_tareas_interfaz(self) -> None:
        """Interfaz mejorada para visualizar tareas del usuario.
        
        Muestra las tareas en una tabla Rich elegante con iconos,
        colores semánticos y opciones de interacción mejoradas.
        Proporciona diferentes vistas según el rol del usuario.
        """
        self.mostrar_titulo('📋 Gestión de Tareas', 'Vista y administración de tareas asignadas')
        
        # Obtener tareas según el rol
        if self.usuario_actual.es_admin():
            tareas     = self.gestor.cargar_tareas()
            vista_tipo = "[green]Vista Administrador - Todas las tareas[/green]"
        else:
            tareas     = self.gestor.obtener_tareas_usuario(self.usuario_actual.nombre)
            vista_tipo = f"[blue]Vista Usuario - Tareas de {self.usuario_actual.nombre}[/blue]"
        
        self.console.print(vista_tipo)
        
        if not tareas:
            # Panel informativo cuando no hay tareas
            no_tareas_panel = Panel(
                "[yellow]📭 No hay tareas disponibles[/yellow]\n\n"
                "[dim]• Si eres usuario: Contacta a un administrador para asignar tareas\n"
                "• Si eres administrador: Crea nuevas tareas desde el menú principal[/dim]",
                title        = "Sin Tareas",
                border_style = "yellow"
            )
            self.console.print(no_tareas_panel)
            self.esperar_enter()
            return
        
        # Crear tabla de tareas
        tabla_tareas = Table(title=f"📊 {len(tareas)} Tarea(s) Encontrada(s)", box=box.ROUNDED)
        tabla_tareas.add_column("ID",             style = "cyan"    , width = 3)
        tabla_tareas.add_column("Nombre",         style = "white"   , width = 28)
        tabla_tareas.add_column("Estado",         style = "green"   , width = 14)
        tabla_tareas.add_column("Usuarios",       style = "magenta" , width = 16)
        tabla_tareas.add_column("Fecha Creación", style = "blue"    , width = 22)
        
        # Llenar tabla con datos
        for i, tarea in enumerate(tareas, start=1):
            # Icono y color según estado
            if tarea.esta_finalizada():
                estado_display = "[green]✅ Finalizada[/green]"
            else:
                estado_display = "[yellow]⏳ Pendiente[/yellow]"
            
            # Usuarios asignados
            usuarios_display = ', '.join(tarea.usuarios_asignados) if tarea.usuarios_asignados else '[dim]Sin asignar[/dim]'
            
            tabla_tareas.add_row(
                str(i),
                tarea.nombre[:23] + "..." if len(tarea.nombre) > 23 else tarea.nombre,
                estado_display,
                usuarios_display,
                tarea.fecha_creacion
            )
        
        self.console.print(tabla_tareas)
        
        # Menú de acciones
        self.mostrar_menu_acciones_tareas(tareas)
    
    def ver_detalle_tarea(self, tareas: List[Tarea]) -> None:
        """Interfaz mejorada para mostrar detalles de una tarea específica.
        
        Args:
            tareas: Lista de tareas disponibles.
            
        Note:
            Muestra información completa en formato Rich con paneles
            y formateo visual mejorado.
        """
        if not tareas:
            self.mostrar_mensaje("No hay tareas disponibles", "warning")
            self.esperar_enter()
            return
            
        try:
            id_tarea = Prompt.ask(
                f"\n[cyan]Ingrese el ID de la tarea (1-{len(tareas)})[/cyan]",
                default="1"
            )
            
            id_num = int(id_tarea)
            if 1 <= id_num <= len(tareas):
                tarea = tareas[id_num - 1]
                self.mostrar_detalle_tarea_rich(tarea)
            else:
                self.mostrar_mensaje(f"ID debe estar entre 1 y {len(tareas)}", "error")
                self.esperar_enter()
        except ValueError:
            self.mostrar_mensaje("ID debe ser un número válido", "error")
            self.esperar_enter()
    
    def mostrar_detalle_tarea_rich(self, tarea: Tarea) -> None:
        """Muestra detalles de tarea con formato Rich elegante.
        
        Args:
            tarea: Tarea a mostrar en detalle.
        """
        self.mostrar_titulo(f'📄 Detalle de Tarea', f'Información completa: {tarea.nombre}')
        
        # Panel principal con información básica
        estado_emoji = "✅" if tarea.esta_finalizada() else "⏳"
        estado_color = "green" if tarea.esta_finalizada() else "yellow"
        
        info_basica = Panel(
            f"[bold]📝 Nombre:[/bold] {tarea.nombre}\n\n"
            f"[bold]📅 Creada:[/bold] {tarea.fecha_creacion}\n"
            f"[bold]🏷️ Estado:[/bold] [{estado_color}]{estado_emoji} {tarea.estado.title()}[/{estado_color}]\n\n"
            f"[bold]📄 Descripción:[/bold]\n{tarea.descripcion}",
            title="[bold blue]ℹ️ Información General[/bold blue]",
            border_style="blue"
        )
        self.console.print(info_basica)
        
        # Panel de usuarios asignados
        if tarea.usuarios_asignados:
            usuarios_texto = "\n".join([f"• {usuario}" for usuario in tarea.usuarios_asignados])
        else:
            usuarios_texto = "[dim]No hay usuarios asignados[/dim]"
            
        usuarios_panel = Panel(
            usuarios_texto,
            title        = f"[bold magenta]👥 Usuarios Asignados ({len(tarea.usuarios_asignados)})[/bold magenta]",
            border_style = "magenta"
        )
        self.console.print(usuarios_panel)
        
        # Panel de comentarios
        if tarea.comentarios:
            comentarios_texto = ""
            for i, (comentario, usuario, fecha) in enumerate(tarea.comentarios, 1):
                comentarios_texto += f"[bold cyan]{i}.[/bold cyan] [bold]{usuario}[/bold] - [dim]{fecha}[/dim]\n"
                comentarios_texto += f"   {comentario}\n\n"
        else:
            comentarios_texto = "[dim]No hay comentarios disponibles[/dim]"
            
        comentarios_panel = Panel(
            comentarios_texto.rstrip(),
            title=f"[bold green]💬 Comentarios ({len(tarea.comentarios)})[/bold green]",
            border_style="green"
        )
        self.console.print(comentarios_panel)
        
        self.esperar_enter()
    
    def agregar_comentario_interfaz(self, tareas: List[Tarea]) -> None:
        """Interfaz mejorada para agregar comentario a una tarea.
        
        Args:
            tareas: Lista de tareas disponibles.
            
        Note:
            Proporciona una experiencia visual mejorada para agregar
            comentarios con preview y validaciones.
        """
        if not tareas:
            self.mostrar_mensaje("No hay tareas disponibles", "warning")
            self.esperar_enter()
            return
            
        self.mostrar_titulo('💬 Agregar Comentario', 'Añadir observaciones a una tarea')
        
        # Mostrar tabla de tareas disponibles
        tabla_tareas = Table(title="🎯 Tareas Disponibles", box=box.ROUNDED)
        tabla_tareas.add_column("ID", style="cyan", width=4)
        tabla_tareas.add_column("Nombre", style="white", width=35)
        tabla_tareas.add_column("Estado", style="green", width=12)
        
        for i, tarea in enumerate(tareas, start=1):
            estado_display = "✅ Finalizada" if tarea.esta_finalizada() else "⏳ Pendiente"
            estado_style   = "green" if tarea.esta_finalizada() else "yellow"
            
            tabla_tareas.add_row(
                str(i),
                tarea.nombre[:28] + "..." if len(tarea.nombre) > 28 else tarea.nombre,
                f"[{estado_style}]{estado_display}[/{estado_style}]"
            )
            
        self.console.print(tabla_tareas)
        
        try:
            id_tarea = Prompt.ask(
                f"\n[cyan]ID de la tarea para comentar (1-{len(tareas)})[/cyan]",
                default="1"
            )
            
            id_num = int(id_tarea)
            if 1 <= id_num <= len(tareas):
                tarea = tareas[id_num - 1]
                
                # Mostrar información de la tarea seleccionada
                tarea_info = Panel(
                    f"[bold]📝 Tarea:[/bold] {tarea.nombre}\n"
                    f"[bold]📄 Descripción:[/bold] {tarea.descripcion[:50]}{'...' if len(tarea.descripcion) > 50 else ''}\n"
                    f"[bold]💬 Comentarios actuales:[/bold] {len(tarea.comentarios)}",
                    title        = "[bold blue]📋 Tarea Seleccionada[/bold blue]",
                    border_style = "blue"
                )
                self.console.print(tarea_info)
                
                # Solicitar comentario
                self.console.print("\n[dim]💡 Proporcione su comentario sobre esta tarea:[/dim]")
                comentario = Prompt.ask(
                    "[white]✍️ Comentario[/white]",
                    default="",
                    show_default=False
                )
                
                if comentario.strip():
                    # Preview del comentario
                    preview_panel = Panel(
                        f"[bold]👤 Autor:[/bold] {self.usuario_actual.nombre}\n"
                        f"[bold]📝 Tarea:[/bold] {tarea.nombre}\n"
                        f"[bold]💬 Comentario:[/bold]\n{comentario.strip()}",
                        title="[bold yellow]👁️ Vista Previa[/bold yellow]",
                        border_style="yellow"
                    )
                    self.console.print(preview_panel)
                    
                    if Confirm.ask("\n[green]¿Agregar este comentario?"):
                        exito, mensaje = self.gestor.agregar_comentario_tarea(
                            tarea.nombre, comentario, self.usuario_actual.nombre
                        )
                        
                        if exito:
                            self.mostrar_mensaje(mensaje, "success")
                        else:
                            self.mostrar_mensaje(mensaje, "error")
                    else:
                        self.mostrar_mensaje("Comentario cancelado", "warning")
                else:
                    self.mostrar_mensaje("El comentario no puede estar vacío", "error")
            else:
                self.mostrar_mensaje(f"ID debe estar entre 1 y {len(tareas)}", "error")
                
        except ValueError:
            self.mostrar_mensaje("ID debe ser un número válido", "error")
        
        self.esperar_enter()
    
    def crear_tarea_interfaz(self) -> None:
        """Interfaz mejorada para crear una nueva tarea.
        
        Proporciona un formulario visual atractivo para la creación
        de tareas con validaciones en tiempo real y preview.
        """
        self.mostrar_titulo('➕ Crear Nueva Tarea', 'Creación de tareas en el sistema')
        
        # Panel informativo centrado
        info_panel = Panel(
            Align.center(
                "[green]📝 Creación de Nueva Tarea[/green]\n\n"
                "[dim]• Proporcione un nombre descriptivo y único\n"
                "• La descripción debe ser clara y detallada\n"
                "• La tarea se creará en estado 'pendiente'\n"
                "• Podrá asignar usuarios después de la creación[/dim]"
            ),
            title="Información",
            border_style="green"
        )
        self.console.print(Align.center(info_panel))
        
        # Formulario de creación
        self.console.print("\n[cyan]📋 Formulario de Creación[/cyan]")
        
        # Solicitar nombre de la tarea
        nombre = Prompt.ask(
            "[white]📌 Nombre de la tarea[/white]",
            default="",
            show_default = False
        )
        
        if not nombre or not nombre.strip():
            self.mostrar_mensaje("El nombre de la tarea no puede estar vacío", "error")
            self.esperar_enter()
            return
        
        # Solicitar descripción
        self.console.print("\n[dim]💬 Proporcione una descripción detallada de la tarea:[/dim]")
        descripcion = Prompt.ask(
            "[white]📄 Descripción[/white]",
            default="",
            show_default=False
        )
        
        if not descripcion or not descripcion.strip():
            self.mostrar_mensaje("La descripción no puede estar vacía", "error")
            self.esperar_enter()
            return
        
        # Preview de la tarea antes de crear (centrado)
        preview_panel = Panel(
            Align.center(
                f"[bold]📌 Nombre:[/bold] {nombre.strip()}\n\n"
                f"[bold]📄 Descripción:[/bold]\n{descripcion.strip()}\n\n"
                f"[bold]📅 Estado inicial:[/bold] [yellow]Pendiente[/yellow]\n"
                f"[bold]👥 Usuarios asignados:[/bold] [dim]Ninguno (se puede asignar después)[/dim]"
            ),
            title="[bold blue]👀 Vista Previa de la Tarea[/bold blue]",
            border_style="blue"
        )
        self.console.print(Align.center(preview_panel))
        
        # Confirmación final
        if Confirm.ask("\n[green]¿Crear la tarea con esta información?"):
            exito, mensaje = self.gestor.crear_tarea(nombre.strip(), descripcion.strip())
            
            if exito:
                self.mostrar_mensaje(mensaje, "success")
                self.console.print(
                    "\n[dim]💡 Puede asignar usuarios a esta tarea desde el menú 'Ver tareas'.[/dim]"
                )
            else:
                self.mostrar_mensaje(mensaje, "error")
        else:
            self.mostrar_mensaje("Creación de tarea cancelada", "warning")
        
        self.esperar_enter()
    
    def mostrar_estadisticas_interfaz(self) -> None:
        """Interfaz mejorada para mostrar estadísticas del sistema.
        
        Presenta un dashboard visual completo con métricas del sistema,
        gráficos de progreso y análisis detallado del estado actual.
        """
        self.mostrar_titulo('📊 Dashboard del Sistema', 'Estadísticas y métricas generales')
        
        stats = self.gestor.obtener_estadisticas_sistema()
        
        if "error" in stats:
            error_panel = Panel(
                f"[red]❌ Error al obtener estadísticas[/red]\n\n"
                f"[yellow]Detalles:[/yellow] {stats['error']}\n\n"
                "[dim]Posibles causas:\n"
                "• Archivos de datos corruptos\n"
                "• Problemas de permisos\n"
                "• Error en el sistema de archivos[/dim]",
                title        = "[bold red]Error del Sistema[/bold red]",
                border_style = "red"
            )
            self.console.print(error_panel)
            self.esperar_enter()
            return
        
        # Estadísticas de usuarios
        tabla_usuarios = Table(title="Estadísticas de Usuarios", box=box.ROUNDED)
        tabla_usuarios.add_column("Métrica",    style = "cyan"  , width = 25)
        tabla_usuarios.add_column("Cantidad",   style = "white" , width = 10)
        tabla_usuarios.add_column("Porcentaje", style = "green" , width = 12)
        tabla_usuarios.add_column("Estado",     style = "yellow", width = 15)
        
        total_usuarios = stats['usuarios']['total']
        if total_usuarios > 0:
            admin_pct = (stats['usuarios']['admins'] / total_usuarios) * 100
            user_pct = (stats['usuarios']['users'] / total_usuarios) * 100
            sin_pass_pct = (stats['usuarios']['sin_password'] / total_usuarios) * 100
        else:
            admin_pct = user_pct = sin_pass_pct = 0
        
        tabla_usuarios.add_row(
            "Admin", 
            str(stats['usuarios']['admins']), 
            f"{admin_pct:.1f}%",
            "[green]Activos[/green]" if stats['usuarios']['admins'] > 0 else "[red]Sin admins[/red]"
        )
        tabla_usuarios.add_row(
            "Usuarios regulares", 
            str(stats['usuarios']['users']), 
            f"{user_pct:.1f}%",
            "[blue]Operativos[/blue]"
        )
        tabla_usuarios.add_row(
            "Sin contraseña", 
            str(stats['usuarios']['sin_password']), 
            f"{sin_pass_pct:.1f}%",
            "[red]Pendientes[/red]" if stats['usuarios']['sin_password'] > 0 else "[green]Completo[/green]"
        )
        tabla_usuarios.add_row(
            "TOTAL", 
            str(total_usuarios), 
            "100.0%",
            "[bold blue]Sistema[/bold blue]"
        )
        
        self.console.print(Align.center(tabla_usuarios))
        
        # Estadísticas de tareas
        tabla_tareas = Table(title="Estadísticas de Tareas", box=box.ROUNDED)
        tabla_tareas.add_column("Métrica",    style = "cyan"  , width = 25)
        tabla_tareas.add_column("Cantidad",   style = "white" , width = 10)
        tabla_tareas.add_column("Porcentaje", style = "green" , width = 12)
        tabla_tareas.add_column("Estado",     style = "yellow", width = 15)
        
        total_tareas = stats['tareas']['total']
        if total_tareas > 0:
            pendientes_pct = (stats['tareas']['pendientes'] / total_tareas) * 100
            finalizadas_pct = (stats['tareas']['finalizadas'] / total_tareas) * 100
        else:
            pendientes_pct = finalizadas_pct = 0
        
        tabla_tareas.add_row(
            "Pendientes", 
            str(stats['tareas']['pendientes']), 
            f"{pendientes_pct:.1f}%",
            "[yellow]En progreso[/yellow]" if stats['tareas']['pendientes'] > 0 else "[green]Completado[/green]"
        )
        tabla_tareas.add_row(
            "Finalizadas", 
            str(stats['tareas']['finalizadas']), 
            f"{finalizadas_pct:.1f}%",
            "[green]Completadas[/green]"
        )
        tabla_tareas.add_row(
            "TOTAL", 
            str(total_tareas), 
            "100.0%",
            "[bold blue]Sistema[/bold blue]"
        )
        
        self.console.print(Align.center(tabla_tareas))
        
        # Panel de resumen ejecutivo
        if total_tareas > 0:
            progreso_general = (stats['tareas']['finalizadas'] / total_tareas) * 100
            if progreso_general >= 80:
                progreso_estado = "[green]Excelente[/green]"
            elif progreso_general >= 60:
                progreso_estado = "[yellow]Bueno[/yellow]"
            else:
                progreso_estado = "[red]Necesita atención[/red]"
        else:
            progreso_general = 0
            progreso_estado = "[dim]Sin datos[/dim]"
        
        resumen_panel = Panel(
            Align.center(
                f"[bold blue]📈 Resumen Ejecutivo[/bold blue]\n\n"
                f"[white]• Progreso general de tareas: [bold]{progreso_general:.1f}%[/bold] {progreso_estado}\n"
                f"• Total de usuarios registrados: [bold]{total_usuarios}[/bold]\n"
                f"• Usuarios sin configurar: [bold]{stats['usuarios']['sin_password']}[/bold]\n"
                f"• Cobertura administrativa: [bold]{admin_pct:.1f}%[/bold][/white]\n\n"
                f"[dim]💡 Recomendación: "
                + ("Excelente gestión del sistema" if progreso_general >= 80 and stats['usuarios']['sin_password'] == 0
                   else "Revisar tareas pendientes y usuarios sin configurar") + "[/dim]"
            ),
            title="[bold green]📋 Estado General[/bold green]",
            border_style="green"
        )
        
        self.console.print(Align.center(resumen_panel))
        self.esperar_enter()
    
    def cambiar_estado_tarea(self, tareas: List[Tarea]) -> None:
        """Interfaz mejorada para cambiar el estado de una tarea.
        
        Args:
            tareas: Lista de tareas disponibles.
            
        Note:
            Permite alternar entre estados pendiente/finalizada con
            confirmaciones visuales y feedback claro.
        """
        if not tareas:
            self.mostrar_mensaje("No hay tareas disponibles", "warning")
            self.esperar_enter()
            return
            
        self.mostrar_titulo('⚡ Cambiar Estado de Tarea', 'Gestión de estados: Pendiente ↔ Finalizada')
        
        # Mostrar tareas con estados actuales
        tabla_estados = Table(title="📊 Estados Actuales de Tareas", box=box.ROUNDED)
        tabla_estados.add_column("ID",                style = "cyan"  , width = 4)
        tabla_estados.add_column("Nombre",            style = "white" , width = 30)
        tabla_estados.add_column("Estado Actual",     style = "yellow", width = 15)
        tabla_estados.add_column("Acción Disponible", style = "green" , width = 20)
        
        for i, tarea in enumerate(tareas, start=1):
            if tarea.esta_finalizada():
                estado_actual = "[green]✅ Finalizada[/green]"
                accion_disponible = "[blue]🔄 Reactivar[/blue]"
            else:
                estado_actual = "[yellow]⏳ Pendiente[/yellow]"
                accion_disponible = "[green]✅ Finalizar[/green]"
                
            tabla_estados.add_row(
                str(i),
                tarea.nombre[:28] + "..." if len(tarea.nombre) > 28 else tarea.nombre,
                estado_actual,
                accion_disponible
            )
            
        self.console.print(tabla_estados)
        
        try:
            id_tarea = Prompt.ask(
                f"\n[cyan]ID de la tarea a modificar (1-{len(tareas)})[/cyan]",
                default="1"
            )
            
            id_num = int(id_tarea)
            if 1 <= id_num <= len(tareas):
                tarea = tareas[id_num - 1]
                
                # Mostrar información de la tarea y acción a realizar
                if tarea.esta_finalizada():
                    accion_texto = "[blue]🔄 REACTIVAR[/blue]"
                    accion_desc  = "La tarea volverá al estado 'Pendiente'"
                    accion_color = "blue"
                else:
                    accion_texto = "[green]✅ FINALIZAR[/green]"
                    accion_desc  = "La tarea se marcará como 'Finalizada'"
                    accion_color = "green"
                
                confirmacion_panel = Panel(
                    f"[bold]📝 Tarea:[/bold] {tarea.nombre}\n\n"
                    f"[bold]📊 Estado actual:[/bold] {'✅ Finalizada' if tarea.esta_finalizada() else '⏳ Pendiente'}\n"
                    f"[bold]🎯 Acción:[/bold] {accion_texto}\n\n"
                    f"[dim]💡 {accion_desc}[/dim]",
                    title="[bold yellow]🔄 Confirmación de Cambio[/bold yellow]",
                    border_style="yellow"
                )
                self.console.print(confirmacion_panel)
                
                if Confirm.ask(f"\n[{accion_color}]¿Proceder con la acción?"):
                    if tarea.esta_finalizada():
                        # Reactivar tarea
                        tarea.activar_tarea()
                        self.gestor.guardar_tareas(tareas)
                        self.mostrar_mensaje(f"Tarea '{tarea.nombre}' reactivada exitosamente", "success")
                    else:
                        # Finalizar tarea
                        exito, mensaje = self.gestor.finalizar_tarea(tarea.nombre)
                        if exito:
                            self.mostrar_mensaje(mensaje, "success")
                        else:
                            self.mostrar_mensaje(mensaje, "error")
                else:
                    self.mostrar_mensaje("Operación cancelada", "warning")
            else:
                self.mostrar_mensaje(f"ID debe estar entre 1 y {len(tareas)}", "error")
                
        except ValueError:
            self.mostrar_mensaje("ID debe ser un número válido", "error")
        
        self.esperar_enter()
    
    def asignar_usuario_interfaz(self, tareas: List[Tarea]) -> None:
        """Interfaz mejorada para asignar usuario a una tarea.
        
        Args:
            tareas: Lista de tareas disponibles.
            
        Note:
            Proporciona una vista completa de tareas y usuarios con
            estados de asignación claramente visualizados.
        """
        if not tareas:
            self.mostrar_mensaje("No hay tareas disponibles", "warning")
            self.esperar_enter()
            return
            
        self.mostrar_titulo('👥 Asignar Usuario', 'Gestión de asignaciones de tareas')
        
        # Mostrar tareas disponibles
        tabla_tareas = Table(title="📋 Tareas Disponibles", box=box.ROUNDED)
        tabla_tareas.add_column("ID",                 style = "cyan"   , width = 4)
        tabla_tareas.add_column("Nombre",             style = "white"  , width = 30)
        tabla_tareas.add_column("Estado",             style = "green"  , width = 12)
        tabla_tareas.add_column("Usuarios Asignados", style = "magenta", width = 20)
        
        for i, tarea in enumerate(tareas, start=1):
            estado_display = "✅ Finalizada" if tarea.esta_finalizada() else "⏳ Pendiente"
            estado_style = "green" if tarea.esta_finalizada() else "yellow"
            usuarios_display = ', '.join(tarea.usuarios_asignados) if tarea.usuarios_asignados else '[dim]Sin asignar[/dim]'
            
            tabla_tareas.add_row(
                str(i),
                tarea.nombre[:23] + "..." if len(tarea.nombre) > 23 else tarea.nombre,
                f"[{estado_style}]{estado_display}[/{estado_style}]",
                usuarios_display
            )
            
        self.console.print(tabla_tareas)
        
        try:
            id_tarea = Prompt.ask(
                f"\n[cyan]ID de la tarea (1-{len(tareas)})[/cyan]",
                default="1"
            )
            
            id_num = int(id_tarea)
            if 1 <= id_num <= len(tareas):
                tarea = tareas[id_num - 1]
                
                # Mostrar información de la tarea seleccionada
                tarea_info = Panel(
                    f"[bold]📝 Tarea:[/bold] {tarea.nombre}\n"
                    f"[bold]📊 Estado:[/bold] {tarea.estado}\n"
                    f"[bold]👥 Asignados actuales:[/bold] {len(tarea.usuarios_asignados)} usuario(s)",
                    title="[bold blue]🎯 Tarea Seleccionada[/bold blue]",
                    border_style="blue"
                )
                self.console.print(tarea_info)
                
                # Mostrar usuarios disponibles
                usuarios = self.gestor.cargar_usuarios()
                tabla_usuarios = Table(title="👤 Usuarios del Sistema", box=box.ROUNDED)
                tabla_usuarios.add_column("Nombre",          style = "white" , width = 20)
                tabla_usuarios.add_column("Rol",             style = "yellow", width = 10)
                tabla_usuarios.add_column("Estado en Tarea", style = "green" , width = 15)
                
                for usuario in usuarios:
                    if usuario.nombre in tarea.usuarios_asignados:
                        estado_asignacion = "[green]✅ Asignado[/green]"
                    else:
                        estado_asignacion = "[dim]➕ Disponible[/dim]"
                        
                    rol_display = "🔑 Admin" if usuario.es_admin() else "👤 User"
                    
                    tabla_usuarios.add_row(
                        usuario.nombre,
                        rol_display,
                        estado_asignacion
                    )
                    
                self.console.print(tabla_usuarios)
                
                nombre_usuario = Prompt.ask(
                    "\n[cyan]Nombre del usuario a asignar/desasignar[/cyan]",
                    default="",
                    show_default=False
                )
                
                if nombre_usuario:
                    # Verificar si el usuario ya está asignado
                    if nombre_usuario in tarea.usuarios_asignados:
                        if Confirm.ask(f"\n[yellow]El usuario '{nombre_usuario}' ya está asignado. ¿Desasignarlo?"):
                            if tarea.quitar_usuario(nombre_usuario):
                                self.gestor.guardar_tareas(tareas)
                                self.mostrar_mensaje(f"Usuario '{nombre_usuario}' desasignado exitosamente", "success")
                            else:
                                self.mostrar_mensaje("Error al desasignar usuario", "error")
                        else:
                            self.mostrar_mensaje("Operación cancelada", "warning")
                    else:
                        # Asignar usuario
                        exito, mensaje = self.gestor.asignar_usuario_tarea(tarea.nombre, nombre_usuario)
                        if exito:
                            self.mostrar_mensaje(mensaje, "success")
                        else:
                            self.mostrar_mensaje(mensaje, "error")
                else:
                    self.mostrar_mensaje("Operación cancelada", "warning")
            else:
                self.mostrar_mensaje(f"ID debe estar entre 1 y {len(tareas)}", "error")
                
        except ValueError:
            self.mostrar_mensaje("ID debe ser un número válido", "error")
        
        self.esperar_enter()
      
    def eliminar_tarea_interfaz(self, tareas: List[Tarea]) -> None:
        """Interfaz para eliminar tareas finalizadas del sistema.
        
        Args:
            tareas: Lista de tareas disponibles.
            
        Note:
            Solo permite eliminar tareas que están en estado finalizada.
            Esta operación es irreversible.
        """
        if not tareas:
            self.mostrar_mensaje("No hay tareas disponibles", "warning")
            self.esperar_enter()
            return
            
        self.mostrar_titulo('🗑️ Eliminar Tarea', 'Eliminación permanente de tareas finalizadas')
        
        # Filtrar solo tareas finalizadas
        tareas_finalizadas = [t for t in tareas if t.esta_finalizada()]
        
        if not tareas_finalizadas:
            # Panel informativo cuando no hay tareas finalizadas
            no_finalizadas_panel = Panel(
                "[yellow]¡ No hay tareas finalizadas para eliminar ![/yellow]\n\n"
                "[dim]• Solo se pueden eliminar tareas en estado 'Finalizada'\n"
                "• Primero debe finalizar las tareas que desee eliminar[/dim]",
                title="Sin Tareas Finalizadas",
                border_style="yellow"
            )
            self.console.print(no_finalizadas_panel)
            self.esperar_enter()
            return
        
        # Mostrar tabla de tareas finalizadas
        tabla_finalizadas = Table(title=f"🗑️ {len(tareas_finalizadas)} Tarea(s) Finalizada(s) - Disponibles para Eliminar", box=box.ROUNDED)
        tabla_finalizadas.add_column("ID", style="cyan", width=3)
        tabla_finalizadas.add_column("Nombre", style="white", width=30)
        tabla_finalizadas.add_column("Usuarios", style="magenta", width=20)
        tabla_finalizadas.add_column("Fecha Finalización", style="green", width=20)
        
        for i, tarea in enumerate(tareas_finalizadas, start=1):
            usuarios_display = ', '.join(tarea.usuarios_asignados) if tarea.usuarios_asignados else '[dim]Sin asignar[/dim]'
            
            tabla_finalizadas.add_row(
                str(i),
                tarea.nombre[:28] + "..." if len(tarea.nombre) > 28 else tarea.nombre,
                usuarios_display,
                tarea.fecha_creacion  # Usamos fecha_creacion como aproximación
            )
        
        self.console.print(tabla_finalizadas)
        
        # Panel de advertencia
        advertencia_panel = Panel(
            Align.center(
                "[red]¡¡ ADVERTENCIA: Esta acción es IRREVERSIBLE !![/red]\n\n"
                "[yellow]Al eliminar una tarea:[/yellow]\n"
                "[dim]• Se perderá toda la información de la tarea\n"
                "• Se perderán todos los comentarios asociados\n"
                "• No se puede recuperar la información eliminada\n"
                "• Solo se pueden eliminar tareas finalizadas[/dim]"
            ),
            title="[bold red]Zona de Peligro[/bold red]",
            border_style="red"
        )
        self.console.print(Align.center(advertencia_panel))
        
        try:
            id_tarea = Prompt.ask(
                f"\n[red]ID de la tarea a ELIMINAR (1-{len(tareas_finalizadas)})[/red]",
                default="",
                show_default=False
            )
            
            if not id_tarea:
                self.mostrar_mensaje("Operación cancelada", "warning")
                self.esperar_enter()
                return
            
            id_num = int(id_tarea)
            if 1 <= id_num <= len(tareas_finalizadas):
                tarea_a_eliminar = tareas_finalizadas[id_num - 1]
                
                # Mostrar información de la tarea a eliminar
                confirmacion_panel = Panel(
                    f"[bold]📝 Tarea:[/bold] {tarea_a_eliminar.nombre}\n\n"
                    f"[bold]📊 Estado:[/bold] ✅ Finalizada\n"
                    f"[bold]👥 Usuarios:[/bold] {', '.join(tarea_a_eliminar.usuarios_asignados) if tarea_a_eliminar.usuarios_asignados else 'Sin asignar'}\n"
                    f"[bold]💬 Comentarios:[/bold] {len(tarea_a_eliminar.comentarios)} comentario(s)\n\n"
                    f"[bold red]🗑️ ACCIÓN:[/bold red] [red]ELIMINAR PERMANENTEMENTE[/red]",
                    title="[bold yellow]⚠️ Confirmación de Eliminación[/bold yellow]",
                    border_style="yellow"
                )
                self.console.print(confirmacion_panel)
                
                # Doble confirmación para mayor seguridad
                if Confirm.ask(f"\n[red]¿CONFIRMA que desea ELIMINAR PERMANENTEMENTE la tarea '[bold]{tarea_a_eliminar.nombre}[/bold]'?"):
                    if Confirm.ask(f"\n[red]¿ESTÁ COMPLETAMENTE SEGURO? Esta acción NO SE PUEDE DESHACER"):
                        exito, mensaje = self.gestor.eliminar_tarea(tarea_a_eliminar.nombre)
                        
                        if exito:
                            self.mostrar_mensaje(mensaje, "success")
                            self.console.print("\n[green]✅ La tarea ha sido eliminada exitosamente del sistema.[/green]")
                        else:
                            self.mostrar_mensaje(mensaje, "error")
                    else:
                        self.mostrar_mensaje("Eliminación cancelada en segunda confirmación", "info")
                else:
                    self.mostrar_mensaje("Eliminación cancelada", "info")
            else:
                self.mostrar_mensaje(f"ID debe estar entre 1 y {len(tareas_finalizadas)}", "error")
                
        except ValueError:
            self.mostrar_mensaje("ID debe ser un número válido", "error")
        except Exception as e:
            self.mostrar_mensaje(f"Error inesperado: {e}", "error")
        
        self.esperar_enter()
    
    def ejecutar(self) -> None:
        """Ejecuta la aplicación principal con interfaz Rich mejorada.
        
        Controla el flujo principal de la aplicación, manejando la
        autenticación, menú principal y gestión de errores con
        presentación visual moderna.
        """
        try:
            # Mostrar pantalla de bienvenida
            self.mostrar_pantalla_inicio()
            
            # Bucle principal de la aplicación
            while True:
                # Verificar existencia de administrador
                if not self.gestor.existe_admin():
                    self.crear_admin_inicial()
                    continue
                
                # Proceso de autenticación
                self.iniciar_sesion()
                
                # Si el login fue exitoso, mostrar menú principal
                if self.usuario_actual:
                    self.manejar_menu_principal(self.usuario_actual)
                    self.usuario_actual = None
                
        except KeyboardInterrupt:
            # Despedida elegante al interrumpir con Ctrl+C
            self.mostrar_despedida()
            sys.exit()
        except Exception as e:
            # Manejo de errores inesperados
            self.mostrar_error_critico(str(e))
            sys.exit(1)
    

def main() -> None:
    """Función principal del programa con interfaz Rich.
    
    Punto de entrada de la aplicación. Inicializa la interfaz
    de consola mejorada con Rich y ejecuta el sistema de
    gestión de tareas.
    
    Features:
        - Interfaz visual moderna con colores y estilos
        - Manejo robusto de errores
        - Experiencia de usuario mejorada
        - Compatibilidad multiplataforma
        
    Raises:
        SystemExit: Al salir de la aplicación normalmente o por error.
        
    Example:
        >>> python main.py
        # Inicia la aplicación con interfaz Rich
    """
    interfaz = InterfazConsola()
    interfaz.ejecutar()


if __name__ == "__main__":
    main()