from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.api.v1 import bp
from app.api.v1.controllers.empleado_controller import empleado_controller

# Rutas para gestión de empleados
@bp.route('/empleados', methods=['POST'])
@jwt_required()
def create_empleado():
    """
    Crea un nuevo empleado
    Requiere autenticación y rol administrador o talento_humano
    """
    # Verificar permisos
    claims = get_jwt()
    if 'rol' not in claims or claims['rol'] not in ['administrador', 'talento_humano']:
        return jsonify({'error': 'Acceso no autorizado'}), 403
        
    return empleado_controller.create_empleado()

@bp.route('/empleados', methods=['GET'])
@jwt_required()
def get_empleados():
    """
    Obtiene lista de empleados con filtros
    Requiere autenticación
    """
    return empleado_controller.get_empleados()

@bp.route('/empleados/<int:empleado_id>', methods=['GET'])
@jwt_required()
def get_empleado(empleado_id):
    """
    Obtiene información de un empleado específico
    Requiere autenticación
    """
    return empleado_controller.get_empleado(empleado_id)

@bp.route('/empleados/buscar', methods=['GET'])
@jwt_required()
def get_empleado_by_cedula():
    """
    Busca un empleado por su cédula
    Requiere autenticación
    """
    return empleado_controller.get_empleado_by_cedula()

@bp.route('/empleados/<int:empleado_id>', methods=['PUT'])
@jwt_required()
def update_empleado(empleado_id):
    """
    Actualiza información de un empleado
    Requiere autenticación y rol administrador o talento_humano
    """
    # Verificar permisos
    claims = get_jwt()
    if 'rol' not in claims or claims['rol'] not in ['administrador', 'talento_humano']:
        return jsonify({'error': 'Acceso no autorizado'}), 403
        
    return empleado_controller.update_empleado(empleado_id)

@bp.route('/empleados/<int:empleado_id>', methods=['DELETE'])
@jwt_required()
def delete_empleado(empleado_id):
    """
    Elimina (desactiva) un empleado
    Requiere autenticación y rol administrador o talento_humano
    """
    # Verificar permisos
    claims = get_jwt()
    if 'rol' not in claims or claims['rol'] not in ['administrador', 'talento_humano']:
        return jsonify({'error': 'Acceso no autorizado'}), 403
        
    return empleado_controller.delete_empleado(empleado_id)

@bp.route('/empleados/areas', methods=['GET'])
@jwt_required()
def get_areas():
    """
    Obtiene lista de áreas disponibles
    Requiere autenticación
    """
    return empleado_controller.get_areas()

@bp.route('/empleados/unidades', methods=['GET'])
@jwt_required()
def get_unidades():
    """
    Obtiene lista de unidades productivas disponibles
    Requiere autenticación
    """
    return empleado_controller.get_unidades_productivas()