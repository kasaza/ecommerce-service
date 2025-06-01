from django.db import models
from customers.models import Customer
from products.models import Product


class Order(models.Model):
    PENDING = 'P'
    COMPLETED = 'C'
    CANCELLED = 'X'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.get_status_display()}"

    @property
    def total_price(self):
        if self.total:  # If we have a pre-calculated total
            return self.total
        return sum(item.price * item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ {self.price}"
