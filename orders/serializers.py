from rest_framework import serializers
from products.models import Product
from orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_price',
            'quantity',
            'unit_price',
        ]
        extra_kwargs = {
            'product': {'write_only': True},
            'unit_price': {'read_only': True},
        }

    def validate_product(self, value):
        if not value.is_active:
            raise serializers.ValidationError("This product is not available")
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    status = serializers.CharField(read_only=True)
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'status',
            'total',
            'created_at',
            'updated_at',
            'items',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        order_items = []
        for item_data in items_data:
            product = item_data['product']
            order_items.append(OrderItem(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                unit_price=product.price
            ))

        OrderItem.objects.bulk_create(order_items)

        # Calculate total
        total = sum(
            item.quantity * item.unit_price
            for item in order_items
        )
        order.total = total
        order.save()

        return order

    def validate(self, data):
        items = data.get('items', [])
        if not items:
            raise serializers.ValidationError("Order must have at least one item")

        # Check product availability
        for item in items:
            product = item['product']
            if product.stock_quantity <= 0:
                raise serializers.ValidationError(
                    f"Product {product.name} is out of stock"
                )
            if item.get('quantity', 0) > product.stock_quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for {product.name}. Available: {product.stock_quantity}"
                )

        return data
