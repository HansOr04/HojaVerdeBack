from app import db
from datetime import datetime
class Empleado(db.Model):
tablename = 'empleados'
id = db.Column(db.Integer, primary_key=True)
cedula = db.Column(db.String(20), unique=True, nullable=False)
nombres = db.Column(db.String(100), nullable=False)
apellidos = db.Column(db.String(100), nullable=False)
area = db.Column(db.String(100), nullable=False)
cargo = db.Column(db.String(100), nullable=False)
fecha_ingreso = db.Column(db.Date, nullable=False, default=datetime.utcnow)
estado = db.Column(db.Boolean, default=True)
unidad_productiva = db.Column(db.String(100), default='JOYGARDENS')

asistencias = db.relationship('Asistencia', backref='empleado', lazy='dynamic')

def __repr__(self):
    return f'<Empleado {self.nombres} {self.apellidos}>'

def to_dict(self):
    return {
        'id': self.id,
        'cedula': self.cedula,
        'nombres': self.nombres,
        'apellidos': self.apellidos,
        'area': self.area,
        'cargo': self.cargo,
        'fecha_ingreso': self.fecha_ingreso.strftime('%Y-%m-%d'),
        'estado': self.estado,
        'unidad_productiva': self.unidad_productiva
    }
