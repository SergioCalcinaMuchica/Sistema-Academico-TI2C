from django import template

register = template.Library()

@register.filter
def get_attribute(dictionary, key):
    """
    Permite acceder a un valor de diccionario (ej. 'estadisticas') 
    usando una clave dinámica, o a un atributo de un objeto (ej. 'matricula') 
    con una clave dinámica.
    """
    if isinstance(dictionary, dict) and key in dictionary:
        return dictionary.get(key)
    
    # Si no es un diccionario, intenta acceder como un atributo
    return getattr(dictionary, key, None)