"""
Módulo de utilidades para la aplicación.
Contiene funciones de utilidad compartidas entre diferentes partes de la aplicación.
"""

# Importar funciones de seguridad para hacerlas disponibles al importar el paquete utils
from app.utils.security import (
    sanitize_input,
    validate_input_length,
    validate_date_format,
    sanitize_sql_params,
    generate_safe_filename,
    is_valid_id
)

# Funciones de formato y conversión
def format_date(date_obj, format_str='%Y-%m-%d'):
    """
    Formatea un objeto fecha en una cadena según el formato especificado
    
    Args:
        date_obj: Objeto fecha a formatear
        format_str: Formato de salida (default: YYYY-MM-DD)
        
    Returns:
        str: Fecha formateada o cadena vacía si date_obj es None
    """
    if not date_obj:
        return ''
    return date_obj.strftime(format_str)

def format_time(time_obj, format_str='%H:%M:%S'):
    """
    Formatea un objeto tiempo en una cadena según el formato especificado
    
    Args:
        time_obj: Objeto tiempo a formatear
        format_str: Formato de salida (default: HH:MM:SS)
        
    Returns:
        str: Tiempo formateado o cadena vacía si time_obj es None
    """
    if not time_obj:
        return ''
    return time_obj.strftime(format_str)

def format_datetime(datetime_obj, format_str='%Y-%m-%d %H:%M:%S'):
    """
    Formatea un objeto datetime en una cadena según el formato especificado
    
    Args:
        datetime_obj: Objeto datetime a formatear
        format_str: Formato de salida (default: YYYY-MM-DD HH:MM:SS)
        
    Returns:
        str: Datetime formateado o cadena vacía si datetime_obj es None
    """
    if not datetime_obj:
        return ''
    return datetime_obj.strftime(format_str)

def format_decimal(value, decimal_places=2):
    """
    Formatea un valor decimal con el número especificado de lugares decimales
    
    Args:
        value: Valor a formatear
        decimal_places: Número de lugares decimales
        
    Returns:
        str: Valor formateado o '0.00' si value es None
    """
    if value is None:
        return f"0.{('0' * decimal_places)}"
    return f"{float(value):.{decimal_places}f}"

def get_pagination_info(pagination, **kwargs):
    """
    Genera información de paginación para respuestas API
    
    Args:
        pagination: Objeto de paginación de SQLAlchemy
        **kwargs: Parámetros adicionales para incluir en la respuesta
        
    Returns:
        dict: Información de paginación
    """
    return {
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        **kwargs
    }

# Constantes útiles
ESTADOS_ASISTENCIA = ['Pendiente', 'Aprobado', 'Rechazado']
ROLES_USUARIO = ['administrador', 'talento_humano', 'consulta']

# Funciones de validación específicas de negocio
def es_cedula_ecuatoriana_valida(cedula):
    """
    Valida si una cédula ecuatoriana es correcta según el algoritmo oficial
    
    Args:
        cedula: Número de cédula a validar
        
    Returns:
        bool: True si la cédula es válida, False si no
    """
    # Eliminar guiones o espacios
    cedula = cedula.replace('-', '').replace(' ', '')
    
    # Verificar longitud
    if len(cedula) != 10 or not cedula.isdigit():
        return False
    
    # Obtener dígitos
    digitos = [int(d) for d in cedula]
    
    # Verificar código de provincia (primeros dos dígitos)
    provincia = int(cedula[:2])
    if provincia < 1 or provincia > 24:
        return False
    
    # Algoritmo de validación
    ultimo = digitos[-1]
    
    # Verificar tercer dígito
    if digitos[2] > 6:
        return False
    
    # Verificar último dígito con algoritmo
    pares = sum(digitos[1:9:2])
    
    impares = 0
    for i in range(0, 9, 2):
        producto = digitos[i] * 2
        if producto > 9:
            producto -= 9
        impares += producto
    
    total = pares + impares
    verificador = 10 - (total % 10)
    if verificador == 10:
        verificador = 0
    
    return verificador == ultimo

# Funciones para manejo de errores
def format_error_response(errors, status_code=400):
    """
    Formatea errores para respuesta API consistente
    
    Args:
        errors: Diccionario de errores o mensaje de error
        status_code: Código de estado HTTP
        
    Returns:
        tuple: (respuesta_json, status_code)
    """
    if isinstance(errors, str):
        errors = {'error': [errors]}
    elif isinstance(errors, list):
        errors = {'error': errors}
    
    return {'errors': errors}, status_code