from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ContaBancaria, Entrada, Saida, Categoria, Subcategoria

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ('usuario',)

class SubcategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategoria
        fields = '__all__'
        read_only_fields = ('usuario',)

class ContaBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaBancaria
        fields = '__all__'
        read_only_fields = ('proprietario',)

class EntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrada
        fields = '__all__'
        read_only_fields = ('usuario',)

class SaidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Saida
        fields = '__all__'
        read_only_fields = ('usuario',)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance

class TransactionSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(write_only=True)

    class Meta:
        model = None  # This will be set dynamically
        fields = '__all__'

    def to_representation(self, instance):
        if isinstance(instance, Entrada):
            self.Meta.model = Entrada
            return super().to_representation(instance)
        elif isinstance(instance, Saida):
            self.Meta.model = Saida
            return super().to_representation(instance)
        return super().to_representation(instance)

    def create(self, validated_data):
        tipo = validated_data.pop('tipo')
        if tipo == 'entrada':
            self.Meta.model = Entrada
        elif tipo == 'saida':
            self.Meta.model = Saida
        else:
            raise serializers.ValidationError("O campo 'tipo' deve ser 'entrada' ou 'saida'.")
        
        return super().create(validated_data)

class ReportsSerializer(serializers.Serializer):
    categoria = serializers.CharField()
    total_entradas = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_saidas = serializers.DecimalField(max_digits=10, decimal_places=2)

class DashboardSerializer(serializers.Serializer):
    total_entradas = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_saidas = serializers.DecimalField(max_digits=15, decimal_places=2)
    saldo_total = serializers.DecimalField(max_digits=15, decimal_places=2)