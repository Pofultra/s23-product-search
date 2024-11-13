from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Product

@registry.register_document
class ProductDocument(Document):
    name = fields.TextField(
        analyzer='spanish',
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField()
        }
    )
    description = fields.TextField(
        analyzer='spanish'
    )
    category = fields.KeywordField()
    price = fields.FloatField()
    stock = fields.IntegerField()

    class Index:
        name = 'products'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'spanish_custom': {
                        'type': 'spanish',
                        'stopwords': '_spanish_'
                    }
                }
            }
        }

    class Django:
        model = Product
        fields = []