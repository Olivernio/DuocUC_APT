# Documentación: Gráficos del Dashboard

## 📊 Resumen General

El sistema de gráficos del dashboard de PetStorePOS está implementado usando **Chart.js v4.4.0**, una biblioteca JavaScript moderna y potente para visualización de datos. Los datos se obtienen desde el backend Django y se renderizan en el frontend usando Canvas HTML5.

---

## 🛠️ Tecnologías Utilizadas

### Frontend
- **Chart.js v4.4.0**: Biblioteca principal para renderizar gráficos
  - **CDN**: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js`
  - **Renderizado**: Canvas HTML5 (`<canvas>`)
  - **Formato**: UMD (Universal Module Definition) - compatible con navegadores modernos

### Backend
- **Django**: Framework web Python
- **ORM de Django**: Para consultas a la base de datos
- **Django Cache Framework**: Para optimización mediante caché
- **JSON**: Para serialización de datos entre backend y frontend

### Otros
- **Bootstrap 5.3.3**: Para el diseño responsive de las tarjetas que contienen los gráficos
- **JavaScript Vanilla**: Para la inicialización y configuración de los gráficos

---

## 📈 Tipos de Gráficos Implementados

El dashboard actualmente incluye **4 gráficos principales**:

### 1. **Gráfico de Ventas por Mes** (Línea)
- **Tipo**: `line`
- **Datos**: Últimos 6 meses de ventas
- **Características**:
  - Línea curva con tensión (0.4)
  - Área rellena con gradiente
  - Puntos destacados en la línea
  - Eje Y formateado como moneda ($)
  - Formato de números con separadores de miles

### 2. **Gráfico de Adopciones por Especie** (Pastel/Pie)
- **Tipo**: `pie`
- **Datos**: Distribución de adopciones por especie (Perro, Gato, Conejo, etc.)
- **Características**:
  - Colores diferentes por segmento
  - Leyenda en la parte inferior
  - Bordes blancos entre segmentos

### 3. **Gráfico de Productos Más Vendidos** (Barras Horizontal)
- **Tipo**: `bar` con `indexAxis: 'y'`
- **Datos**: Top 10 productos más vendidos
- **Características**:
  - Barras horizontales
  - Ordenado de mayor a menor cantidad vendida

### 4. **Gráfico de Stock por Categoría** (Barras Vertical)
- **Tipo**: `bar`
- **Datos**: Stock total agrupado por categoría de productos
- **Características**:
  - Barras verticales
  - Colores diferenciados por categoría

---

## 🔄 Flujo de Datos

### 1. Backend (Django Views)
**Archivo**: `PetStorePOS/dashboard/views.py`

La vista `index()` realiza las siguientes operaciones:

```python
# 1. Consulta la base de datos usando Django ORM
sales_by_month = []  # Ventas de los últimos 6 meses
months_labels = []   # Etiquetas de meses

# 2. Agregaciones de datos
Order.objects.filter(...).aggregate(total=Sum('total'))
Product.objects.values('category').annotate(total_stock=Sum('stock'))

# 3. Serialización a JSON
context = {
    'sales_by_month': json.dumps(sales_by_month),
    'months_labels': json.dumps([str(m) for m in months_labels]),
    # ... más datos
}
```

### 2. Template (HTML)
**Archivo**: `PetStorePOS/templates/dashboard/index.html`

```html
<!-- Canvas para cada gráfico -->
<canvas id="salesChart" style="max-height: 300px;"></canvas>
<canvas id="adoptionsChart" style="max-height: 300px;"></canvas>
<canvas id="topProductsChart" style="max-height: 400px;"></canvas>
<canvas id="stockChart" style="max-height: 400px;"></canvas>
```

### 3. Frontend (JavaScript)
**Ubicación**: Script inline en `index.html`

```javascript
// 1. Obtener datos del contexto Django (ya serializados como JSON)
const monthsLabels = {{ months_labels|safe }} || [];
const salesData = {{ sales_by_month|safe }} || [];

// 2. Obtener el elemento Canvas
const salesCtx = document.getElementById('salesChart');

// 3. Crear el gráfico con Chart.js
new Chart(salesCtx, {
    type: 'line',
    data: { ... },
    options: { ... }
});
```

---

## ⚙️ Optimización y Caché

### Sistema de Caché
El dashboard implementa un sistema de caché para mejorar el rendimiento:

**Archivo**: `PetStorePOS/core/utils.py`

```python
def get_cached_or_compute(cache_key, compute_func, timeout=300):
    """
    Obtiene un valor del caché o lo calcula si no existe.
    Timeout: 5-10 minutos dependiendo del dato.
    """
```

**Datos en caché**:
- Ventas del mes actual (5 minutos)
- Stock bajo (10 minutos)
- Adopciones (10 minutos)
- Top productos (10 minutos)

### Optimización de Queries
- **`select_related()`**: Para evitar consultas N+1
- **`aggregate()`**: Para cálculos en base de datos
- **`values().annotate()`**: Para agrupaciones eficientes

---

## 🎨 Personalización y Temas

### Modo Alto Contraste
Los gráficos detectan automáticamente el modo de accesibilidad:

```javascript
const isHighContrast = document.documentElement.classList.contains('high-contrast');

const chartColors = isHighContrast ? {
    primary: '#FFFF00',  // Amarillo
    secondary: '#FFFFFF', // Blanco
    text: '#FFFFFF',      // Texto blanco
    // ...
} : {
    primary: 'rgb(13, 110, 253)', // Azul Bootstrap
    // ...
};
```

### Configuración Común
Todos los gráficos comparten una configuración base (`commonOptions`):
- Responsive design
- Colores adaptativos
- Tipografía consistente
- Tooltips personalizados
- Escalas configuradas

---

## 📁 Estructura de Archivos

```
PetStorePOS/
├── dashboard/
│   └── views.py              # Lógica de negocio y preparación de datos
├── templates/
│   └── dashboard/
│       └── index.html        # Template con gráficos y JavaScript
├── core/
│   └── utils.py              # Funciones helper y caché
└── static/
    └── css/
        └── dashboard/        # Estilos específicos del dashboard (si existen)
```

---

## 🔧 Configuración de Chart.js

### Opciones Principales
```javascript
{
    responsive: true,              // Se adapta al tamaño del contenedor
    maintainAspectRatio: true,     // Mantiene proporción
    plugins: {
        legend: { ... },           // Configuración de leyenda
        tooltip: { ... }           // Tooltips personalizados
    },
    scales: {
        x: { ... },                // Eje X
        y: { ... }                 // Eje Y
    }
}
```

---

## 📊 Datos Procesados

### Ventas por Mes
- **Origen**: `Order` model
- **Filtro**: Estado `CONFIRMED`, `PROCESSING`, `SHIPPED`, `DELIVERED`
- **Período**: Últimos 6 meses
- **Cálculo**: `Sum('total')` por mes

### Adopciones por Especie
- **Origen**: `AdoptionRequest` model (solicitudes procesadas)
- **Agrupación**: Por `Mascota__Especie`
- **Cálculo**: `Count('id')` por especie

### Top Productos
- **Origen**: `OrderItem` model
- **Agregación**: `Sum('quantity')` por producto
- **Orden**: Descendente por cantidad
- **Límite**: Top 10

### Stock por Categoría
- **Origen**: `Product` model
- **Agrupación**: Por `category`
- **Cálculo**: `Sum('stock')` por categoría

---

## 🚀 Mejoras Futuras Sugeridas

1. **Actualización en Tiempo Real**: WebSockets para actualizar gráficos sin recargar
2. **Filtros Interactivos**: Permitir cambiar rangos de fechas desde el frontend
3. **Exportación**: Agregar botones para exportar gráficos como PNG/PDF
4. **Zoom y Pan**: Habilitar interacción avanzada con Chart.js plugins
5. **Animaciones**: Personalizar animaciones de carga
6. **Más Tipos de Gráficos**: Doughnut, Radar, Area charts, etc.

---

## 📚 Referencias

- **Chart.js Documentación**: https://www.chartjs.org/docs/latest/
- **Chart.js CDN**: https://cdn.jsdelivr.net/npm/chart.js/
- **Django Cache Framework**: https://docs.djangoproject.com/en/stable/topics/cache/

---

## 💡 Notas Técnicas

- **Versión de Chart.js**: 4.4.0 (última estable al momento de implementación)
- **Compatibilidad**: Navegadores modernos con soporte para Canvas HTML5
- **Rendimiento**: Los gráficos se renderizan después de `DOMContentLoaded`
- **Accesibilidad**: Los colores se ajustan automáticamente en modo alto contraste
- **Responsive**: Los gráficos se adaptan al tamaño del contenedor usando Bootstrap grid

---

**Última actualización**: 2024
**Mantenido por**: Equipo de desarrollo PetStorePOS

