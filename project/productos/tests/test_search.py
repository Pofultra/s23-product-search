from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from elasticsearch_dsl import Index
from unittest.mock import patch, Mock
from ..models import Product
from ..documents import ProductDocument
from elasticsearch.exceptions import ConnectionError


class SearchProductsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods"""
        cls.url = reverse("search-products")
        cls.test_products = [
            {
                "name": "Gaming Laptop",
                "description": "High-end gaming laptop",
                "category": "Electronics",
                "price": 1500.00,
                "stock": 10,
            },
            {
                "name": "LED Monitor",
                "description": "27-inch LED monitor",
                "category": "Electronics",
                "price": 300.00,
                "stock": 0,
            },
            {
                "name": "Mechanical Keyboard",
                "description": "Gaming keyboard with blue switches",
                "category": "Peripherals",
                "price": 100.00,
                "stock": 5,
            },
        ]

    def setUp(self):
        """Setup for each test"""
        self.client = APIClient()

        # Clear and recreate the index
        index = Index("products")
        index.delete(ignore=404)
        index.create()

        # Create and index test products
        self.products = []
        for product_data in self.test_products:
            product = Product.objects.create(**product_data)
            self.products.append(product)

        # Index products and force refresh
        ProductDocument().update(self.products)
        index.refresh()

    def tearDown(self):
        """Cleanup after each test"""
        Product.objects.all().delete()
        Index("products").delete(ignore=404)

    def test_basic_search_empty_query(self):
        """Test search with empty query returns all products"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), len(self.test_products))

    def test_basic_search_with_query(self):
        """Test basic text search with specific query"""
        response = self.client.get(self.url, {"query": "gaming"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["results"]) >= 2)

        # Verify relevant fields are present in response
        result = response.data["results"][0]
        expected_fields = {
            "id",
            "name",
            "description",
            "category",
            "price",
            "stock",
            "score",
        }
        self.assertEqual(set(result.keys()), expected_fields)

    def test_search_by_category_exact_match(self):
        """Test filtering by category with exact match"""
        # Ensure index is ready
        Index("products").refresh()

        response = self.client.get(self.url, {"category": "Peripherals"})
        self.assertEqual(response.status_code, 200)

        results = response.data["results"]
        self.assertTrue(len(results) > 0, "No results found for category 'Peripherals'")
        self.assertTrue(
            all(r["category"] == "Peripherals" for r in results),
            f"Found wrong categories: {[r['category'] for r in results]}",
        )

    def test_search_by_stock_availability(self):
        """Test filtering by stock availability"""
        response = self.client.get(self.url, {"available": "true"})
        self.assertEqual(response.status_code, 200)

        results = response.data["results"]
        self.assertTrue(len(results) > 0)
        self.assertTrue(all(r["stock"] > 0 for r in results))

    def test_price_range_search(self):
        """Test search with various price range scenarios"""
        test_cases = [
            {"price_min": "200", "price_max": "1000", "expected_count": 1},
            {"price_min": "0", "price_max": "150", "expected_count": 1},
            {"price_min": "1000", "expected_count": 1},
            {"price_max": "500", "expected_count": 2},
        ]

        for case in test_cases:
            expected_count = case.pop("expected_count")
            response = self.client.get(self.url, case)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                len(response.data["results"]),
                expected_count,
                f"Failed for price range: {case}",
            )

    def test_invalid_inputs(self):
        """Test handling of invalid input parameters"""
        test_cases = [
            {"price_min": "invalid", "expected_status": 400},
            {"price_max": "invalid", "expected_status": 400},
            {
                "price_min": "-100",
                "expected_status": 200,
            },  # Negative prices are allowed
            {
                "available": "invalid",
                "expected_status": 200,
            },  # Invalid boolean defaults to false
        ]

        for case in test_cases:
            expected_status = case.pop("expected_status")
            response = self.client.get(self.url, case)
            self.assertEqual(
                response.status_code,
                expected_status,
                f"Failed for invalid input: {case}",
            )

    def test_combined_search_filters(self):
        """Test combination of multiple search filters"""
        # Ensure index is ready
        Index("products").refresh()

        params = {
            "query": "gaming",
            "category": "Electronics",
            "price_min": "1000",
            "available": "true",
        }

        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)

        results = response.data["results"]
        self.assertTrue(len(results) > 0, f"No results found with params: {params}")

        for result in results:
            self.assertGreaterEqual(float(result["price"]), 1000)
            self.assertEqual(result["category"], "Electronics")
            self.assertGreater(result["stock"], 0)

    @patch("elasticsearch_dsl.Search.execute")
    def test_elasticsearch_connection_error(self, mock_execute):
        """Test handling of Elasticsearch connection errors"""
        mock_execute.side_effect = ConnectionError("Mocked connection error")

        with patch("elasticsearch_dsl.Search.execute", mock_execute):
            response = self.client.get(self.url, {"query": "test"})

        self.assertEqual(
            response.status_code,
            503,
            f"Expected status code 503, got {response.status_code}",
        )
        self.assertIn("error", response.data)
        self.assertIn("Connection error", response.data["error"])

    @patch("elasticsearch_dsl.Search.execute")
    def test_general_exception_handling(self, mock_execute):
        """Test handling of general exceptions"""
        mock_execute.side_effect = Exception("Unexpected error")

        response = self.client.get(self.url, {"query": "test"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.data)
        self.assertIn("Internal server error", response.data["error"])
