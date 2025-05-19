import re
import bleach
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from app.api.v1.services import empleado_service
from app.utils.security import sanitize_input, validate_input_length

class EmpleadoController:
    """Controlador para gestionar empleados"""
    
    def create_empleado(self):
        """Maneja la creación de nuevos empleados"""
        try:
            # Validar formato de solicitud
            if not request.is_json:
                return jsonify({'error': 'Solicitud debe ser JSON'}), 400
                
            data = request.get_json()
            
            # Sanitizar campos de texto
            for key in ['cedula', 'nombres', 'apellidos', 'area', 'cargo', 'unidad_productiva']:
                if key in data and isinstance(data[key], str):
                    data[key] = sanitize_input(data[key])
                    
                    # Validar longitud
                    max_length = 20 if key == 'cedula' else 100
                    if not validate_input_length(data[key], min_length=2, max_length=max_length):
                        return jsonify({'error': f'Campo {key} tiene longitud inválida'}), 400
            
            # Validar cédula (permitir solo dígitos y guiones)
            if 'cedula' in data:
                if not re.match(r'^[0-9-]+$', data['cedula']):
                    return jsonify({'error': 'Cédula debe contener solo números y guiones'}), 400
            
            # Crear empleado vía servicio
            empleado, error = empleado_service.create_empleado(data)
            
            if error:
                return jsonify({'error': error}), 400
                
            return jsonify({
                'message': 'Empleado creado exitosamente',
                'empleado': empleado.to_dict()
            }), 201
                
        except BadRequest:
            return jsonify({'error': 'JSON inválido'}), 400
        except Exception as e:
            print(f"Error creando empleado: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def get_empleado(self, empleado_id):
        """Obtiene información de un empleado por ID"""
        try:
            # Validar ID
            try:
                empleado_id = int(empleado_id)
            except ValueError:
                return jsonify({'error': 'ID de empleado debe ser un número'}), 400
                
            empleado = empleado_service.get_empleado_by_id(empleado_id)
            
            if not empleado:
                return jsonify({'error': 'Empleado no encontrado'}), 404
                
            return jsonify(empleado.to_dict()), 200
                
        except Exception as e:
            print(f"Error obteniendo empleado: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def get_empleado_by_cedula(self):
        """Obtiene información de un empleado por cédula"""
        try:
            cedula = request.args.get('cedula')
            
            if not cedula:
                return jsonify({'error': 'Se requiere la cédula'}), 400
                
            # Sanitizar cédula
            cedula = sanitize_input(cedula)
            
            # Validar formato
            if not re.match(r'^[0-9-]+$', cedula):
                return jsonify({'error': 'Formato de cédula inválido'}), 400
                
            empleado = empleado_service.get_empleado_by_cedula(cedula)
            
            if not empleado:
                return jsonify({'error': 'Empleado no encontrado'}), 404
                
            return jsonify(empleado.to_dict()), 200
                
        except Exception as e:
            print(f"Error buscando empleado por cédula: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def get_empleados(self):
        """Obtiene lista de empleados con filtros"""
        try:
            # Obtener parámetros de consulta
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)  # Limitar a 100
            
            # Sanitizar filtros
            filters = {}
            valid_filters = ['area', 'estado', 'unidad_productiva', 'busqueda']
            
            for f in valid_filters:
                if f in request.args:
                    filters[f] = sanitize_input(request.args.get(f))
            
            # Obtener empleados vía servicio
            empleados, total = empleado_service.get_all_empleados(page, per_page, **filters)
            
            return jsonify({
                'empleados': [e.to_dict() for e in empleados],
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total // per_page) + (1 if total % per_page > 0 else 0)
            }), 200
                
        except Exception as e:
            print(f"Error obteniendo empleados: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def update_empleado(self, empleado_id):
        """Actualiza información de un empleado"""
        try:
            # Validar ID
            try:
                empleado_id = int(empleado_id)
            except ValueError:
                return jsonify({'error': 'ID de empleado debe ser un número'}), 400
            
            # Validar formato de solicitud
            if not request.is_json:
                return jsonify({'error': 'Solicitud debe ser JSON'}), 400
                
            data = request.get_json()
            
            # Sanitizar campos de texto
            for key in data.keys():
                if isinstance(data[key], str):
                    data[key] = sanitize_input(data[key])
                    
                    # Validar longitud para campos de texto
                    if key in ['cedula', 'nombres', 'apellidos', 'area', 'cargo', 'unidad_productiva']:
                        max_length = 20 if key == 'cedula' else 100
                        if not validate_input_length(data[key], min_length=2, max_length=max_length):
                            return jsonify({'error': f'Campo {key} tiene longitud inválida'}), 400
            
            # Validar cédula si está presente
            if 'cedula' in data:
                if not re.match(r'^[0-9-]+$', data['cedula']):
                    return jsonify({'error': 'Cédula debe contener solo números y guiones'}), 400
            
            # Actualizar vía servicio
            empleado, error = empleado_service.update_empleado(empleado_id, data)
            
            if error:
                return jsonify({'error': error}), 400
                
            return jsonify({
                'message': 'Empleado actualizado exitosamente',
                'empleado': empleado.to_dict()
            }), 200
                
        except BadRequest:
            return jsonify({'error': 'JSON inválido'}), 400
        except Exception as e:
            print(f"Error actualizando empleado: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def delete_empleado(self, empleado_id):
        """Elimina (desactiva) un empleado"""
        try:
            # Validar ID
            try:
                empleado_id = int(empleado_id)
            except ValueError:
                return jsonify({'error': 'ID de empleado debe ser un número'}), 400
                
            # Eliminar vía servicio
            result = empleado_service.delete_empleado(empleado_id)
            
            if not result:
                return jsonify({'error': 'Empleado no encontrado'}), 404
                
            return jsonify({'message': 'Empleado desactivado exitosamente'}), 200
                
        except Exception as e:
            print(f"Error eliminando empleado: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def get_areas(self):
        """Obtiene lista de áreas disponibles"""
        try:
            areas = empleado_service.get_areas()
            return jsonify(areas), 200
        except Exception as e:
            print(f"Error obteniendo áreas: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def get_unidades_productivas(self):
        """Obtiene lista de unidades productivas disponibles"""
        try:
            unidades = empleado_service.get_unidades_productivas()
            return jsonify(unidades), 200
        except Exception as e:
            print(f"Error obteniendo unidades productivas: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500