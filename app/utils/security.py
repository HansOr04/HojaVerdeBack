import re
import bleach
from datetime import datetime

def sanitize_input(input_str):
    """
    Sanitiza una entrada para prevenir XSS y otros ataques
    
    Args:
        input_str: La cadena a sanitizar
        
    Returns:
        str: La cadena sanitizada
    """
    if not isinstance(input_str, str):
        return input_str
        
    # Eliminar caracteres no imprimibles
    input_str = ''.join(c for c in input_str if c.isprintable())
    
    # Sanitizar HTML con bleach
    allowed_tags = []  # No permitir ninguna etiqueta HTML
    allowed_attrs = {}
    input_str = bleach.clean(input_str, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    
    return input_str

def validate_input_length(input_str, min_length=1, max_length=255):
    """
    Valida que una cadena tenga una longitud adecuada
    para prevenir ataques de desbordamiento
    
    Args:
        input_str: La cadena a validar
        min_length: Longitud mínima permitida
        max_length: Longitud máxima permitida
        
    Returns:
        bool: True si la longitud es válida, False si no
    """
    if not isinstance(input_str, str):
        return False
        
    length = len(input_str)
    return min_length <= length <= max_length

def validate_date_format(date_str):
    """
    Valida que una fecha tenga el formato YYYY-MM-DD
    
    Args:
        date_str: La cadena a validar
        
    Returns:
        bool: True si el formato es válido, False si no
    """
    if not isinstance(date_str, str):
        return False
        
    # Verificar patrón YYYY-MM-DD
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False
        
    # Verificar que es una fecha válida
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def sanitize_sql_params(params):
    """
    Sanitiza parámetros para prevenir inyección SQL
    
    Args:
        params: Lista o diccionario de parámetros
        
    Returns:
        Los parámetros sanitizados
    """
    if isinstance(params, dict):
        return {k: sanitize_input(v) if isinstance(v, str) else v for k, v in params.items()}
    elif isinstance(params, list):
        return [sanitize_input(v) if isinstance(v, str) else v for v in params]
    elif isinstance(params, str):
        return sanitize_input(params)
    else:
        return params

def generate_safe_filename(filename):
    """
    Genera un nombre de archivo seguro
    
    Args:
        filename: Nombre de archivo original
        
    Returns:
        str: Nombre de archivo sanitizado
    """
    # Mantener solo caracteres alfanuméricos, punto, guion y guion bajo
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Limitar longitud
    if len(safe_filename) > 100:
        extension = safe_filename.split('.')[-1] if '.' in safe_filename else ''
        safe_filename = safe_filename[:95] + '.' + extension
        
    return safe_filename

def is_valid_id(id_value):
    """
    Verifica si un valor es un ID válido (entero positivo)
    
    Args:
        id_value: El valor a verificar
        
    Returns:
        bool: True si es válido, False si no
    """
    try:
        id_int = int(id_value)
        return id_int > 0
    except (ValueError, TypeError):
        return False