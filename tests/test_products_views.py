# tests/test_products_views.py
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Category, Product

User = get_user_model()


class CategoryAPITest(APITestCase):
    """API tests for Category endpoints"""
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
            username='admin'
        )
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            username='user'
        )
        self.root = Category.objects.create(name='Root')

    def test_create_category_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/categories/', {
            'name': 'New Category',
            'parent': self.root.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/categories/', {
            'name': 'New Category',
            'parent': self.root.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

    def test_list_categories(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_category_stats(self):
        """Test category stats endpoint"""
        category = Category.objects.create(name="Test Category")
        products = [
            Product.objects.create(name=f"Product {i}", price=10.00)
            for i in range(3)
        ]
        for product in products:
            product.categories.add(category)

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/categories/stats/?category_id={category.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['average_price']), 10.00)
        self.assertEqual(response.data['product_count'], 3)

    def test_category_stats_unauthorized(self):
        """Test that regular users can't access stats"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/categories/stats/?category_id=1')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)