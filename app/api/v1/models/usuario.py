from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nombre_completo = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(20), default='consulta')  # administrador, talento_humano, consulta
    email = db.Column(db.String(120), unique=True, nullable=False)
    estado = db.Column(db.Boolean, default=True)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    aprobaciones = db.relationship('Asistencia', backref='aprobador', lazy='dynamic', 
                                 foreign_keys='Asistencia.usuario_aprobacion')
    
    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre_usuario': self.nombre_usuario,
            'nombre_completo': self.nombre_completo,
            'rol': self.rol,
            'email': self.email,
            'estado': self.estado,
            'ultimo_acceso': self.ultimo_acceso.strftime('%Y-%m-%d %H:%M:%S') if self.ultimo_acceso else None
        }
    
    @staticmethod
    def create_usuario(nombre_usuario, password, nombre_completo, email, rol='consulta'):
        """Método para crear un nuevo usuario"""
        usuario = Usuario(
            nombre_usuario=nombre_usuario,
            nombre_completo=nombre_completo,
            email=email,
            rol=rol
        )
        usuario.set_password(password)
        return usuario