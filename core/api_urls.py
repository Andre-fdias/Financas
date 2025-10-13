from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import api_views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'contas', api_views.ContaBancariaViewSet, basename='conta')
router.register(r'categorias', api_views.CategoriaViewSet, basename='categoria')
router.register(r'subcategorias', api_views.SubcategoriaViewSet, basename='subcategoria')
router.register(r'transacoes', api_views.TransactionViewSet, basename='transacao')
router.register(r'profile', api_views.ProfileViewSet, basename='profile')
router.register(r'relatorios', api_views.ReportsViewSet, basename='relatorio')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    
    # Auth endpoints
    path('auth/register/', api_views.RegisterView.as_view(), name='api_register'),
    path('auth/user/', api_views.CurrentUserView.as_view(), name='api_current_user'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Dashboard endpoint
    path('dashboard/', api_views.DashboardView.as_view(), name='api_dashboard'),
]