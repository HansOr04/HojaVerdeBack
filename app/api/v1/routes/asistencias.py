from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.api.v1 import bp
from app.api.v1.controllers import asistencia_controller

# Rutas para registro y gestión de asistencias
@bp.route('/asistencias/registrar', methods=['POST'])
@jwt_required()
def registrar_asistencia():
    """
    Registra entrada o salida de un empleado
    Requiere autenticación
    """
    return asistencia_controller.registrar_asistencia()

@bp.route('/asistencias', methods=['GET'])
@jwt_required()
def get_asistencias():
    """
    Obtiene lista de asistencias con filtros y paginación
    Requiere autenticación
    """
    return asistencia_controller.get_asistencias()

@bp.route('/asistencias/<int:asistencia_id>', methods=['GET'])
@jwt_required()
def get_asistencia(asistencia_id):
    """
    Obtiene información de una asistencia específica
    Requiere autenticación
    """
    return asistencia_controller.get_asistencia(asistencia_id)

@bp.route('/asistencias/empleado/<int:empleado_id>', methods=['GET'])
@jwt_required()
def get_asistencias_empleado(empleado_id):
    """
    Obtiene asistencias de un empleado específico
    Requiere autenticación
    """
    return asistencia_controller.get_asistencias_empleado(empleado_id)

@bp.route('/asistencias/hoy/empleado/<int:empleado_id>', methods=['GET'])
@jwt_required()
def get_asistencia_hoy(empleado_id):
    """
    Obtiene la asistencia del día actual para un empleado
    Requiere autenticación
    """
    return asistencia_controller.get_asistencia_hoy(empleado_id)

@bp.route('/asistencias/<int:asistencia_id>/aprobar', methods=['PUT'])
@jwt_required()
def aprobar_asistencia(asistencia_id):
    """
    Aprueba o rechaza una asistencia
    Requiere autenticación y rol administrador o talento_humano
    """
    # Verificar permisos
    claims = get_jwt()
    if 'rol' not in claims or claims['rol'] not in ['administrador', 'talento_humano']:
        return jsonify({'error': 'Acceso no autorizado'}), 403
    
    # Agregar ID de usuario al header para el controlador
    from flask import request
    request.headers = request.headers.environ_copy()
    request.headers['X-Usuario-ID'] = str(get_jwt_identity())
    
    return asistencia_controller.aprobar_asistencia(asistencia_id)

@bp.route('/asistencias/horas/empleado/<int:empleado_id>', methods=['GET'])
@jwt_required()
def calcular_horas(empleado_id):
    """
    Calcula horas trabajadas y extras de un empleado en un período
    Requiere autenticación
    """
    return asistencia_controller.calcular_horas(empleado_id)

@bp.route('/asistencias/reporte', methods=['GET'])
@jwt_required()
def generar_reporte():
    """
    Genera reporte de asistencias por período y criterios
    Requiere autenticación y rol administrador o talento_humano
    """
    # Verificar permisos
    claims = get_jwt()
    if 'rol' not in claims or claims['rol'] not in ['administrador', 'talento_humano']:
        return jsonify({'error': 'Acceso no autorizado'}), 403
        
    return asistencia_controller.generar_reporte()