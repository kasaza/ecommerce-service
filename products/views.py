# products/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from products.models import Category, Product
from products.serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductUploadSerializer,
    CategoryStatsSerializer
)
import csv
from io import TextIOWrapper
from django.db.models import Avg


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='stats', permission_classes=[IsAdminUser])
    def category_stats(self, request):
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({'error': 'category_id parameter is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'},
                            status=status.HTTP_404_NOT_FOUND)

        categories = category.get_descendants(include_self=True)
        products = Product.objects.filter(categories__in=categories).distinct()

        # Calculate average price with proper decimal handling
        avg_price = products.aggregate(avg_price=Avg('price'))['avg_price']
        if avg_price is None:
            avg_price = 0
        else:
            avg_price = round(float(avg_price), 2)

        data = {
            'category': category.id,
            'average_price': avg_price,
            'product_count': products.count(),
        }

        serializer = CategoryStatsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'upload']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], serializer_class=ProductUploadSerializer, permission_classes=[IsAdminUser])
    def upload(self, request):
        serializer = ProductUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']
        decoded_file = TextIOWrapper(file, encoding='utf-8')
        reader = csv.DictReader(decoded_file)

        products_created = 0
        for row in reader:
            categories = row.get('categories', '').split(',')
            category_objs = []
            for cat_id in categories:
                if cat_id.strip():
                    try:
                        category_objs.append(Category.objects.get(id=int(cat_id.strip())))
                    except Category.DoesNotExist:
                        continue

            product_data = {
                'name': row['name'],
                'description': row.get('description', ''),
                'price': row['price'],
                'stock_quantity': row.get('stock_quantity', 0),
            }

            product_serializer = ProductSerializer(data=product_data)
            if product_serializer.is_valid():
                product = product_serializer.save()
                product.categories.set(category_objs)
                products_created += 1

        return Response({'status': f'{products_created} products created'}, status=status.HTTP_201_CREATED)
