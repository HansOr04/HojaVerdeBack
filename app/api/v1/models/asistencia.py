from app import db
from datetime import datetime, time

class Asistencia(db.Model):
    __tablename__ = 'asistencias'
    
    id = db.Column(db.Integer, primary_key=True)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
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
    
    def calcular_horas(self):
        """Calcula las horas trabajadas y extras"""
        if not self.hora_entrada or not self.hora_salida:
            self.horas_trabajadas = 0
            self.horas_extras = 0
            return
        
        # Calcular diferencia en horas
        entrada_seconds = self.hora_entrada.hour * 3600 + self.hora_entrada.minute * 60 + self.hora_entrada.second
        salida_seconds = self.hora_salida.hour * 3600 + self.hora_salida.minute * 60 + self.hora_salida.second
        
        # Si la salida es antes que la entrada, asumimos que pasó la medianoche
        if salida_seconds < entrada_seconds:
            salida_seconds += 24 * 3600
            
        total_seconds = salida_seconds - entrada_seconds
        total_hours = total_seconds / 3600
        
        # Jornada normal: 6 horas
        jornada_normal = 6
        
        self.horas_trabajadas = min(total_hours, jornada_normal)
        self.horas_extras = max(0, total_hours - jornada_normal)
    
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
    
    @staticmethod
    def registrar_entrada(empleado_id, hora=None, observaciones=None):
        """Registra la entrada de un empleado"""
        # Verificar si ya existe un registro para hoy
        hoy = datetime.utcnow().date()
        asistencia = Asistencia.query.filter_by(empleado_id=empleado_id, fecha=hoy).first()
        
        if asistencia:
            # Ya existe un registro, verificar si tiene hora de entrada
            if asistencia.hora_entrada:
                return None, "Ya existe un registro de entrada para hoy"
        else:
            # Crear nuevo registro
            asistencia = Asistencia(empleado_id=empleado_id, fecha=hoy)
        
        # Registrar hora de entrada
        asistencia.hora_entrada = hora if hora else datetime.utcnow().time()
        asistencia.observaciones = observaciones
        
        return asistencia, "Entrada registrada correctamente"
    
    @staticmethod
    def registrar_salida(empleado_id, hora=None, observaciones=None):
        """Registra la salida de un empleado"""
        # Buscar registro de hoy
        hoy = datetime.utcnow().date()
        asistencia = Asistencia.query.filter_by(empleado_id=empleado_id, fecha=hoy).first()
        
        if not asistencia:
            return None, "No existe registro de entrada para hoy"
        
        if asistencia.hora_salida:
            return None, "Ya existe un registro de salida para hoy"
        
        # Registrar hora de salida
        asistencia.hora_salida = hora if hora else datetime.utcnow().time()
        
        # Agregar observaciones si existen
        if observaciones:
            asistencia.observaciones = (asistencia.observaciones or "") + "; " + observaciones
        
        # Calcular horas trabajadas y extras
        asistencia.calcular_horas()
        
        return asistencia, "Salida registrada correctamente"