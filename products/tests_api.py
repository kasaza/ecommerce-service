# products/tests_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Category, Product

User = get_user_model()


class CategoryAPITest(APITestCase):
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
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
