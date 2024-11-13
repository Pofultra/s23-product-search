from django.urls import path
from .views import ReadmeView, search_products


urlpatterns = [
    path("api/search/", search_products, name="search-products"),
    path('', ReadmeView.as_view(), name='readme'),
]
