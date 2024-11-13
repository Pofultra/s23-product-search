# Proyecto Django: Buscador Avanzado de Productos

## Objetivo
Este proyecto implementa una API REST en Django para realizar búsquedas avanzadas de productos, aprovechando Elasticsearch para la búsqueda "full-text" y la optimización de consultas, cumpliendo con los requisitos de la prueba técnica.

## Requisitos del Proyecto
- **Django**: Configuración de un proyecto básico con una app llamada `productos`.
- **Modelo de Datos**: Definición del modelo `Producto` con los campos `nombre`, `descripcion`, `categoria`, `precio`, y `stock`.
- **Elasticsearch**: Configuración de Elasticsearch para sincronizar datos y realizar búsquedas avanzadas con filtros y relevancia.
- **API REST**: Implementación de una API de búsqueda avanzada con filtros en el campo `nombre`, `descripcion`, rango de precios, y disponibilidad de stock.
- **Optimización**: Mejora de rendimiento de consultas con Elasticsearch, utilizando IA para optimizar y documentar el proceso.

## Estructura del Proyecto
```plaintext
  myproject/
  ├── productos/
  │   ├── migrations/
  │   ├── models.py             # Definición del modelo de Producto
  │   ├── views.py              # Implementación de la API de búsqueda avanzada
  │   ├── serializers.py        # Serializadores para el modelo Producto
  │   ├── urls.py               # Rutas para la API
  ├── settings.py               # Configuración de Elasticsearch
  ├── urls.py                   # Rutas generales del proyecto
  └── README.md                 # Documentación del proyecto
  ```
## Instalación y Configuración
Requisitos Previos
Python 3.x
Django
Elasticsearch
Paso a Paso
Clonar el Repositorio:

### bash

```bash
git clone <URL_del_repositorio>
cd myproject
```
Instalar las Dependencias:

### bash
```bash
pip install -r requirements.txt
```

## Configurar Elasticsearch:

Asegúrate de que Elasticsearch esté ejecutándose en el puerto especificado en settings.py.
En settings.py, configura la conexión a Elasticsearch y define el índice productos.

## Migrar la Base de Datos:
```bash
python manage.py makemigrations
python manage.py migrate
```
## Sincronizar el Índice en Elasticsearch: 

```bash
python manage.py search_index --create  # Crear el índice por primera vez.
python manage.py search_index --populate  # Población inicial de datos.
```

## Iniciar el Servidor de Desarrollo:

```bash
python manage.py runserver
```

## API de Búsqueda Avanzada

La API permite realizar búsquedas de productos utilizando los siguientes filtros:

Texto en nombre y descripcion: Búsqueda "full-text".
Rango de precios (precio_min, precio_max): Filtra por rango de precios.
Filtro por categoria: Devuelve productos de una categoría específica.
Stock disponible: Devuelve productos con stock mayor a 0.
### Ejemplo de Consulta:
```plaintext
http

GET /api/productos/?search=nombre_del_producto&categoria=electronica&precio_min=100&precio_max=500&stock=1
```
### Ejemplo de Respuesta
```plaintext
json

{
  "productos": [
    {
      "nombre": "Producto 1",
      "descripcion": "Descripción del producto 1",
      "categoria": "Electronica",
      "precio": 300.00,
      "stock": 10,
      "relevancia": 1.2
    }
  ]
}
```
## Uso de IA
Se uso la IA para medir la escala de trabajo y organizar las tareas en el proyecto. 
Ver [Plan de Tareas - Prueba Técnica](project_technical_specifications.md).
Para la optimizacion de consultas se uso Claude para mejorar las consultas de Elasticsearch basdo en el modelo de producto, los requerimientos tecnicos y la consulta base que se contruyo en la vista.
De manera genral se uso la IA para contruir logica solida en cada tarea. Las herramientas utilizadas fueron:
- **ChatGPT**: Generar documentos.
- **Claude**: Mejorar consultas.
- **Codeium**: Refactorizar código, gestionar errores.
- **Perplexity**: Búsqueda de información relacionada.

## Licencia
Este proyecto está bajo la Licencia MIT.