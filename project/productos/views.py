# views.py
from elasticsearch_dsl import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .documents import ProductDocument

@api_view(["GET"])
def search_products(request):
    """
    Vista para búsqueda avanzada de productos con soporte para español
    """
    # Obtener parámetros de búsqueda
    query = request.GET.get("query", "")
    precio_min = request.GET.get("precio_min")
    precio_max = request.GET.get("precio_max")
    categoria = request.GET.get("categoria")
    solo_disponibles = request.GET.get("disponibles", "false").lower() == "true"

    # Construir la consulta base
    search = ProductDocument.search()

    # Búsqueda por texto en nombre y descripción con boost
    if query:
        search = search.query(
            Q("multi_match",
              query=query,
              fields=['name^2', 'description'],
              type="best_fields",
              analyzer='spanish',
              minimum_should_match="75%"
            )
        )
    else:
        search = search.query(Q("match_all"))

    # Aplicar filtros
    filters = []
    
    # Filtro de rango de precios
    if precio_min or precio_max:
        price_range = {}
        if precio_min:
            price_range["gte"] = float(precio_min)
        if precio_max:
            price_range["lte"] = float(precio_max)
        filters.append(Q("range", price=price_range))

    # Filtro por categoría
    if categoria:
        filters.append(Q("term", category=categoria))

    # Filtro de stock disponible
    if solo_disponibles:
        filters.append(Q("range", stock={"gt": 0}))

    # Aplicar todos los filtros
    if filters:
        search = search.filter('bool', must=filters)

    # Agregar resaltado de coincidencias
    search = search.highlight('name', 'description',
                            pre_tags=['<em>'],
                            post_tags=['</em>'],
                            fragment_size=150)

    # Ejecutar búsqueda
    response = search.execute()

    # Preparar resultados
    results = []
    for hit in response:
        result = {
            "id": hit.meta.id,
            "name": hit.name,
            "description": hit.description,
            "category": hit.category,
            "price": hit.price,
            "stock": hit.stock,
            "score": hit.meta.score,
            "highlights": {
                "name": hit.meta.highlight.name[0] if hasattr(hit.meta, 'highlight') and hasattr(hit.meta.highlight, 'name') else None,
                "description": hit.meta.highlight.description[0] if hasattr(hit.meta, 'highlight') and hasattr(hit.meta.highlight, 'description') else None
            }
        }
        results.append(result)

    return Response({
        "total": response.hits.total.value,
        "max_score": response.hits.max_score,
        "results": results
    })