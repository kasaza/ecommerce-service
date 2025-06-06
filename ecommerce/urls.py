# config/urls.py
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from products.views import CategoryViewSet, ProductViewSet
from orders.views import OrderViewSet
from accounts.views import CustomOIDCLoginView, CustomOIDCLogoutView, test_login, check_auth, health_check
from mozilla_django_oidc import views as oidc_views

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('oidc/login/', CustomOIDCLoginView.as_view(), name='oidc_authentication_init'),
    path('oidc/logout/', CustomOIDCLogoutView.as_view(), name='oidc_logout'),
    path('oidc/callback/', oidc_views.OIDCAuthenticationCallbackView.as_view(), name='oidc_authentication_callback'),

    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/check-auth/', check_auth, name='check-auth'),
    path('test-login/', test_login, name='test_login'),
    path('health/', health_check, name='health-check'),
]


