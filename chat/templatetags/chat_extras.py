from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter para acessar item de dicionário por chave"""
    if dictionary is None:
        return 0
    return dictionary.get(key, 0)
