from datetime import datetime
from sqlalchemy import or_
from app import db
from app.api.v1.models.empleado import Empleado
from app.api.v1.schemas import validate_data, empleado_schema, empleado_update_schema

class EmpleadoService:
    """Servicio para gestionar empleados"""
    
    def create_empleado(self, empleado_data):
        """
        Crear un nuevo empleado
        
        Args:
            empleado_data (dict): Datos del empleado a crear
            
        Returns:
            tuple: (empleado, None) si la creación es exitosa, (None, error) si hay error
        """
        # Validar datos de entrada
        validated_data, errors = validate_data(empleado_schema, empleado_data)
        if errors:
            return None, errors
            
        # Verificar si ya existe un empleado con esa cédula
        if Empleado.query.filter_by(cedula=validated_data['cedula']).first():
            return None, {'cedula': ['Ya existe un empleado con esta cédula']}
        
        # Crear el nuevo empleado
        nuevo_empleado = Empleado(**validated_data)
        
        try:
            db.session.add(nuevo_empleado)
            db.session.commit()
            return nuevo_empleado, None
        except Exception as e:
            db.session.rollback()
            return None, {'database': [str(e)]}
    
    def get_empleado_by_id(self, empleado_id):
        """
        Obtener un empleado por su ID
        
        Args:
            empleado_id (int): ID del empleado
            
        Returns:
            Empleado or None: El empleado si existe, None si no
        """
        return Empleado.query.get(empleado_id)
    
    def get_empleado_by_cedula(self, cedula):
        """
        Obtener un empleado por su cédula
        
        Args:
            cedula (str): Cédula del empleado
            
        Returns:
            Empleado or None: El empleado si existe, None si no
        """
        return Empleado.query.filter_by(cedula=cedula).first()
    
    def get_all_empleados(self, page=1, per_page=20, **filters):
        """
        Obtener todos los empleados con paginación y filtros
        
        Args:
            page (int): Número de página
            per_page (int): Elementos por página
            **filters: Filtros adicionales (area, estado, unidad_productiva, busqueda)
            
        Returns:
            tuple: (empleados, total)
        """
        query = Empleado.query
        
        # Aplicar filtros
        if 'area' in filters and filters['area']:
            query = query.filter(Empleado.area == filters['area'])
        
        if 'estado' in filters:
            estado_val = True if filters['estado'] == 'true' else False
            query = query.filter(Empleado.estado == estado_val)
        
        if 'unidad_productiva' in filters and filters['unidad_productiva']:
            query = query.filter(Empleado.unidad_productiva == filters['unidad_productiva'])
        
        if 'busqueda' in filters and filters['busqueda']:
            search_term = f"%{filters['busqueda']}%"
            query = query.filter(
                or_(
                    Empleado.cedula.ilike(search_term),
                    Empleado.nombres.ilike(search_term),
                    Empleado.apellidos.ilike(search_term)
                )
            )
        
        # Ejecutar consulta con paginación
        pagination = query.order_by(Empleado.apellidos, Empleado.nombres).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return pagination.items, pagination.total
    
    def get_areas(self):
        """
        Obtener todas las áreas distintas de los empleados
        
        Returns:
            list: Lista de áreas únicas
        """
        areas = db.session.query(Empleado.area).distinct().all()
        return [area[0] for area in areas]
    
    def get_unidades_productivas(self):
        """
        Obtener todas las unidades productivas distintas
        
        Returns:
            list: Lista de unidades productivas únicas
        """
        unidades = db.session.query(Empleado.unidad_productiva).distinct().all()
        return [unidad[0] for unidad in unidades]
    
    def update_empleado(self, empleado_id, empleado_data):
        """
        Actualizar información de un empleado
        
        Args:
            empleado_id (int): ID del empleado a actualizar
            empleado_data (dict): Datos a actualizar
            
        Returns:
            tuple: (empleado, None) si la actualización es exitosa, (None, error) si hay error
        """
        # Buscar el empleado
        empleado = Empleado.query.get(empleado_id)
        if not empleado:
            return None, {'empleado': ['Empleado no encontrado']}
        
        # Validar datos de entrada
        validated_data, errors = validate_data(empleado_update_schema, empleado_data, partial=True)
        if errors:
            return None, errors
        
        # Si se actualiza la cédula, verificar que no exista otro empleado con esa cédula
        if 'cedula' in validated_data and validated_data['cedula'] != empleado.cedula:
            existe = Empleado.query.filter_by(cedula=validated_data['cedula']).first()
            if existe and existe.id != empleado_id:
                return None, {'cedula': ['Ya existe otro empleado con esta cédula']}
        
        # Actualizar campos
        for key, value in validated_data.items():
            setattr(empleado, key, value)
        
        try:
            db.session.commit()
            return empleado, None
        except Exception as e:
            db.session.rollback()
            return None, {'database': [str(e)]}
    
    def delete_empleado(self, empleado_id):
        """
        Eliminar un empleado (marcarlo como inactivo)
        
        Args:
            empleado_id (int): ID del empleado a eliminar
            
        Returns:
            bool: True si la eliminación es exitosa, False si hay error
        """
        empleado = Empleado.query.get(empleado_id)
        if not empleado:
            return False
        
        empleado.estado = False
        
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
    
    def get_empleados_by_unidad(self, unidad_productiva):
        """
        Obtener todos los empleados de una unidad productiva
        
        Args:
            unidad_productiva (str): Nombre de la unidad productiva
            
        Returns:
            list: Lista de empleados
        """
        return Empleado.query.filter_by(unidad_productiva=unidad_productiva, estado=True).all()
    
    def get_empleados_by_area(self, area):
        """
        Obtener todos los empleados de un área
        
        Args:
            area (str): Nombre del área
            
        Returns:
            list: Lista de empleados
        """
        return Empleado.query.filter_by(area=area, estado=True).all()