import pytest
from django.urls import reverse
from rest_framework import status
from products.models import Category, Product


@pytest.mark.django_db
def test_category_hierarchy():
    root = Category.objects.create(name="All Products")
    bakery = Category.objects.create(name="Bakery", parent=root)
    bread = Category.objects.create(name="Bread", parent=bakery)

    assert bread.get_ancestors() == [root, bakery]
    assert root.get_descendants() == [bakery, bread]


@pytest.mark.django_db
def test_average_price(api_client, product_factory):
    category = Category.objects.create(name="Test Category")
    product_factory.create_batch(3, price=10.00, categories=[category])

    url = reverse('product-average-price', kwargs={'category_id': category.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['avg_price'] == 10.00
