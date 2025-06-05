# orders/serializers.py
from decimal import Decimal

from django.db import transaction
from rest_framework import serializers
from django.core.mail import send_mail
from ecommerce import settings
from orders.models import Order, OrderItem
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', 'total']
        read_only_fields = ['price']
        extra_kwargs = {'quantity': {'min_value': 1}}

    def get_total(self, obj):
        total = round(float(obj.quantity) * float(obj.price), 2)
        return f"{total:.2f}"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'created_at', 'updated_at', 'total', 'items']
        read_only_fields = ['customer', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        with transaction.atomic():
            items_data = validated_data.pop('items')
            user = self.context['request'].user
            order = Order.objects.create(customer=user)

            total = Decimal('0')

            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                price = Decimal(str(product.price))
                total += price * Decimal(str(quantity))

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )

            order.total = total
            order.save()

            # Send notification
            self.send_order_notification(order)

            return order

    def send_order_notification(self, order):
        """Send email notification about the new order"""
        subject = f'New Order #{order.id}'
        message = f'A new order has been created with total ${order.total}.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.ADMIN_EMAIL]

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=True,
        )
