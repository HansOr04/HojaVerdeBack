import re
import bleach
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from app.api.v1.services import auth_service
from app.api.v1.schemas import validate_data, usuario_schema, usuario_login_schema, usuario_update_schema
from app.utils.security import sanitize_input, validate_input_length

class AuthController:
    """Controlador para gestionar autenticación y usuarios"""
    
    def register(self):
        """Maneja el registro de nuevos usuarios"""
        try:
            # Obtener y validar JSON
            if not request.is_json:
                return jsonify({'error': 'Solicitud debe ser JSON'}), 400
                
            data = request.get_json()
            
            # Sanitizar y validar entradas
            for key in ['nombre_usuario', 'password', 'nombre_completo', 'email']:
                if key in data:
                    # Sanitizar contra XSS
                    data[key] = sanitize_input(data[key])
                    
                    # Validar longitud para prevenir desbordamientos
                    if not validate_input_length(data[key], min_length=3, max_length=128):
                        return jsonify({'error': f'Campo {key} tiene longitud inválida'}), 400
            
            # Validaciones adicionales específicas
            if 'nombre_usuario' in data:
                # Solo permitir alfanumérico y guiones
                if not re.match(r'^[a-zA-Z0-9_-]+$', data['nombre_usuario']):
                    return jsonify({'error': 'Nombre de usuario solo puede contener letras, números, guiones y guion bajo'}), 400
            
            if 'email' in data:
                # Verificar formato de email
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
                    return jsonify({'error': 'Formato de email inválido'}), 400
            
            # Crear usuario vía servicio
            usuario, error = auth_service.register(data)
            
            if error:
                return jsonify({'error': error}), 400
                
            return jsonify({
                'message': 'Usuario creado exitosamente',
                'usuario': usuario.to_dict()
            }), 201
                
        except BadRequest as e:
            return jsonify({'error': 'JSON inválido'}), 400
        except Exception as e:
            # Loggear el error pero no exponer detalles al cliente
            print(f"Error en registro: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def login(self):
        """Maneja el login de usuarios"""
        try:
            # Obtener y validar JSON
            if not request.is_json:
                return jsonify({'error': 'Solicitud debe ser JSON'}), 400
                
            data = request.get_json()
            
            # Sanitizar entradas
            for key in ['nombre_usuario', 'password']:
                if key in data:
                    data[key] = sanitize_input(data[key])
            
            # Login vía servicio
            token_data, error = auth_service.login(data)
            
            if error:
                return jsonify({'error': error}), 401
                
            return jsonify(token_data), 200
                
        except BadRequest:
            return jsonify({'error': 'JSON inválido'}), 400
        except Exception as e:
            print(f"Error en login: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def get_usuario(self, usuario_id):
        """Obtiene información de un usuario por ID"""
        try:
            usuario = auth_service.get_usuario_by_id(usuario_id)
            
            if not usuario:
                return jsonify({'error': 'Usuario no encontrado'}), 404
                
            return jsonify(usuario.to_dict()), 200
                
        except Exception as e:
            print(f"Error obteniendo usuario: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def get_usuarios(self):
        """Obtiene lista de usuarios con filtros"""
        try:
            # Obtener parámetros de consulta
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)  # Limitar a 100 para prevenir DOS
            
            # Filtros (sanitizados)
            filters = {}
            valid_filters = ['rol', 'estado', 'busqueda']
            
            for f in valid_filters:
                if f in request.args:
                    filters[f] = sanitize_input(request.args.get(f))
            
            usuarios, total = auth_service.get_all_usuarios(page, per_page, **filters)
            
            return jsonify({
                'usuarios': [u.to_dict() for u in usuarios],
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total // per_page) + (1 if total % per_page > 0 else 0)
            }), 200
                
        except Exception as e:
            print(f"Error obteniendo usuarios: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def update_usuario(self, usuario_id):
        """Actualiza información de un usuario"""
        try:
            # Obtener y validar JSON
            if not request.is_json:
                return jsonify({'error': 'Solicitud debe ser JSON'}), 400
                
            data = request.get_json()
            
            # Sanitizar y validar entradas
            for key in data.keys():
                if isinstance(data[key], str):
                    data[key] = sanitize_input(data[key])
                    
                    # Validar longitud para campos de texto
                    if key in ['nombre_completo', 'email', 'password']:
                        if not validate_input_length(data[key], min_length=3, max_length=128):
                            return jsonify({'error': f'Campo {key} tiene longitud inválida'}), 400
            
            # Validaciones específicas
            if 'email' in data:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
                    return jsonify({'error': 'Formato de email inválido'}), 400
            
            # Actualizar vía servicio
            usuario, error = auth_service.update_usuario(usuario_id, data)
            
            if error:
                return jsonify({'error': error}), 400
                
            return jsonify({
                'message': 'Usuario actualizado exitosamente',
                'usuario': usuario.to_dict()
            }), 200
                
        except BadRequest:
            return jsonify({'error': 'JSON inválido'}), 400
        except Exception as e:
            print(f"Error actualizando usuario: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def delete_usuario(self, usuario_id):
        """Elimina (desactiva) un usuario"""
        try:
            result = auth_service.delete_usuario(usuario_id)
            
            if not result:
                return jsonify({'error': 'Usuario no encontrado'}), 404
                
            return jsonify({'message': 'Usuario desactivado exitosamente'}), 200
                
        except Exception as e:
            print(f"Error eliminando usuario: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500