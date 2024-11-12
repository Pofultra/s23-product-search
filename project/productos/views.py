from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from elasticsearch_dsl import Q
from .models import Product
from .documents import ProductDocument
from .serializers import ProductSerializer


class ProductViewSet(ModelViewSet):
    """
    ViewSet para CRUD de productos
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


@api_view(["GET"])
def search_products(request):
    """
    Vista para búsqueda avanzada de productos
    """
    # Obtener parámetros de búsqueda
    query = request.GET.get("query", "")
    precio_min = request.GET.get("precio_min")
    precio_max = request.GET.get("precio_max")
    categoria = request.GET.get("categoria")
    solo_disponibles = request.GET.get("disponibles", "false").lower() == "true"

    # Construir la consulta base
    search = ProductDocument.search()

    # Búsqueda por texto en nombre y descripción
    if query:
        q = Q("multi_match", query=query, fields=["name", "description"])
        search = search.query(q)

    # Filtro de rango de precios
    price_range = {}
    if precio_min:
        price_range["gte"] = float(precio_min)
    if precio_max:
        price_range["lte"] = float(precio_max)
    if price_range:
        search = search.filter("range", price=price_range)

    # Filtro por categoría
    if categoria:
        search = search.filter("term", category=categoria)

    # Filtro de stock disponible
    if solo_disponibles:
        search = search.filter("range", stock={"gt": 0})

    # Ejecutar búsqueda
    response = search.execute()

    # Preparar resultados
    results = []
    for hit in response:
        result = {
            "name": hit.name,
            "description": hit.description,
            "category": hit.category,
            "price": hit.price,
            "stock": hit.stock,
            "score": hit.meta.score,
        }
        results.append(result)

    return Response({"total": response.hits.total.value, "results": results})
