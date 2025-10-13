from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Retorna o valor de um dicionário para uma chave específica
    Suporta dicionários Python normais e listas de tuplas
    """
    if dictionary is None:
        return ''
    
    # Se for um dicionário Python
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    
    # Se for uma lista de tuplas (como choices do Django)
    elif isinstance(dictionary, (list, tuple)):
        # Procura pela chave na lista de tuplas
        for item in dictionary:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                if str(item[0]) == str(key):
                    return item[1]
    
    return ''

@register.filter
def abs(value):
    """Retorna o valor absoluto de um número"""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value

@register.filter
def direction_arrow(value):
    """Retorna uma seta para cima ou para baixo baseado no valor"""
    try:
        if float(value) >= 0:
            return "↑"  # Seta para cima
        else:
            return "↓"  # Seta para baixo
    except (ValueError, TypeError):
        return ""

@register.filter
def classname(obj):
    return obj.__class__.__name__

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def br_currency(value):
    """Formata valor como moeda brasileira"""
    if value is None:
        return 'R$ 0,00'
    try:
        # Converte para float e formata
        value_float = float(value)
        return f'R$ {value_float:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return 'R$ 0,00'