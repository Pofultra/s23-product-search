from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, search_products

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search/', search_products, name='search-products'),
]