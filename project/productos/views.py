from elasticsearch_dsl import Q
from elasticsearch.exceptions import ConnectionError as ESConnectionError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .documents import ProductDocument


@api_view(["GET"])
def search_products(request):
    """
    View for advanced search of products with Spanish support
    """
    try:
        # Get and validate parameters
        query = request.GET.get("query", "")
        price_min = request.GET.get("price_min")
        price_max = request.GET.get("price_max")
        category = request.GET.get("category")
        only_available = request.GET.get("available", "false").lower() == "true"

        # Validate prices before continuing
        try:
            if price_min:
                price_min = float(price_min)
            if price_max:
                price_max = float(price_max)
        except ValueError:
            return Response({"error": "Invalid price values"}, status=400)

        # Build the base query
        search = ProductDocument.search()
        must_queries = []
        filter_queries = []

        # Text search
        if query:
            must_queries.append(
                Q(
                    "multi_match",
                    query=query,
                    fields=["name^2", "description"],
                    type="best_fields",
                    analyzer="spanish",
                    minimum_should_match="75%",
                )
            )

        # Price filter
        if price_min is not None or price_max is not None:
            price_range = {}
            if price_min is not None:
                price_range["gte"] = price_min
            if price_max is not None:
                price_range["lte"] = price_max
            filter_queries.append(Q("range", price=price_range))

        # Category filter
        if category:
            filter_queries.append(Q("term", category=category.lower()))

        # Stock filter
        if only_available:
            filter_queries.append(Q("range", stock={"gt": 0}))

        # Build the complete query
        if must_queries or filter_queries:
            search = search.query(
                Q(
                    "bool",
                    must=must_queries if must_queries else [Q("match_all")],
                    filter=filter_queries,
                )
            )

        # Execute search
        response = search.execute()

        # Prepare results
        results = []
        for hit in response:
            result = {
                "id": hit.meta.id,
                "name": hit.name,
                "description": hit.description,
                "category": hit.category,
                "price": float(hit.price),  # Ensure price is float
                "stock": int(hit.stock),  # Ensure stock is int
                "score": hit.meta.score,
            }
            results.append(result)

        return Response(
            {
                "total": response.hits.total.value,
                "max_score": response.hits.max_score,
                "results": results,
            }
        )

    except ESConnectionError:
        return Response(
            {"error": "Connection error with the search service"}, status=503
        )
    except Exception as e:
        return Response({"error": f"Internal server error: {str(e)}"}, status=500)
