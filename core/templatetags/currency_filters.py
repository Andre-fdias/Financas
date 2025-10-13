# core/templatetags/currency_filters.py

from django import template
from decimal import Decimal, InvalidOperation
import locale # Importe o módulo locale

register = template.Library()


@register.filter
def br_currency(value):
    """
    Filtro para formatar valores monetários no padrão brasileiro.
    Ex: 1234.56 -> R$ 1.234,56
    """
    if value is None:
        return "R$ 0,00"
    
    try:
        # Tenta converter para Decimal se for string
        if isinstance(value, str):
            # Remove possíveis formatações anteriores
            value = value.replace('R$', '').replace('.', '').replace(',', '.').strip()
            value = Decimal(value)
        
        # Garante que é Decimal
        value = Decimal(str(value))
        
        # Formata para o padrão brasileiro
        formatted = f"R$ {value:,.2f}"
        # Substitui a formatação padrão para o padrão brasileiro
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        return formatted
    except (InvalidOperation, ValueError, TypeError):
        # Retorna valor padrão em caso de erro
        return "R$ 0,00"
    

@register.filter
def classname(obj):
    """Retorna o nome da classe do objeto"""
    return obj.__class__.__name__

@register.filter
def keys(dictionary):
    return list(dictionary.keys())

@register.filter
def values(dictionary):
    return list(dictionary.values())
