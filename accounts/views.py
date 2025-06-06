# auth/views.py
from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from mozilla_django_oidc.contrib.drf import OIDCAuthentication
from mozilla_django_oidc.views import OIDCAuthenticationRequestView, OIDCLogoutView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# class Auth0TokenAuthentication(OIDCAuthentication):
#     def authenticate(self, request):
#         auth_header = request.META.get('HTTP_AUTHORIZATION', '')
#
#         if not auth_header.startswith('Bearer '):
#             return None
#
#         return super().authenticate(request)


class CustomOIDCLoginView(OIDCAuthenticationRequestView):
    """Initiates OIDC login flow by redirecting user to Auth0."""

    def get_redirect_url(self):
        # Use the setting if defined, otherwise fall back to home
        return getattr(settings, 'LOGIN_REDIRECT_URL', reverse_lazy('home'))


class CustomOIDCLogoutView(OIDCLogoutView):
    """Handles both Django and Auth0 logout with proper redirects."""

    def get(self, request: HttpRequest):
        # Store the id_token before clearing session
        id_token = request.session.get('oidc_id_token')

        # Clear Django session completely
        django_logout(request)
        request.session.flush()

        # Generate the Auth0 logout URL
        logout_url = (
            f"https://{settings.OIDC_OP_DOMAIN}/v2/logout?"
            f"client_id={settings.OIDC_RP_CLIENT_ID}&"
            f"returnTo={settings.LOGOUT_REDIRECT_URL}"
        )

        if id_token:
            logout_url += f"&id_token_hint={id_token}"

        # Add &federated if full SSO logout is needed
        logout_url += "&federated"

        # Redirect to Auth0 for complete logout
        return redirect(logout_url)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth(request):
    user = request.user
    return Response({
        "authenticated": True,
        "username": user.username,
        "email": user.email,
    })


@login_required
def test_login(request: HttpRequest) -> HttpResponse:
    """Test endpoint to verify authentication status."""
    return HttpResponse(f"Hello {request.user.email or request.user.username}, you are logged in.")


def health_check(request):
    return JsonResponse({
        'status': 'OK',
        'message': 'Health check',
    })
