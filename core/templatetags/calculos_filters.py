from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtrai arg de value"""
    try:
        return value - arg
    except (ValueError, TypeError):
        return value

@register.filter
def div(value, arg):
    """Divide value por arg"""
    try:
        if arg != 0:
            return value / arg
        return 0
    except (ValueError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    """Multiplica value por arg"""
    try:
        return value * arg
    except (ValueError, TypeError):
        return value