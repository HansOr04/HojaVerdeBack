from datetime import datetime
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from app.api.v1.services import asistencia_service
from app.utils.security import sanitize_input, validate_date_format

class AsistenciaController:
    """Controlador para gestionar asistencias"""
    
    def registrar_asistencia(self):
        """Maneja el registro de entrada/salida"""
        try:
            # Validar formato de solicitud
            if not request.is_json:
                return jsonify({'error': 'Solicitud debe ser JSON'}), 400
                
            data = request.get_json()
            
            # Sanitizar observaciones si existen
            if 'observaciones' in data and data['observaciones']:
                data['observaciones'] = sanitize_input(data['observaciones'])
            
            # Validar tipo de registro
            if 'tipo_registro' not in data or data['tipo_registro'] not in ['entrada', 'salida']:
                return jsonify({'error': 'Tipo de registro debe ser "entrada" o "salida"'}), 400
            
            # Validar ID de empleado
            if 'empleado_id' not in data:
                return jsonify({'error': 'Se requiere ID de empleado'}), 400
            
            try:
                data['empleado_id'] = int(data['empleado_id'])
            except ValueError:
                return jsonify({'error': 'ID de empleado debe ser un número'}), 400
            
            # Registrar vía servicio
            asistencia, mensaje, error = asistencia_service.registrar_asistencia(data)
            
            if error:
                return jsonify({'error': error}), 400
                
            return jsonify({
                'message': mensaje,
                'asistencia': asistencia.to_dict()
            }), 201
                
        except BadRequest:
            return jsonify({'error': 'JSON inválido'}), 400
        except Exception as e:
            print(f"Error registrando asistencia: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def get_asistencia(self, asistencia_id):
        """Obtiene información de una asistencia por ID"""
        try:
            # Validar ID
            try:
                asistencia_id = int(asistencia_id)
            except ValueError:
                return jsonify({'error': 'ID de asistencia debe ser un número'}), 400
                
            asistencia = asistencia_service.get_asistencia_by_id(asistencia_id)
            
            if not asistencia:
                return jsonify({'error': 'Asistencia no encontrada'}), 404
                
            return jsonify(asistencia.to_dict()), 200
                
        except Exception as e:
            print(f"Error obteniendo asistencia: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def get_asistencias_empleado(self, empleado_id):
        """Obtiene asistencias de un empleado con filtros de fecha"""
        try:
            # Validar ID
            try:
                empleado_id = int(empleado_id)
            except ValueError:
                return jsonify({'error': 'ID de empleado debe ser un número'}), 400
            
            # Obtener y validar fechas
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            
            # Parsear fechas si están presentes
            if fecha_inicio:
                if not validate_date_format(fecha_inicio):
                    return jsonify({'error': 'Formato de fecha_inicio inválido. Usar YYYY-MM-DD'}), 400
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                
            if fecha_fin:
                if not validate_date_format(fecha_fin):
                    return jsonify({'error': 'Formato de fecha_fin inválido. Usar YYYY-MM-DD'}), 400
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            # Obtener asistencias vía servicio
            asistencias = asistencia_service.get_asistencias_by_empleado(
                empleado_id, fecha_inicio, fecha_fin)
            
            return jsonify({
                'asistencias': [a.to_dict() for a in asistencias],
                'total': len(asistencias)
            }), 200
                
        except Exception as e:
            print(f"Error obteniendo asistencias: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def get_asistencia_hoy(self, empleado_id):
        """Obtiene la asistencia del día actual para un empleado"""
        try:
            # Validar ID
            try:
                empleado_id = int(empleado_id)
            except ValueError:
                return jsonify({'error': 'ID de empleado debe ser un número'}), 400
                
            asistencia = asistencia_service.get_asistencia_del_dia(empleado_id)
            
            if not asistencia:
                return jsonify({'message': 'No hay registro de asistencia para hoy'}), 404
                
            return jsonify(asistencia.to_dict()), 200
                
        except Exception as e:
            print(f"Error obteniendo asistencia del día: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def get_asistencias(self):
        """Obtiene lista de asistencias con filtros"""
        try:
            # Obtener parámetros de consulta
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)  # Limitar a 100
            
            # Preparar filtros
            filters = {}
            
            # Filtro por empleado
            if 'empleado_id' in request.args:
                try:
                    filters['empleado_id'] = int(request.args.get('empleado_id'))
                except ValueError:
                    return jsonify({'error': 'ID de empleado debe ser un número'}), 400
            
            # Filtros de fecha
            if 'fecha_inicio' in request.args:
                fecha_inicio = request.args.get('fecha_inicio')
                if not validate_date_format(fecha_inicio):
                    return jsonify({'error': 'Formato de fecha_inicio inválido. Usar YYYY-MM-DD'}), 400
                filters['fecha_inicio'] = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                
            if 'fecha_fin' in request.args:
                fecha_fin = request.args.get('fecha_fin')
                if not validate_date_format(fecha_fin):
                    return jsonify({'error': 'Formato de fecha_fin inválido. Usar YYYY-MM-DD'}), 400
                filters['fecha_fin'] = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            # Otros filtros (sanitizados)
            for f in ['estado', 'area', 'unidad_productiva']:
                if f in request.args:
                    filters[f] = sanitize_input(request.args.get(f))
            
            # Obtener asistencias vía servicio
            asistencias, total = asistencia_service.get_all_asistencias(page, per_page, **filters)
            
            return jsonify({
                'asistencias': [a.to_dict() for a in asistencias],
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total // per_page) + (1 if total % per_page > 0 else 0)
            }), 200
                
        except Exception as e:
            print(f"Error obteniendo asistencias: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def aprobar_asistencia(self, asistencia_id):
        """Aprueba o rechaza una asistencia"""
        try:
            # Validar ID
            try:
                asistencia_id = int(asistencia_id)
            except ValueError:
                return jsonify({'error': 'ID de asistencia debe ser un número'}), 400
            
            # Validar formato de solicitud
            if not request.is_json:
                return jsonify({'error': 'Solicitud debe ser JSON'}), 400
                
            data = request.get_json()
            
            # Validar estado
            if 'estado' not in data or data['estado'] not in ['Aprobado', 'Rechazado']:
                return jsonify({'error': 'Estado debe ser "Aprobado" o "Rechazado"'}), 400
            
            # Sanitizar observaciones si existen
            if 'observaciones' in data and data['observaciones']:
                data['observaciones'] = sanitize_input(data['observaciones'])
            
            # Extraer ID de usuario de JWT o request
            # En este caso asumimos que está en el request
            usuario_id = request.headers.get('X-Usuario-ID')
            if not usuario_id:
                return jsonify({'error': 'Se requiere ID de usuario para aprobar'}), 401
                
            try:
                usuario_id = int(usuario_id)
            except ValueError:
                return jsonify({'error': 'ID de usuario inválido'}), 400
            
            # Aprobar vía servicio
            asistencia, error = asistencia_service.aprobar_asistencia(asistencia_id, usuario_id, data)
            
            if error:
                return jsonify({'error': error}), 400
                
            return jsonify({
                'message': f'Asistencia {data["estado"].lower()} correctamente',
                'asistencia': asistencia.to_dict()
            }), 200
                
        except BadRequest:
            return jsonify({'error': 'JSON inválido'}), 400
        except Exception as e:
            print(f"Error aprobando asistencia: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def calcular_horas(self, empleado_id):
        """Calcula horas de un empleado en un período"""
        try:
            # Validar ID
            try:
                empleado_id = int(empleado_id)
            except ValueError:
                return jsonify({'error': 'ID de empleado debe ser un número'}), 400
            
            # Obtener y validar fechas (requeridas)
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            
            if not fecha_inicio or not fecha_fin:
                return jsonify({'error': 'Se requieren fecha_inicio y fecha_fin'}), 400
            
            # Validar formato de fechas
            if not validate_date_format(fecha_inicio) or not validate_date_format(fecha_fin):
                return jsonify({'error': 'Formato de fecha inválido. Usar YYYY-MM-DD'}), 400
            
            # Parsear fechas
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            # Validar que fecha_inicio sea menor o igual a fecha_fin
            if fecha_inicio > fecha_fin:
                return jsonify({'error': 'fecha_inicio debe ser menor o igual a fecha_fin'}), 400
            
            # Calcular vía servicio
            resultado = asistencia_service.calcular_horas_empleado(empleado_id, fecha_inicio, fecha_fin)
            
            if not resultado:
                return jsonify({'error': 'Empleado no encontrado'}), 404
                
            return jsonify({
                'empleado_id': empleado_id,
                'periodo': {
                    'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                    'fecha_fin': fecha_fin.strftime('%Y-%m-%d')
                },
                'resultados': resultado
            }), 200
                
        except Exception as e:
            print(f"Error calculando horas: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    def generar_reporte(self):
        """Genera un reporte de asistencias por período"""
        try:
            # Obtener y validar fechas (requeridas)
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            
            if not fecha_inicio or not fecha_fin:
                return jsonify({'error': 'Se requieren fecha_inicio y fecha_fin'}), 400
            
            # Validar formato de fechas
            if not validate_date_format(fecha_inicio) or not validate_date_format(fecha_fin):
                return jsonify({'error': 'Formato de fecha inválido. Usar YYYY-MM-DD'}), 400
            
            # Parsear fechas
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            # Validar que fecha_inicio sea menor o igual a fecha_fin
            if fecha_inicio > fecha_fin:
                return jsonify({'error': 'fecha_inicio debe ser menor o igual a fecha_fin'}), 400
            
            # Filtros (sanitizados)
            area = request.args.get('area')
            unidad_productiva = request.args.get('unidad_productiva')
            
            if area:
                area = sanitize_input(area)
                
            if unidad_productiva:
                unidad_productiva = sanitize_input(unidad_productiva)
            
            # Generar reporte vía servicio
            reporte = asistencia_service.generar_reporte_asistencias(
                fecha_inicio, fecha_fin, area, unidad_productiva)
            
            return jsonify(reporte), 200
                
        except Exception as e:
            print(f"Error generando reporte: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
            