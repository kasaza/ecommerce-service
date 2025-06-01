# products/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from products.models import Category, Product

User = get_user_model()


class CategoryModelTest(TestCase):
    def setUp(self):
        self.root = Category.objects.create(name='Root')
        self.child1 = Category.objects.create(name='Child1', parent=self.root)
        self.child2 = Category.objects.create(name='Child2', parent=self.root)
        self.grandchild = Category.objects.create(name='Grandchild', parent=self.child1)

    def test_category_str(self):
        self.assertEqual(str(self.root), 'Root')

    def test_get_ancestors(self):
        ancestors = self.grandchild.get_ancestors()
        self.assertEqual(len(ancestors), 2)
        self.assertEqual(ancestors[0].name, 'Child1')
        self.assertEqual(ancestors[1].name, 'Root')

    def test_get_descendants(self):
        descendants = self.root.get_descendants()
        self.assertEqual(len(descendants), 3)
        self.assertEqual(descendants[0].name, 'Child1')
        self.assertEqual(descendants[1].name, 'Grandchild')
        self.assertEqual(descendants[2].name, 'Child2')


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.99,
            stock_quantity=100
        )
        self.product.categories.add(self.category)

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Test Product')

    def test_product_category_relationship(self):
        self.assertEqual(self.product.categories.count(), 1)
        self.assertEqual(self.product.categories.first().name, 'Test Category')
