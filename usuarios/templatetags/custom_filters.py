from django import template

register = template.Library()

# Permite iterar con un índice: {% for index, item in lista|enumerate %}
@register.filter
def enumerate(iterable):
    return zip(range(len(iterable)), iterable)

# Permite acceder a un elemento de la lista/diccionario con un índice: {{ lista|get_item:index }}
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key) if hasattr(dictionary, 'get') else dictionary[key]