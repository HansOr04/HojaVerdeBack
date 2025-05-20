from marshmallow import Schema, fields, validate, ValidationError, post_load

# Esquema base para respuestas genéricas
class ResponseSchema(Schema):
    message = fields.Str(required=True)
    status = fields.Str(required=True)

# Esquemas para Usuario
class UsuarioSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre_usuario = fields.Str(required=True, validate=validate.Length(min=3, max=64))
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8, max=128))
    nombre_completo = fields.Str(required=True, validate=validate.Length(min=3, max=128))
    rol = fields.Str(validate=validate.OneOf(['administrador', 'talento_humano', 'consulta']))
    email = fields.Email(required=True)
    estado = fields.Bool()
    ultimo_acceso = fields.DateTime(dump_only=True)
    
    @post_load
    def set_defaults(self, data, **kwargs):
        """Establecer valores predeterminados después de la carga"""
        if 'rol' not in data:
            data['rol'] = 'consulta'
        if 'estado' not in data:
            data['estado'] = True
        return data

class UsuarioLoginSchema(Schema):
    nombre_usuario = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class UsuarioUpdateSchema(Schema):
    nombre_completo = fields.Str(validate=validate.Length(min=3, max=128))
    email = fields.Email()
    rol = fields.Str(validate=validate.OneOf(['administrador', 'talento_humano', 'consulta']))
    estado = fields.Bool()
    password = fields.Str(load_only=True, validate=validate.Length(min=8, max=128))

# Esquemas para Empleado
class EmpleadoSchema(Schema):
    id = fields.Int(dump_only=True)
    cedula = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    nombres = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    apellidos = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    nombre_completo = fields.Str(dump_only=True)
    area = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    cargo = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    fecha_ingreso = fields.Date()
    estado = fields.Bool()
    unidad_productiva = fields.Str()
    
    @post_load
    def set_defaults(self, data, **kwargs):
        """Establecer valores predeterminados después de la carga"""
        if 'estado' not in data:
            data['estado'] = True
        if 'unidad_productiva' not in data:
            data['unidad_productiva'] = 'JOYGARDENS'
        return data

class EmpleadoUpdateSchema(Schema):
    cedula = fields.Str(validate=validate.Length(min=10, max=20))
    nombres = fields.Str(validate=validate.Length(min=2, max=100))
    apellidos = fields.Str(validate=validate.Length(min=2, max=100))
    area = fields.Str(validate=validate.Length(min=2, max=100))
    cargo = fields.Str(validate=validate.Length(min=2, max=100))
    fecha_ingreso = fields.Date()
    estado = fields.Bool()
    unidad_productiva = fields.Str()

# Esquemas para Asistencia
class AsistenciaSchema(Schema):
    id = fields.Int(dump_only=True)
    empleado_id = fields.Int(required=True)
    fecha = fields.Date()
    hora_entrada = fields.Time()
    hora_salida = fields.Time()
    horas_trabajadas = fields.Float(dump_only=True)
    horas_extras = fields.Float(dump_only=True)
    observaciones = fields.Str()
    estado = fields.Str(validate=validate.OneOf(['Pendiente', 'Aprobado', 'Rechazado']))
    usuario_aprobacion = fields.Int()
    fecha_aprobacion = fields.DateTime()
    
    @post_load
    def set_defaults(self, data, **kwargs):
        """Establecer valores predeterminados después de la carga"""
        from datetime import date
        if 'fecha' not in data:
            data['fecha'] = date.today()
        if 'estado' not in data:
            data['estado'] = 'Pendiente'
        return data

class AsistenciaRegistroSchema(Schema):
    empleado_id = fields.Int(required=True)
    tipo_registro = fields.Str(required=True, validate=validate.OneOf(['entrada', 'salida']))
    observaciones = fields.Str()

class AsistenciaAprobacionSchema(Schema):
    estado = fields.Str(required=True, validate=validate.OneOf(['Aprobado', 'Rechazado']))
    observaciones = fields.Str()

# Esquemas para filtros y paginación
class PaginationSchema(Schema):
    page = fields.Int()
    per_page = fields.Int()
    total = fields.Int(dump_only=True)
    total_pages = fields.Int(dump_only=True)
    
    @post_load
    def set_defaults(self, data, **kwargs):
        """Establecer valores predeterminados después de la carga"""
        if 'page' not in data:
            data['page'] = 1
        if 'per_page' not in data:
            data['per_page'] = 20
        return data

class EmpleadoFilterSchema(PaginationSchema):
    area = fields.Str()
    estado = fields.Bool()
    unidad_productiva = fields.Str()
    busqueda = fields.Str()  # Para búsqueda por nombre o cédula

class AsistenciaFilterSchema(PaginationSchema):
    empleado_id = fields.Int()
    fecha_inicio = fields.Date()
    fecha_fin = fields.Date()
    estado = fields.Str(validate=validate.OneOf(['Pendiente', 'Aprobado', 'Rechazado']))
    unidad_productiva = fields.Str()
    area = fields.Str()

# Instancias de esquemas comúnmente utilizados
usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)
usuario_login_schema = UsuarioLoginSchema()
usuario_update_schema = UsuarioUpdateSchema()

empleado_schema = EmpleadoSchema()
empleados_schema = EmpleadoSchema(many=True)
empleado_update_schema = EmpleadoUpdateSchema()

asistencia_schema = AsistenciaSchema()
asistencias_schema = AsistenciaSchema(many=True)
asistencia_registro_schema = AsistenciaRegistroSchema()
asistencia_aprobacion_schema = AsistenciaAprobacionSchema()

# Función para validar datos según esquema
def validate_data(schema, data, partial=False):
    """
    Valida datos usando un esquema Marshmallow.
    Retorna (datos_validados, None) si la validación es exitosa,
    o (None, errores) si hay errores de validación.
    """
    try:
        validated_data = schema.load(data, partial=partial)
        return validated_data, None
    except ValidationError as err:
        return None, err.messages