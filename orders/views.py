# orders/api/views.py
import logging
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from orders.models import Order
from orders.serializers import OrderSerializer
from django.core.mail import send_mail
from django.conf import settings
import africastalking
# from accounts.views import Auth0TokenAuthentication

# Get logger instance
logger = logging.getLogger('orders')


class OrderViewSet(viewsets.ModelViewSet):
    # authentication_classes = [Auth0TokenAuthentication]
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        logger.debug(f"Fetching orders for customer: {self.request.user.username}")
        return Order.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        order = serializer.save()
        customer = self.request.user
        logger.info(f"Starting order processing for order #{order.id}")

        try:
            # Log order details
            logger.info(f"Order Created - ID: {order.id}")
            logger.info(f"Customer: {customer.username} (ID: {customer.id}, Email: {customer.email})")
            logger.info(f"Order Total: KES{order.total}")

            # Build items list and log each item
            items_list = []
            for item in order.items.all():
                item_info = f"{item.product.name}: {item.quantity} x {item.price} = KES {item.quantity * item.price}"
                logger.debug(f"Order Item: {item_info}")
                items_list.append(item_info)

            product_lines = "\n".join(f"- {line}" for line in items_list)

            # SMS Notification
            self._send_sms_notification(customer, order, product_lines)

            # Email Notification
            self._send_email_notification(customer, order, product_lines)

            logger.info(f"Successfully processed order #{order.id}")

        except Exception as e:
            logger.error(f"Failed to process notifications for order #{order.id}", exc_info=True)
            # Don't fail the order creation if notifications fail

        return order

    def _send_sms_notification(self, customer, order, product_lines):
        """Handle SMS notification with logging"""
        if not customer.phone_number:
            logger.warning(f"No phone number for customer {customer.id}, skipping SMS")
            return

        try:
            logger.debug("Initializing Africa's Talking SMS service")
            africastalking.initialize(
                username=settings.AFRICASTALKING_USERNAME,
                api_key=settings.AFRICASTALKING_API_KEY
            )
            sms = africastalking.SMS

            message = (f"Hello {customer.username}, your order #{order.id} for:\n{product_lines}\n"
                       f"Total: KES {order.total}")

            logger.info(f"Attempting to send SMS to {customer.phone_number}")
            response = sms.send(message, [customer.phone_number])
            logger.info(f"SMS sent to {customer.phone_number}. Response: {response}")

        except Exception as e:
            logger.error(f"Failed to send SMS to {customer.phone_number}", exc_info=True)
            raise

    def _send_email_notification(self, customer, order, product_lines):
        """Handle email notification with logging"""
        try:
            subject = f"New Order #{order.id}"
            message = (
                f"New order received:\n\n"
                f"Order ID: {order.id}\n"
                f"Customer: {customer.email}\n"
                f"Items:\n{product_lines}\n"
                f"Total: KES {order.total}"
            )

            logger.info(f"Attempting to send email to admin: {settings.ADMIN_EMAIL}")
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            logger.info(f"Email sent to admin: {settings.ADMIN_EMAIL}")

        except Exception as e:
            logger.error(f"Failed to send email to admin", exc_info=True)
            raise
