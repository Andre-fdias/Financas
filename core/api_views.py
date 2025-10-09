from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import ContaBancaria, Entrada, Saida, Categoria, Subcategoria
from .serializers import (
    RegisterSerializer,
    ContaBancariaSerializer, 
    EntradaSerializer, 
    SaidaSerializer,
    CategoriaSerializer,
    SubcategoriaSerializer,
    DashboardSerializer,
    TransactionSerializer,
    ProfileSerializer,
    ReportsSerializer
)

# View for user registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

# View to get current user data
class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# Base ViewSet to automatically filter by user
class UserFilteredViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """This view should return a list of all the objects
        for the currently authenticated user."""
        return self.queryset.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class ContaBancariaViewSet(UserFilteredViewSet):
    queryset = ContaBancaria.objects.all()
    serializer_class = ContaBancariaSerializer
    
    # Override get_queryset for ContaBancaria's owner field name
    def get_queryset(self):
        return self.queryset.filter(proprietario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(proprietario=self.request.user)

class CategoriaViewSet(UserFilteredViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class SubcategoriaViewSet(UserFilteredViewSet):
    queryset = Subcategoria.objects.all()
    serializer_class = SubcategoriaSerializer

class EntradaViewSet(UserFilteredViewSet):
    queryset = Entrada.objects.all()
    serializer_class = EntradaSerializer

class SaidaViewSet(UserFilteredViewSet):
    queryset = Saida.objects.all()
    serializer_class = SaidaSerializer

class TransactionViewSet(UserFilteredViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        entradas = Entrada.objects.filter(usuario=self.request.user)
        saidas = Saida.objects.filter(usuario=self.request.user)
        return list(entradas) + list(saidas)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        serializer.save()

class ReportsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_page(60 * 10)) # Cache de 10 minutos
    def list(self, request):
        report_data = []
        for categoria in Categoria.objects.filter(usuario=request.user):
            total_entradas = Entrada.objects.filter(usuario=request.user, categoria=categoria).aggregate(Sum('valor'))['valor__sum'] or 0
            total_saidas = Saida.objects.filter(usuario=request.user, categoria=categoria).aggregate(Sum('valor'))['valor__sum'] or 0
            report_data.append({
                'categoria': categoria.nome,
                'total_entradas': total_entradas,
                'total_saidas': total_saidas
            })

        serializer = ReportsSerializer(report_data, many=True)
        return Response(serializer.data)

class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_page(60 * 5)) # Cache de 5 minutos
    def get(self, request):
        total_entradas = Entrada.objects.filter(usuario=request.user).aggregate(Sum('valor'))['valor__sum'] or 0
        total_saidas = Saida.objects.filter(usuario=request.user).aggregate(Sum('valor'))['valor__sum'] or 0
        saldo_total = total_entradas - total_saidas

        serializer = DashboardSerializer({
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_total': saldo_total
        })

        return Response(serializer.data)
