from flask import jsonify, request
from app.api.v1 import bp
from app.api.v1.models.usuario import Usuario
from app import db, jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
@bp.route('/auth/login', methods=['POST'])
def login():
data = request.get_json()
if not data or not data.get('nombre_usuario') or not data.get('password'):
return jsonify({'message': 'Faltan datos de acceso'}), 400
usuario = Usuario.query.filter_by(nombre_usuario=data['nombre_usuario']).first()
if not usuario or not usuario.check_password(data['password']):
    return jsonify({'message': 'Credenciales inválidas'}), 401

access_token = create_access_token(identity=usuario.id)
return jsonify({'token': access_token, 'usuario': usuario.to_dict()}), 200
@bp.route('/usuarios', methods=['GET'])
@jwt_required()
def get_usuarios():
usuarios = Usuario.query.all()
return jsonify([usuario.to_dict() for usuario in usuarios]), 200
