from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.api.v1 import bp
from app.api.v1.controllers import auth_controller

# Rutas para autenticación
@bp.route('/auth/register', methods=['POST'])
@jwt_required()
def register_usuario():
    """
    Registra un nuevo usuario
    Requiere autenticación y rol administrador
    """
    # Verificar permiso de administrador
    claims = get_jwt()
    if 'rol' not in claims or claims['rol'] != 'administrador':
        return jsonify({'error': 'Acceso no autorizado'}), 403
        
    return auth_controller.register()

@bp.route('/auth/login', methods=['POST'])
def login():
    """
    Inicia sesión y devuelve token JWT
    """
    return auth_controller.login()

# Rutas para gestión de usuarios
@bp.route('/usuarios', methods=['GET'])
@jwt_required()
def get_usuarios():
    """
    Obtiene lista de usuarios
    Requiere autenticación
    """
    # Verificar permisos (solo administrador o talento_humano pueden ver todos los usuarios)
    claims = get_jwt()
    if 'rol' not in claims or claims['rol'] not in ['administrador', 'talento_humano']:
        return jsonify({'error': 'Acceso no autorizado'}), 403
        
    return auth_controller.get_usuarios()

@bp.route('/usuarios/<int:usuario_id>', methods=['GET'])
@jwt_required()
def get_usuario(usuario_id):
    """
    Obtiene información de un usuario específico
    Requiere autenticación y ser el propio usuario o administrador
    """
    # Verificar que sea el propio usuario o un administrador
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    if usuario_id != current_user_id and ('rol' not in claims or claims['rol'] != 'administrador'):
        return jsonify({'error': 'Acceso no autorizado'}), 403
        
    return auth_controller.get_usuario(usuario_id)

@bp.route('/usuarios/<int:usuario_id>', methods=['PUT'])
@jwt_required()
def update_usuario(usuario_id):
    """
    Actualiza información de un usuario
    Requiere autenticación y ser el propio usuario o administrador
    """
    # Verificar que sea el propio usuario o un administrador
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    if usuario_id != current_user_id and ('rol' not in claims or claims['rol'] != 'administrador'):
        return jsonify({'error': 'Acceso no autorizado'}), 403
        
    return auth_controller.update_usuario(usuario_id)

@bp.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(usuario_id):
    """
    Elimina (desactiva) un usuario
    Requiere autenticación y rol administrador
    """
    # Verificar permiso de administrador
    claims = get_jwt()
    if 'rol' not in claims or claims['rol'] != 'administrador':
        return jsonify({'error': 'Acceso no autorizado'}), 403
        
    return auth_controller.delete_usuario(usuario_id)

@bp.route('/usuarios/perfil', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Obtiene información del usuario actual
    Requiere autenticación
    """
    current_user_id = get_jwt_identity()
    return auth_controller.get_usuario(current_user_id)