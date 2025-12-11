from django import template

register = template.Library()

# Permite iterar con un índice: {% for index, item in lista|enumerate %}
@register.filter
def enumerate(iterable):
    return zip(range(len(iterable)), iterable)

# Permite acceder a un elemento de la lista/diccionario con un índice: {{ lista|get_item:index }}
@register.filter
def get_item(dictionary, key):
    """Filtro para acceder a diccionarios en templates"""
    if dictionary is None:
        return None
    
    # Convertir key a string si es necesario
    key_str = str(key)
    
    # Si es un diccionario
    if hasattr(dictionary, 'get'):
        return dictionary.get(key_str)
    
    # Si es una lista/tupla
    try:
        # Intentar como entero
        key_int = int(key)
        return dictionary[key_int]
    except (ValueError, IndexError, TypeError):
        return None

@register.filter
def slice(value, arg):
    """Filtro para hacer slicing en templates"""
    try:
        if ':' in arg:
            start, end = arg.split(':')
            start = int(start) if start else 0
            end = int(end) if end else None
            return value[start:end]
        else:
            # Si no hay :, es solo el final
            return value[:int(arg)]
    except:
        return value
    
@register.filter
def length(value):
    try:
        return len(value)
    except:
        return 0