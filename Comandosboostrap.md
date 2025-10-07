# Bootstrap 5 Diccionario de Clases y Componentes

# Para trabajar en el entorno Virtual y empesar a trabjar
- 1 - .\venv\Scripts\Activate

- 2 - cd esto es de ustedes\Documentos\GitHub\DuocUC_APT\ 
- 3 - pip install -r requirements.txt
- 4 - python manage.py migrate
- 5 - python manage.py createsuperuser
- 6 - python manage.py runserver


- Ocupar esto en emergencia en el duoc python manage.py runserver 8080

## Contenedores
- `container`: Contenedor responsivo con ancho fijo basado en puntos de ruptura.
- `container-fluid`: Contenedor que ocupa todo el ancho disponible.
- `container-{breakpoint}`: Contenedor responsivo específico (sm, md, lg, xl, xxl).

## Rejilla (Grid)
- `row`: Fila para organizar columnas.
- `col`: Columna que ocupa todo el espacio disponible.
- `col-{n}`: Columna con ancho fijo en fracciones del sistema de 12 (ej. col-6 es la mitad).
- `col-{breakpoint}-{n}`: Columna con tamaño fijo y punto de ruptura (ej. col-md-4).
- `offset-{n}`, `offset-{breakpoint}-{n}`: Desplazamiento horizontal en columnas.
- `order-{n}`, `order-{breakpoint}-{n}`: Cambia el orden visual de columnas.

## Tipografía
- `fs-{size}`: Tamaño de fuente (1 a 6).
- `fw-bold`, `fw-normal`, `fw-light`: Peso de la fuente.
- `text-{color}`: Color del texto (primary, secondary, success, danger, warning, info, light, dark).
- `text-center`, `text-start`, `text-end`: Alineación del texto.
- `text-wrap`, `text-nowrap`: Control del ajuste del texto.

## Espaciado
- `m{t|b|s|e|x|y}-{n}`: Margen (m), con dirección top, bottom, start, end, axis-x o axis-y. n=0 a 5 (ej. mt-3).
- `p{t|b|s|e|x|y}-{n}`: Relleno (padding) con las mismas direcciones y escala igual que margen.

## Botones
- `btn`: Clase base para botones.
- `btn-{color}`: Estilo de botón (primary, secondary, success, danger, warning, info, light, dark).
- `btn-lg`, `btn-sm`: Tamaños grandes o pequeños.
- `btn-outline-{color}`: Botones con borde y fondo transparentes.

## Formularios
- `form-control`: Input estilizado.
- `form-check`: Wrapper para checkboxes y radios.
- `form-check-input`: Estilo de checkbox o radio input.
- `form-check-label`: Etiqueta para checkbox o radio.
- `form-text`: Texto de ayuda.
- `form-floating`: Inputs con label flotante.

## Tarjetas (Cards)
- `card`: Contenedor de tarjeta.
- `card-body`: Cuerpo de la tarjeta.
- `card-header`: Encabezado de la tarjeta.
- `card-footer`: Pie de tarjeta.
- `card-title`: Título de tarjeta.
- `card-text`: Texto del contenido.

## Alertas
- `alert`: Contenedor de alerta.
- `alert-{color}`: Tipo de alerta (primary, secondary, success, danger, warning, info, light, dark).
- `alert-dismissible`: Alerta con botón para cerrar.

## Navegación
- `navbar`: Barra de navegación.
- `navbar-expand-{breakpoint}`: Expansión responsiva del navbar.
- `navbar-brand`: Marca o logo.
- `nav`: Contenedor para elementos de navegación.
- `nav-item`: Ítem de navegación.
- `nav-link`: Enlace dentro de navegación.

## Utilidades
- `d-{value}`: Control de display (none, block, inline, inline-block, flex).
- `flex-{value}`: Flexbox utilities (row, column, wrap, nowrap, etc).
- `justify-content-{value}`: Alineación horizontal en flex.
- `align-items-{value}`: Alineación vertical en flex.
- `text-decoration-{value}`: Decoración de texto (underline, none, etc).
- `shadow`, `shadow-sm`, `shadow-lg`: Sombras de caja.
- `rounded`, `rounded-circle`: Bordes redondeados.

## Imágenes
- `img-fluid`: Imágenes responsivas.
- `rounded`: Bordes redondeados para imágenes.

---

Este diccionario cubre las clases y comandos más usados en Bootstrap 5 para construir interfaces modernas y responsivas. ¿Quieres que te prepare un diccionario similar pero para componentes JavaScript como modales, tooltips y dropdowns?
