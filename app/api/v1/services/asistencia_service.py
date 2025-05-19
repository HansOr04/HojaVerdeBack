from datetime import datetime, time, timedelta
from sqlalchemy import func, and_, desc
from app import db
from app.api.v1.models.asistencia import Asistencia
from app.api.v1.models.empleado import Empleado
from app.api.v1.models.usuario import Usuario
from app.api.v1.schemas import validate_data, asistencia_schema, asistencia_registro_schema, asistencia_aprobacion_schema

class AsistenciaService:
    """Servicio para gestionar asistencias"""
    
    def registrar_asistencia(self, data):
        """
        Registrar entrada o salida de un empleado
        
        Args:
            data (dict): Datos del registro (empleado_id, tipo_registro, observaciones)
            
        Returns:
            tuple: (asistencia, mensaje, None) si el registro es exitoso, (None, None, error) si hay error
        """
        # Validar datos de entrada
        validated_data, errors = validate_data(asistencia_registro_schema, data)
        if errors:
            return None, None, errors
        
        # Verificar que el empleado existe y está activo
        empleado = Empleado.query.get(validated_data['empleado_id'])
        if not empleado:
            return None, None, {'empleado_id': ['Empleado no encontrado']}
        if not empleado.estado:
            return None, None, {'empleado_id': ['El empleado está inactivo']}
        
        # Obtener hora actual
        now = datetime.utcnow()
        current_time = now.time()
        
        # Registrar según el tipo (entrada o salida)
        if validated_data['tipo_registro'] == 'entrada':
            asistencia, mensaje = Asistencia.registrar_entrada(
                empleado_id=empleado.id,
                hora=current_time,
                observaciones=validated_data.get('observaciones')
            )
        else:  # salida
            asistencia, mensaje = Asistencia.registrar_salida(
                empleado_id=empleado.id,
                hora=current_time,
                observaciones=validated_data.get('observaciones')
            )
        
        if not asistencia:
            return None, None, {'registro': [mensaje]}
        
        try:
            db.session.add(asistencia)
            db.session.commit()
            return asistencia, mensaje, None
        except Exception as e:
            db.session.rollback()
            return None, None, {'database': [str(e)]}
    
    def get_asistencia_by_id(self, asistencia_id):
        """
        Obtener una asistencia por su ID
        
        Args:
            asistencia_id (int): ID de la asistencia
            
        Returns:
            Asistencia or None: La asistencia si existe, None si no
        """
        return Asistencia.query.get(asistencia_id)
    
    def get_asistencias_by_empleado(self, empleado_id, fecha_inicio=None, fecha_fin=None):
        """
        Obtener asistencias de un empleado en un rango de fechas
        
        Args:
            empleado_id (int): ID del empleado
            fecha_inicio (date, optional): Fecha de inicio del rango
            fecha_fin (date, optional): Fecha fin del rango
            
        Returns:
            list: Lista de asistencias
        """
        query = Asistencia.query.filter_by(empleado_id=empleado_id)
        
        if fecha_inicio:
            query = query.filter(Asistencia.fecha >= fecha_inicio)
        
        if fecha_fin:
            query = query.filter(Asistencia.fecha <= fecha_fin)
        
        return query.order_by(desc(Asistencia.fecha)).all()
    
    def get_asistencia_del_dia(self, empleado_id):
        """
        Obtener asistencia del día actual para un empleado
        
        Args:
            empleado_id (int): ID del empleado
            
        Returns:
            Asistencia or None: La asistencia del día si existe, None si no
        """
        hoy = datetime.utcnow().date()
        return Asistencia.query.filter_by(empleado_id=empleado_id, fecha=hoy).first()
    
    def get_all_asistencias(self, page=1, per_page=20, **filters):
        """
        Obtener todas las asistencias con paginación y filtros
        
        Args:
            page (int): Número de página
            per_page (int): Elementos por página
            **filters: Filtros adicionales (empleado_id, fecha_inicio, fecha_fin, estado)
            
        Returns:
            tuple: (asistencias, total)
        """
        query = Asistencia.query
        
        # Aplicar filtros
        if 'empleado_id' in filters and filters['empleado_id']:
            query = query.filter(Asistencia.empleado_id == filters['empleado_id'])
        
        if 'fecha_inicio' in filters and filters['fecha_inicio']:
            query = query.filter(Asistencia.fecha >= filters['fecha_inicio'])
        
        if 'fecha_fin' in filters and filters['fecha_fin']:
            query = query.filter(Asistencia.fecha <= filters['fecha_fin'])
        
        if 'estado' in filters and filters['estado']:
            query = query.filter(Asistencia.estado == filters['estado'])
        
        if 'area' in filters and filters['area']:
            query = query.join(Empleado).filter(Empleado.area == filters['area'])
        
        if 'unidad_productiva' in filters and filters['unidad_productiva']:
            query = query.join(Empleado).filter(Empleado.unidad_productiva == filters['unidad_productiva'])
        
        # Ejecutar consulta con paginación
        pagination = query.order_by(desc(Asistencia.fecha), Asistencia.empleado_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return pagination.items, pagination.total
    
    def aprobar_asistencia(self, asistencia_id, usuario_id, data):
        """
        Aprobar o rechazar una asistencia
        
        Args:
            asistencia_id (int): ID de la asistencia a aprobar
            usuario_id (int): ID del usuario que aprueba
            data (dict): Datos de aprobación (estado, observaciones)
            
        Returns:
            tuple: (asistencia, None) si la aprobación es exitosa, (None, error) si hay error
        """
        # Validar datos de entrada
        validated_data, errors = validate_data(asistencia_aprobacion_schema, data)
        if errors:
            return None, errors
        
        # Buscar la asistencia
        asistencia = Asistencia.query.get(asistencia_id)
        if not asistencia:
            return None, {'asistencia': ['Asistencia no encontrada']}
        
        # Verificar que la asistencia esté pendiente
        if asistencia.estado != 'Pendiente':
            return None, {'asistencia': ['Esta asistencia ya fue procesada']}
        
        # Verificar que el usuario exista
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return None, {'usuario': ['Usuario no encontrado']}
        
        # Verificar que el usuario tenga permisos (administrador o talento_humano)
        if usuario.rol not in ['administrador', 'talento_humano']:
            return None, {'permisos': ['No tiene permisos para realizar esta acción']}
        
        # Actualizar la asistencia
        asistencia.estado = validated_data['estado']
        asistencia.usuario_aprobacion = usuario_id
        asistencia.fecha_aprobacion = datetime.utcnow()
        
        if 'observaciones' in validated_data and validated_data['observaciones']:
            obs_prefix = "[Aprobación] " if validated_data['estado'] == 'Aprobado' else "[Rechazo] "
            if asistencia.observaciones:
                asistencia.observaciones += f"; {obs_prefix}{validated_data['observaciones']}"
            else:
                asistencia.observaciones = f"{obs_prefix}{validated_data['observaciones']}"
        
        try:
            db.session.commit()
            return asistencia, None
        except Exception as e:
            db.session.rollback()
            return None, {'database': [str(e)]}
    
    def calcular_horas_empleado(self, empleado_id, fecha_inicio, fecha_fin):
        """
        Calcular horas trabajadas y extras de un empleado en un período
        
        Args:
            empleado_id (int): ID del empleado
            fecha_inicio (date): Fecha de inicio del período
            fecha_fin (date): Fecha fin del período
            
        Returns:
            dict: Resumen de horas {total_trabajadas, total_extras, dias_asistidos, dias_faltantes}
        """
        # Verificar que el empleado existe
        empleado = Empleado.query.get(empleado_id)
        if not empleado:
            return None
        
        # Obtener asistencias aprobadas en el período
        asistencias = Asistencia.query.filter(
            Asistencia.empleado_id == empleado_id,
            Asistencia.fecha.between(fecha_inicio, fecha_fin),
            Asistencia.estado == 'Aprobado'
        ).all()
        
        # Calcular totales
        total_trabajadas = sum(a.horas_trabajadas for a in asistencias if a.horas_trabajadas is not None)
        total_extras = sum(a.horas_extras for a in asistencias if a.horas_extras is not None)
        dias_asistidos = len(asistencias)
        
        # Calcular días laborables en el período (lunes a sábado)
        dias_periodo = 0
        current_date = fecha_inicio
        while current_date <= fecha_fin:
            # 0 = lunes, 6 = domingo
            if current_date.weekday() != 6:  # No contar domingos
                dias_periodo += 1
            current_date += timedelta(days=1)
        
        dias_faltantes = dias_periodo - dias_asistidos
        
        return {
            'total_trabajadas': round(total_trabajadas, 2),
            'total_extras': round(total_extras, 2),
            'dias_asistidos': dias_asistidos,
            'dias_faltantes': dias_faltantes,
            'dias_periodo': dias_periodo
        }
    
    def generar_reporte_asistencias(self, fecha_inicio, fecha_fin, area=None, unidad_productiva=None):
        """
        Generar reporte de asistencias por período y criterios
        
        Args:
            fecha_inicio (date): Fecha de inicio del período
            fecha_fin (date): Fecha fin del período
            area (str, optional): Filtrar por área
            unidad_productiva (str, optional): Filtrar por unidad productiva
            
        Returns:
            dict: Reporte de asistencias
        """
        # Construir query base
        query = db.session.query(
            Empleado.id,
            Empleado.cedula,
            Empleado.nombres,
            Empleado.apellidos,
            Empleado.area,
            Empleado.unidad_productiva,
            func.sum(Asistencia.horas_trabajadas).label('total_trabajadas'),
            func.sum(Asistencia.horas_extras).label('total_extras'),
            func.count(Asistencia.id).label('dias_asistidos')
        ).join(
            Asistencia, 
            and_(
                Empleado.id == Asistencia.empleado_id,
                Asistencia.fecha.between(fecha_inicio, fecha_fin),
                Asistencia.estado == 'Aprobado'
            ),
            isouter=True
        ).group_by(
            Empleado.id,
            Empleado.cedula,
            Empleado.nombres,
            Empleado.apellidos,
            Empleado.area,
            Empleado.unidad_productiva
        )
        
        # Aplicar filtros
        if area:
            query = query.filter(Empleado.area == area)
        
        if unidad_productiva:
            query = query.filter(Empleado.unidad_productiva == unidad_productiva)
        
        # Filtrar solo empleados activos
        query = query.filter(Empleado.estado == True)
        
        # Ejecutar consulta
        results = query.all()
        
        # Calcular días laborables en el período (lunes a sábado)
        dias_periodo = 0
        current_date = fecha_inicio
        while current_date <= fecha_fin:
            # 0 = lunes, 6 = domingo
            if current_date.weekday() != 6:  # No contar domingos
                dias_periodo += 1
            current_date += timedelta(days=1)
        
        # Formatear resultados
        reporte = {
            'periodo': {
                'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
                'dias_laborables': dias_periodo
            },
            'filtros': {
                'area': area,
                'unidad_productiva': unidad_productiva
            },
            'resumen': {
                'total_empleados': len(results),
                'total_horas_trabajadas': round(sum(r.total_trabajadas or 0 for r in results), 2),
                'total_horas_extras': round(sum(r.total_extras or 0 for r in results), 2),
                'promedio_asistencia': round(sum(r.dias_asistidos or 0 for r in results) / len(results) if results else 0, 2)
            },
            'empleados': [
                {
                    'id': r.id,
                    'cedula': r.cedula,
                    'nombres': r.nombres,
                    'apellidos': r.apellidos,
                    'nombre_completo': f"{r.nombres} {r.apellidos}",
                    'area': r.area,
                    'unidad_productiva': r.unidad_productiva,
                    'horas_trabajadas': round(r.total_trabajadas or 0, 2),
                    'horas_extras': round(r.total_extras or 0, 2),
                    'dias_asistidos': r.dias_asistidos or 0,
                    'dias_faltantes': dias_periodo - (r.dias_asistidos or 0),
                    'porcentaje_asistencia': round(((r.dias_asistidos or 0) / dias_periodo) * 100, 2) if dias_periodo > 0 else 0
                }
                for r in results
            ]
        }
        
        return reporte