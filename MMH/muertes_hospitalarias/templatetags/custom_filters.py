from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def div(value, arg):
    """Divide value by arg."""
    try:
        return value / arg
    except (ZeroDivisionError, ValueError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiply value by arg."""
    return value * arg