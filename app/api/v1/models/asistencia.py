from app import db
from datetime import datetime
class Asistencia(db.Model):
tablename = 'asistencias'
id = db.Column(db.Integer, primary_key=True)
empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'), nullable=False)
fecha = db.Column(db.Date, nullable=False)
hora_entrada = db.Column(db.Time, nullable=True)
hora_salida = db.Column(db.Time, nullable=True)
horas_trabajadas = db.Column(db.Float, default=0)
horas_extras = db.Column(db.Float, default=0)
observaciones = db.Column(db.Text, nullable=True)
estado = db.Column(db.String(20), default='Pendiente')  # Pendiente, Aprobado, Rechazado
usuario_aprobacion = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
fecha_aprobacion = db.Column(db.DateTime, nullable=True)

def __repr__(self):
    return f'<Asistencia {self.empleado_id} {self.fecha}>'

def to_dict(self):
    return {
        'id': self.id,
        'empleado_id': self.empleado_id,
        'fecha': self.fecha.strftime('%Y-%m-%d'),
        'hora_entrada': self.hora_entrada.strftime('%H:%M:%S') if self.hora_entrada else None,
        'hora_salida': self.hora_salida.strftime('%H:%M:%S') if self.hora_salida else None,
        'horas_trabajadas': self.horas_trabajadas,
        'horas_extras': self.horas_extras,
        'observaciones': self.observaciones,
        'estado': self.estado,
        'usuario_aprobacion': self.usuario_aprobacion,
        'fecha_aprobacion': self.fecha_aprobacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_aprobacion else None
    }
