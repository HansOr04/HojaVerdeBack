from app import db
from datetime import datetime

class Empleado(db.Model):
    __tablename__ = 'empleados'
    
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)
    fecha_ingreso = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    estado = db.Column(db.Boolean, default=True)
    unidad_productiva = db.Column(db.String(100), default='JOYGARDENS')
    
    # Relaciones
    asistencias = db.relationship('Asistencia', backref='empleado', lazy='dynamic',
                                 foreign_keys='Asistencia.empleado_id')
    
    def __repr__(self):
        return f'<Empleado {self.nombres} {self.apellidos}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'cedula': self.cedula,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'nombre_completo': f"{self.nombres} {self.apellidos}",
            'area': self.area,
            'cargo': self.cargo,
            'fecha_ingreso': self.fecha_ingreso.strftime('%Y-%m-%d'),
            'estado': self.estado,
            'unidad_productiva': self.unidad_productiva
        }
    
    @staticmethod
    def from_dict(data):
        """Método para crear o actualizar un empleado desde un diccionario"""
        campos_requeridos = ['cedula', 'nombres', 'apellidos', 'area', 'cargo']
        for campo in campos_requeridos:
            if campo not in data:
                raise ValueError(f"El campo '{campo}' es requerido")
        
        return {
            'cedula': data.get('cedula'),
            'nombres': data.get('nombres'),
            'apellidos': data.get('apellidos'),
            'area': data.get('area'),
            'cargo': data.get('cargo'),
            'fecha_ingreso': datetime.strptime(data.get('fecha_ingreso'), '%Y-%m-%d') if data.get('fecha_ingreso') else datetime.utcnow(),
            'estado': data.get('estado', True),
            'unidad_productiva': data.get('unidad_productiva', 'JOYGARDENS')
        }