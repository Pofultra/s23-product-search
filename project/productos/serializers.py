from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'stock']

    def get_field_names(self, declared_fields=None, for_json=False):
        return self.fields.keys()