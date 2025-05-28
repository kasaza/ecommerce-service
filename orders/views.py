from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from notifications.tasks import send_order_confirmation_sms, send_order_notification_email


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).prefetch_related('items__product')

    def perform_create(self, serializer):
        order = serializer.save(customer=self.request.user)

        # Update product stock quantities
        for item in order.items.all():
            product = item.product
            product.stock_quantity -= item.quantity
            product.save()

        # Optionally calculate and set total
        order.total = sum(item.quantity * item.product.price for item in order.items.all())
        order.save()

        # Send notifications
        send_order_confirmation_sms.delay(order.id)
        send_order_notification_email.delay(order.id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

