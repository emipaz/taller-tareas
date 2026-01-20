# Guía de Jinja2: HTML, JavaScript, CSS y Filtros

## Índice
1. [Introducción](#introducción)
2. [Jinja en HTML](#jinja-en-html)
3. [Jinja en JavaScript](#jinja-en-javascript)
4. [Jinja en CSS](#jinja-en-css)
5. [Filtros de Jinja](#filtros-de-jinja)
6. [Filtros Encadenados](#filtros-encadenados)
7. [Mejores Prácticas](#mejores-prácticas)

---

## Introducción

**Jinja2** es un motor de plantillas server-side (lado del servidor) para Python.

### Flujo de Procesamiento:
```
1. Python/FastAPI → 2. Jinja2 procesa → 3. HTML/CSS/JS puro → 4. Navegador
```

**Importante**: El navegador nunca ve el código Jinja. Todo se procesa en el servidor antes de enviar la respuesta.

### Sintaxis Básica:
```jinja
{{ variable }}              {# Imprime una variable #}
{% if condicion %}          {# Lógica de control #}
{% for item in lista %}     {# Bucles #}
{# comentario #}            {# Comentarios (no se envían al navegador) #}
```

---

## Jinja en HTML

### 1. Variables Simples
```html
<!-- Plantilla Jinja -->
<h1>Bienvenido, {{ usuario.nombre }}</h1>
<p>Email: {{ usuario.email }}</p>
<p>Edad: {{ usuario.edad }}</p>

<!-- Resultado enviado al navegador -->
<h1>Bienvenido, Juan Pérez</h1>
<p>Email: juan@example.com</p>
<p>Edad: 30</p>
```

### 2. Condicionales
```html
<!-- Plantilla Jinja -->
{% if usuario.rol == "admin" %}
    <button>Panel de Administración</button>
{% elif usuario.rol == "moderador" %}
    <button>Panel de Moderación</button>
{% else %}
    <p>Usuario estándar</p>
{% endif %}

<!-- Resultado si usuario.rol == "admin" -->
<button>Panel de Administración</button>
```

### 3. Bucles (Loops)
```html
<!-- Plantilla Jinja -->
<ul>
{% for tarea in tareas %}
    <li>
        <strong>{{ tarea.nombre }}</strong>
        <span>{{ tarea.estado }}</span>
    </li>
{% endfor %}
</ul>

<!-- Resultado con tareas = [{"nombre": "Tarea 1", "estado": "pendiente"}, ...] -->
<ul>
    <li>
        <strong>Tarea 1</strong>
        <span>pendiente</span>
    </li>
    <li>
        <strong>Tarea 2</strong>
        <span>completada</span>
    </li>
</ul>
```

### 4. Bucles con Índice
```html
{% for item in lista %}
    <p>Índice: {{ loop.index }} - Valor: {{ item }}</p>
    <!-- loop.index: empieza en 1 -->
    <!-- loop.index0: empieza en 0 -->
    <!-- loop.first: True si es el primer elemento -->
    <!-- loop.last: True si es el último elemento -->
{% endfor %}
```

### 5. Valores por Defecto
```html
<!-- Si la variable no existe, muestra valor por defecto -->
<p>Nombre: {{ usuario.nombre | default("Sin nombre") }}</p>
```

---

## Jinja en JavaScript

Jinja procesa el contenido dentro de `<script>` **antes** de que el navegador ejecute el JavaScript.

### 1. Variables en JavaScript
```html
<script>
// Plantilla Jinja
const usuario = {
    nombre: "{{ usuario.nombre }}",
    email: "{{ usuario.email }}",
    rol: "{{ usuario.rol }}",
    edad: {{ usuario.edad }}  // Números sin comillas
};

console.log(usuario.nombre);

// Resultado enviado al navegador
const usuario = {
    nombre: "Juan Pérez",
    email: "juan@example.com",
    rol: "admin",
    edad: 30
};

console.log(usuario.nombre);
</script>
```

### 2. Condicionales en JavaScript
```html
<script>
{% if usuario.rol == "admin" %}
    function mostrarPanelAdmin() {
        console.log("Mostrando panel de administración");
        // Código solo para administradores
    }
    mostrarPanelAdmin();
{% else %}
    console.log("Usuario sin privilegios de admin");
{% endif %}

// Resultado para admin:
function mostrarPanelAdmin() {
    console.log("Mostrando panel de administración");
}
mostrarPanelAdmin();
</script>
```

### 3. Arrays/Listas en JavaScript
```html
<script>
// Plantilla Jinja
const tareas = [
    {% for tarea in tareas %}
        {
            nombre: "{{ tarea.nombre }}",
            estado: "{{ tarea.estado }}",
            prioridad: {{ tarea.prioridad }}
        }{% if not loop.last %},{% endif %}
    {% endfor %}
];

// Resultado
const tareas = [
    {
        nombre: "Tarea 1",
        estado: "pendiente",
        prioridad: 1
    },
    {
        nombre: "Tarea 2",
        estado: "completada",
        prioridad: 2
    }
];
</script>
```

### 4. Configuración Dinámica
```html
<script>
const CONFIG = {
    apiUrl: "{{ api_url }}",
    debug: {{ "true" if debug_mode else "false" }},
    version: "{{ version }}",
    features: {
        comentarios: {{ "true" if features.comentarios else "false" }},
        notificaciones: {{ "true" if features.notificaciones else "false" }}
    }
};
</script>
```

---

## Jinja en CSS

Igual que con JavaScript, Jinja procesa `<style>` en el servidor.

### 1. Variables de Color
```html
<style>
/* Plantilla Jinja */
:root {
    --primary-color: {{ tema.color_primario }};
    --secondary-color: {{ tema.color_secundario }};
    --font-size: {{ tema.tamaño_fuente }}px;
}

.boton-primario {
    background-color: {{ tema.color_primario }};
    color: {{ tema.color_texto }};
}

/* Resultado con tema = {"color_primario": "#4caf50", ...} */
:root {
    --primary-color: #4caf50;
    --secondary-color: #2196f3;
    --font-size: 16px;
}

.boton-primario {
    background-color: #4caf50;
    color: #ffffff;
}
</style>
```

### 2. Estilos Condicionales
```html
<style>
{% if usuario.tema_oscuro %}
    body {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }
{% else %}
    body {
        background-color: #ffffff;
        color: #333333;
    }
{% endif %}

.tarjeta {
    border: 1px solid {{ "#555" if usuario.tema_oscuro else "#ddd" }};
}
</style>
```

### 3. Generación de Clases Dinámicas
```html
<style>
/* Generar clases para diferentes estados */
{% for estado in estados_tarea %}
.tarea-{{ estado.nombre }} {
    background-color: {{ estado.color }};
    border-left: 4px solid {{ estado.borde }};
}
{% endfor %}

/* Resultado con estados_tarea = [
    {"nombre": "pendiente", "color": "#fff3cd", "borde": "#ffc107"},
    {"nombre": "en_progreso", "color": "#cfe2ff", "borde": "#0d6efd"}
] */

.tarea-pendiente {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
}

.tarea-en_progreso {
    background-color: #cfe2ff;
    border-left: 4px solid #0d6efd;
}
</style>
```

### 4. Media Queries Dinámicas
```html
<style>
.contenedor {
    max-width: {{ configuracion.ancho_maximo }}px;
}

@media (max-width: {{ configuracion.breakpoint_mobile }}px) {
    .contenedor {
        padding: {{ configuracion.padding_mobile }}px;
    }
}
</style>
```

---

## Filtros de Jinja

Los filtros modifican variables usando el operador `|` (pipe).

### Sintaxis:
```jinja
{{ variable | filtro }}
{{ variable | filtro(argumento) }}
{{ variable | filtro1 | filtro2 }}  {# Encadenados #}
```

### 1. Filtros de Texto

#### `upper` - Convertir a mayúsculas
```html
{{ "hola mundo" | upper }}
<!-- Resultado: HOLA MUNDO -->

<h1>{{ usuario.nombre | upper }}</h1>
<!-- Resultado: JUAN PÉREZ -->
```

#### `lower` - Convertir a minúsculas
```html
{{ "HOLA MUNDO" | lower }}
<!-- Resultado: hola mundo -->
```

#### `capitalize` - Primera letra mayúscula
```html
{{ "hola mundo" | capitalize }}
<!-- Resultado: Hola mundo -->
```

#### `title` - Cada palabra con mayúscula inicial
```html
{{ "hola mundo python" | title }}
<!-- Resultado: Hola Mundo Python -->
```

#### `trim` - Eliminar espacios al inicio y final
```html
{{ "  hola  " | trim }}
<!-- Resultado: hola -->
```

#### `replace` - Reemplazar texto
```html
{{ "Hola mundo" | replace("mundo", "amigo") }}
<!-- Resultado: Hola amigo -->
```

### 2. Filtros de Longitud/Truncado

#### `length` - Obtener longitud
```html
<p>Tienes {{ tareas | length }} tareas</p>
<!-- Si tareas = [1, 2, 3] → Resultado: Tienes 3 tareas -->
```

#### `truncate` - Truncar texto
```html
{{ descripcion | truncate(50) }}
<!-- Si descripcion tiene más de 50 caracteres, corta y añade "..." -->

{{ descripcion | truncate(50, True, "...") }}
<!-- True: corta por palabras completas -->
```

#### `wordcount` - Contar palabras
```html
{{ texto | wordcount }}
<!-- Resultado: número de palabras -->
```

### 3. Filtros de Listas

#### `first` - Primer elemento
```html
{{ tareas | first }}
<!-- Devuelve el primer elemento de la lista -->

{{ usuarios | first | upper }}
<!-- Primer usuario en mayúsculas -->
```

#### `last` - Último elemento
```html
{{ tareas | last }}
```

#### `join` - Unir elementos
```html
{{ ["Python", "JavaScript", "Java"] | join(", ") }}
<!-- Resultado: Python, JavaScript, Java -->

<p>Lenguajes: {{ lenguajes | join(" | ") }}</p>
```

#### `sort` - Ordenar
```html
{{ [3, 1, 4, 1, 5] | sort }}
<!-- Resultado: [1, 1, 3, 4, 5] -->

{{ usuarios | sort(attribute="nombre") }}
<!-- Ordena por atributo -->
```

#### `reverse` - Invertir orden
```html
{{ [1, 2, 3] | reverse }}
<!-- Resultado: [3, 2, 1] -->
```

#### `unique` - Elementos únicos
```html
{{ [1, 2, 2, 3, 3, 3] | unique }}
<!-- Resultado: [1, 2, 3] -->
```

### 4. Filtros Numéricos

#### `round` - Redondear
```html
{{ 3.14159 | round(2) }}
<!-- Resultado: 3.14 -->

{{ precio | round(2, "floor") }}  {# Redondear hacia abajo #}
{{ precio | round(2, "ceil") }}   {# Redondear hacia arriba #}
```

#### `abs` - Valor absoluto
```html
{{ -15 | abs }}
<!-- Resultado: 15 -->
```

#### `int` - Convertir a entero
```html
{{ "42" | int }}
<!-- Resultado: 42 -->

{{ 3.7 | int }}
<!-- Resultado: 3 -->
```

#### `float` - Convertir a flotante
```html
{{ "3.14" | float }}
<!-- Resultado: 3.14 -->
```

### 5. Filtros de Valores por Defecto

#### `default` - Valor si está vacío
```html
{{ usuario.nombre | default("Anónimo") }}
<!-- Si nombre está vacío o no existe → "Anónimo" -->

{{ comentario | default("Sin comentarios", true) }}
<!-- true: considera también valores falsy (0, "", False) -->
```

### 6. Filtros de Seguridad

#### `safe` - Marcar como HTML seguro
```html
{{ html_content | safe }}
<!-- No escapa el HTML, lo renderiza tal cual -->

<!-- ⚠️ PELIGRO: Solo usar con contenido confiable -->
```

#### `escape` - Escapar HTML (por defecto)
```html
{{ "<script>alert('xss')</script>" | escape }}
<!-- Resultado: &lt;script&gt;alert('xss')&lt;/script&gt; -->

<!-- Jinja escapa automáticamente, este filtro es redundante generalmente -->
```

#### `striptags` - Remover etiquetas HTML
```html
{{ "<p>Hola <strong>mundo</strong></p>" | striptags }}
<!-- Resultado: Hola mundo -->
```

### 7. Filtros de Formato

#### `format` - Formatear strings
```html
{{ "Hola %s, tienes %d mensajes" | format(nombre, cantidad) }}
<!-- Resultado: Hola Juan, tienes 5 mensajes -->
```

#### `center` - Centrar con espacios
```html
{{ "texto" | center(20) }}
<!-- Resultado: "       texto        " -->
```

### 8. Filtros de Fechas (con extensión)

```html
<!-- Requiere importar filtros personalizados -->
{{ fecha | strftime("%d/%m/%Y") }}
<!-- Formato de fecha -->
```

### 9. Filtros de Diccionarios/Objetos

#### `dictsort` - Ordenar diccionario
```html
{% for key, value in diccionario | dictsort %}
    {{ key }}: {{ value }}
{% endfor %}
```

#### `list` - Convertir a lista
```html
{{ diccionario.keys() | list }}
```

### 10. Filtros de Condiciones

#### `select` - Filtrar elementos
```html
{{ tareas | selectattr("estado", "equalto", "pendiente") | list }}
<!-- Filtra tareas con estado == "pendiente" -->
```

#### `reject` - Rechazar elementos
```html
{{ tareas | rejectattr("completada") | list }}
<!-- Tareas NO completadas -->
```

---

## Filtros Encadenados

Puedes combinar múltiples filtros:

```html
<!-- Ejemplo 1: Texto -->
{{ nombre | trim | upper | truncate(20) }}
<!-- 1. Quita espacios → 2. Mayúsculas → 3. Trunca a 20 -->

<!-- Ejemplo 2: Lista -->
{{ usuarios | map(attribute="nombre") | join(", ") | upper }}
<!-- 1. Extrae nombres → 2. Une con comas → 3. Todo en mayúsculas -->
<!-- Resultado: JUAN, MARÍA, PEDRO -->

<!-- Ejemplo 3: Con valores por defecto -->
{{ usuario.bio | default("Sin biografía") | truncate(100) | safe }}

<!-- Ejemplo 4: Números -->
{{ precio | float | round(2) }}

<!-- Ejemplo 5: Listas ordenadas -->
{{ tareas | selectattr("prioridad", "gt", 3) | sort(attribute="fecha") | first }}
<!-- 1. Filtra prioridad > 3 → 2. Ordena por fecha → 3. Toma la primera -->
```

### Ejemplo Completo Real:
```html
<div class="usuarios">
    {% for nombre in usuarios | map(attribute="nombre") | sort | unique %}
        <span class="tag">{{ nombre | title }}</span>
    {% endfor %}
</div>

<!-- Proceso:
1. map(attribute="nombre") → extrae solo nombres
2. sort → ordena alfabéticamente
3. unique → elimina duplicados
4. title → Primera letra mayúscula de cada nombre
-->
```

---

## Mejores Prácticas

### ✅ DO (Hacer)

1. **Usar filtros para transformaciones simples:**
   ```html
   {{ nombre | title }}
   ```

2. **Valores por defecto para evitar errores:**
   ```html
   {{ usuario.telefono | default("No especificado") }}
   ```

3. **Escapar contenido de usuario:**
   ```html
   {{ comentario_usuario }}  {# Ya escapa por defecto #}
   ```

4. **Comentarios para código complejo:**
   ```jinja
   {# Filtra tareas completadas en los últimos 7 días #}
   {% for tarea in tareas | selectattr("completada") %}
   ```

### ❌ DON'T (No hacer)

1. **Lógica de negocio en plantillas:**
   ```html
   <!-- ❌ MAL -->
   {% set precio_final = precio * 1.21 + descuento %}
   
   <!-- ✅ BIEN: calcular en Python -->
   {{ precio_final }}
   ```

2. **Queries a base de datos en plantillas:**
   ```html
   <!-- ❌ MAL: hacer queries en template -->
   
   <!-- ✅ BIEN: pasar datos ya consultados desde Python -->
   ```

3. **Abusar de `safe` sin validar:**
   ```html
   <!-- ❌ PELIGRO: XSS -->
   {{ user_input | safe }}
   
   <!-- ✅ BIEN: solo con contenido confiable -->
   {{ admin_html_content | safe }}
   ```

4. **Demasiados filtros encadenados (dificulta lectura):**
   ```html
   <!-- ❌ Difícil de leer -->
   {{ data | filter1 | filter2 | filter3 | filter4 | filter5 }}
   
   <!-- ✅ Procesar en Python si es muy complejo -->
   ```

---

## Ejemplo Completo: Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - {{ usuario.nombre }}</title>
    <style>
        /* CSS con Jinja */
        :root {
            --theme-color: {{ tema.color_principal | default("#4caf50") }};
        }
        
        {% if usuario.tema_oscuro %}
        body {
            background: #1a1a1a;
            color: #e0e0e0;
        }
        {% endif %}
        
        .prioridad-alta { color: #f44336; }
        .prioridad-media { color: #ff9800; }
        .prioridad-baja { color: #4caf50; }
    </style>
</head>
<body>
    <!-- HTML con Jinja -->
    <h1>Bienvenido, {{ usuario.nombre | title }}</h1>
    <p>Tienes {{ tareas | length }} tareas</p>
    
    <ul>
    {% for tarea in tareas | sort(attribute="prioridad", reverse=true) %}
        <li class="prioridad-{{ tarea.prioridad_texto | lower }}">
            <strong>{{ tarea.nombre | truncate(30) }}</strong>
            <span>{{ tarea.estado | upper }}</span>
            {% if tarea.fecha_limite %}
                <small>Vence: {{ tarea.fecha_limite }}</small>
            {% endif %}
        </li>
    {% else %}
        <li>No tienes tareas pendientes</li>
    {% endfor %}
    </ul>
    
    <script>
    // JavaScript con Jinja
    const config = {
        usuario: "{{ usuario.nombre }}",
        rol: "{{ usuario.rol }}",
        tareasCount: {{ tareas | length }},
        {% if usuario.rol == "admin" %}
        adminPanel: true,
        {% endif %}
        tareas: [
            {% for tarea in tareas %}
            {
                id: {{ tarea.id }},
                nombre: "{{ tarea.nombre | escape }}",
                prioridad: {{ tarea.prioridad }}
            }{% if not loop.last %},{% endif %}
            {% endfor %}
        ]
    };
    
    console.log(`Usuario ${config.usuario} tiene ${config.tareasCount} tareas`);
    </script>
</body>
</html>
```

---

## Recursos Adicionales

- [Documentación oficial Jinja2](https://jinja.palletsprojects.com/)
- [Lista completa de filtros](https://jinja.palletsprojects.com/en/3.1.x/templates/#builtin-filters)
- [Funciones de test](https://jinja.palletsprojects.com/en/3.1.x/templates/#builtin-tests)

---

**Recuerda**: Jinja procesa todo en el **servidor** (Python), el navegador recibe HTML/CSS/JS puro.
