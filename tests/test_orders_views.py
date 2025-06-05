# tests/test_orders_views.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from ecommerce import settings
from orders.models import Order, OrderItem
from orders.serializers import OrderItemSerializer, OrderSerializer
from products.models import Product, Category
from unittest.mock import patch, MagicMock

User = get_user_model()


class OrderViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            username='testuser'
        )
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            username='admin'
        )

        # Create test category and products
        self.category = Category.objects.create(name='Test Category')
        self.product1 = Product.objects.create(
            name='Product 1',
            price=10.00,
            stock_quantity=100
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            price=20.00,
            stock_quantity=50
        )
        self.product1.categories.add(self.category)
        self.product2.categories.add(self.category)

        self.client.force_authenticate(user=self.user)

    def test_create_order(self):
        url = reverse('order-list')
        data = {
            'items': [
                {
                    'product': self.product1.id,
                    'quantity': 2
                },
                {
                    'product': self.product2.id,
                    'quantity': 1
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 2)

        order = Order.objects.first()
        self.assertEqual(float(order.total), 40.00)  # (2*10) + (1*20)
        self.assertEqual(order.status, 'P')
        self.assertEqual(order.customer, self.user)

    def test_list_orders(self):
        # Create test orders
        order1 = Order.objects.create(customer=self.user, total=30.00)
        OrderItem.objects.create(order=order1, product=self.product1, quantity=3, price=10.00)

        order2 = Order.objects.create(customer=self.user, total=20.00)
        OrderItem.objects.create(order=order2, product=self.product2, quantity=1, price=20.00)

        url = reverse('order-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['total'], '30.00')
        self.assertEqual(response.data[1]['total'], '20.00')

    @patch('orders.views.africastalking.initialize')
    @patch('orders.views.africastalking.SMS')  # Only accessed, not called
    @patch('orders.views.send_mail')
    def test_order_notifications(self, mock_send_mail, mock_sms, mock_init):
        # Create a mock SMS instance (no need to call SMS, just set send)
        mock_sms.send.return_value = {
            'SMSMessageData': {'Message': 'Sent'}
        }

        # Configure other mocks
        mock_send_mail.return_value = 1
        mock_init.return_value = None

        # Set phone number for user
        self.user.phone_number = '+254712345678'
        self.user.save()

        url = reverse('order-list')
        data = {
            'items': [{
                'product': self.product1.id,
                'quantity': 1
            }]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify Africa's Talking was initialized
        mock_init.assert_called_once_with(
            username=settings.AFRICASTALKING_USERNAME,
            api_key=settings.AFRICASTALKING_API_KEY
        )

        # Remove this line:
        # mock_sms.assert_called_once()

        # Verify SMS was sent
        expected_message = (
            f"Hello {self.user.username}, your order #{Order.objects.last().id} for:\n"
            f"- {self.product1.name}: 1 x {self.product1.price:.2f} = KES {1 * self.product1.price:.2f}\n"
            f"Total: KES {Order.objects.last().total:.2f}"
        )
        mock_sms.send.assert_called_once_with(
            expected_message,
            [self.user.phone_number]
        )


# Verify email was sent
        mock_send_mail.assert_called_once()


    def test_order_creation_with_invalid_quantity(self):
        url = reverse('order-list')
        data = {
            'items': [
                {
                    'product': self.product1.id,
                    'quantity': 0  # Invalid quantity
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_creation_with_nonexistent_product(self):
        url = reverse('order-list')
        data = {
            'items': [
                {
                    'product': 9999,  # Non-existent product ID
                    'quantity': 1
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderModelTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            username='testuser'
        )

        self.product = Product.objects.create(
            name='Test Product',
            price=15.00,
            stock_quantity=100
        )

        self.order = Order.objects.create(
            customer=self.user,
            total=30.00
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=15.00
        )

    def test_order_str(self):
        self.assertEqual(str(self.order), f"Order #{self.order.id} - Pending")

    def test_order_total_price_property(self):
        # Test with pre-calculated total
        self.assertEqual(float(self.order.total_price), 30.00)

        # Test calculated total
        self.order.total = None
        self.assertEqual(float(self.order.total_price), 30.00)

    def test_order_item_str(self):
        order_item = OrderItem.objects.first()
        expected_str = f"2 x Test Product @ 15.00"
        self.assertEqual(str(order_item), expected_str)


class OrderSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            username='testuser'
        )

        self.product = Product.objects.create(
            name='Test Product',
            price=10.00,
            stock_quantity=50
        )

        self.order_data = {
            'items': [
                {
                    'product': self.product.id,
                    'quantity': 3
                }
            ]
        }

    def test_order_serializer_create(self):
        serializer = OrderSerializer(data=self.order_data, context={'request': MagicMock(user=self.user)})
        self.assertTrue(serializer.is_valid())

        order = serializer.save()
        self.assertEqual(order.customer, self.user)
        self.assertEqual(float(order.total), 30.00)
        self.assertEqual(order.items.count(), 1)

    def test_order_item_serializer_total(self):
        order = Order.objects.create(customer=self.user, total=30.00)
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=3,
            price=10.00
        )

        serializer = OrderItemSerializer(order_item)
        self.assertEqual(serializer.data['total'], '30.00')

    def test_order_serializer_invalid_items(self):
        invalid_data = {
            'items': [
                {
                    'product': self.product.id,
                    'quantity': 0  # Invalid quantity
                }
            ]
        }

        serializer = OrderSerializer(data=invalid_data, context={'request': MagicMock(user=self.user)})
        self.assertFalse(serializer.is_valid())
        self.assertIn('items', serializer.errors)
