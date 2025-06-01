# products/serializers.py
from rest_framework import serializers
from products.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'children']

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data


# products/serializers.py
class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False  # Make optional if needed
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'categories', 'stock_quantity']


class ProductUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed")
        return value


# products/serializers.py
class CategoryStatsSerializer(serializers.Serializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    average_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False  # Return as float instead of string
    )
    product_count = serializers.IntegerField()
