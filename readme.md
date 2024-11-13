# 🔍 Advanced Product Search Engine with Django & Elasticsearch

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-4.2%2B-green.svg)](https://www.djangoproject.com/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.x-yellow.svg)](https://www.elastic.co/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

## 📋 Overview
A high-performance REST API implementation leveraging Django and Elasticsearch for advanced product search capabilities. The system utilizes full-text search functionality and query optimization techniques to deliver precise and relevant results.

## 🎯 Core Features
- Full-text search with advanced filtering capabilities
- Real-time index synchronization
- RESTful API endpoints
- Bulk data import functionality
- Admin interface with enhanced product management

## 🏗️ Technical Architecture

### Data Model
```python
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
```

### Project Structure
```
myproject/
├── 📁 productos/
│   ├── documents.py          # Elasticsearch document mappings
│   ├── models.py            # Django ORM models
│   ├── serializers.py       # DRF serializers
│   ├── views.py            # API endpoints
│   └── tests/
│       └── test_search.py  # Unit/Integration tests
├── 📁 project/
│   ├── settings.py         # Project configuration
│   └── urls.py            # URL routing
└── requirements.txt        # Dependencies
```

## 🚀 Deployment Guide

### Prerequisites
- Python 3.8+
- Django 4.2+
- Elasticsearch 8.x
- Virtual environment (recommended)

### Installation Steps

1. **Clone Repository**
```bash
git clone git@github.com:username/project.git
cd project
```

2. **Environment Setup**
```bash
python -m venv venv
source venv/bin/activate  # Unix
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

3. **Elasticsearch Configuration**
```python
# settings.py
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200',        
    }
}
```

4. **Database Initialization**
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. **Index Management**
```bash
# Create and populate Elasticsearch index
python manage.py search_index --create
python manage.py search_index --populate
```

## 🔌 API Reference

### Search Endpoint
`GET /api/search/`

#### Query Parameters
| Parameter    | Type    | Description                          |
|-------------|---------|--------------------------------------|
| query       | string  | Full-text search query               |
| min_price   | decimal | Minimum price filter                 |
| max_price   | decimal | Maximum price filter                 |
| category    | string  | Category filter                      |
| in_stock    | boolean | Filter for available products        |

#### Response Schema
```json
{
  "total": integer,
  "max_score": float,
  "results": [
    {
      "id": string,
      "name": string,
      "description": string,
      "category": string,
      "price": decimal,
      "stock": integer,
      "score": float
    }
  ]
}
```

## 🔧 Advanced Configuration

### Elasticsearch Mapping
```python
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
    category = fields.KeywordField(
        normalizer='lowercase'
    )
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
                },
                'normalizer': {
                    'lowercase': {
                        'type': 'custom',
                        'filter': ['lowercase', 'asciifolding']
                    }
                }
            }
        }

    class Django:
        model = Product
        fields = []
```

## 🤖 AI Integration
The project leverages various AI tools for development optimization:
- **Query Optimization**: Elasticsearch DSL queries refined using Claude
- **Code Quality**: Refactoring and error handling improved with Codeium
- **Documentation**: Technical writing enhanced with GPT-4
- **Research**: Architecture decisions supported by Perplexity

## 📈 Performance Considerations
- Implemented query result caching
- Optimized Elasticsearch mappings for faster searches
- Bulk indexing for efficient data synchronization
- Connection pooling for improved response times

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
