import africastalking
from django.core.mail import send_mail
from django.conf import settings
from orders.models import Order


def initialize_africastalking():
    africastalking.initialize(
        username=settings.AFRICASTALKING_USERNAME,
        api_key=settings.AFRICASTALKING_API_KEY
    )
    return africastalking.SMS


def send_order_confirmation_sms(order_id):
    order = Order.objects.get(pk=order_id)
    sms = initialize_africastalking()

    message = f"Hello {order.customer.username}, your order #{order.id} has been received. Total: {order.total}"

    try:
        response = sms.send(message, [order.customer.phone_number])
        return response
    except Exception as e:
        print(f"SMS sending failed: {str(e)}")
        raise


def send_order_notification_email(order_id):
    order = Order.objects.get(pk=order_id)
    subject = f"New Order #{order.id} Received"
    message = f"""
    New order details:
    Customer: {order.customer.email}
    Total: {order.total}
    Items:
    {''.join(f"{item.product.name} - {item.quantity} x {item.unit_price}" for item in order.items.all())}
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=False,
    )