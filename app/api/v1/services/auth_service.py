from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from app import db
from app.api.v1.models.usuario import Usuario
from app.api.v1.schemas import validate_data, usuario_schema, usuario_login_schema

class AuthService:
    """Servicio para gestionar la autenticación y usuarios"""
    
    def register(self, user_data):
        """
        Registra un nuevo usuario en el sistema
        
        Args:
            user_data (dict): Datos del usuario a registrar
            
        Returns:
            tuple: (usuario, None) si el registro es exitoso, (None, error) si hay error
        """
        # Validar datos de entrada
        validated_data, errors = validate_data(usuario_schema, user_data)
        if errors:
            return None, errors
            
        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(nombre_usuario=validated_data['nombre_usuario']).first():
            return None, {'nombre_usuario': ['Este nombre de usuario ya está en uso']}
            
        if Usuario.query.filter_by(email=validated_data['email']).first():
            return None, {'email': ['Este email ya está registrado']}
            
        # Crear el nuevo usuario
        password = validated_data.pop('password')
        nuevo_usuario = Usuario(**validated_data)
        nuevo_usuario.set_password(password)
        
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            return nuevo_usuario, None
        except Exception as e:
            db.session.rollback()
            return None, {'database': [str(e)]}
    
    def login(self, credentials):
        """
        Autentica un usuario y genera un token JWT
        
        Args:
            credentials (dict): Credenciales de login (nombre_usuario, password)
            
        Returns:
            tuple: (token_data, None) si login exitoso, (None, error) si falla
        """
        # Validar datos de entrada
        validated_data, errors = validate_data(usuario_login_schema, credentials)
        if errors:
            return None, errors
            
        # Buscar usuario por nombre de usuario
        usuario = Usuario.query.filter_by(nombre_usuario=validated_data['nombre_usuario']).first()
        if not usuario or not usuario.check_password(validated_data['password']):
            return None, {'auth': ['Credenciales inválidas']}
            
        if not usuario.estado:
            return None, {'auth': ['Usuario inactivo']}
            
        # Actualizar último acceso
        usuario.ultimo_acceso = datetime.utcnow()
        db.session.commit()
        
        # Generar token JWT
        access_token = create_access_token(
            identity=usuario.id,
            additional_claims={
                'rol': usuario.rol,
                'nombre': usuario.nombre_completo
            }
        )
        
        return {
            'access_token': access_token,
            'usuario': usuario_schema.dump(usuario)
        }, None
            
    def get_usuario_by_id(self, usuario_id):
        """Obtiene un usuario por su ID"""
        return Usuario.query.get(usuario_id)
    
    def get_all_usuarios(self, page=1, per_page=20, **filters):
        """
        Obtiene todos los usuarios con paginación y filtros
        
        Args:
            page (int): Número de página
            per_page (int): Elementos por página
            **filters: Filtros adicionales
            
        Returns:
            tuple: (pagination_obj, total)
        """
        query = Usuario.query
        
        # Aplicar filtros
        if 'rol' in filters and filters['rol']:
            query = query.filter(Usuario.rol == filters['rol'])
            
        if 'estado' in filters:
            if filters['estado'] == 'true':
                query = query.filter(Usuario.estado == True)
            elif filters['estado'] == 'false':
                query = query.filter(Usuario.estado == False)
        
        if 'busqueda' in filters and filters['busqueda']:
            search_term = f"%{filters['busqueda']}%"
            query = query.filter(
                (Usuario.nombre_usuario.ilike(search_term)) |
                (Usuario.nombre_completo.ilike(search_term)) |
                (Usuario.email.ilike(search_term))
            )
            
        # Ejecutar consulta con paginación
        pagination = query.order_by(Usuario.nombre_usuario).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return pagination.items, pagination.total
    
    def update_usuario(self, usuario_id, user_data):
        """
        Actualiza información de un usuario
        
        Args:
            usuario_id (int): ID del usuario a actualizar
            user_data (dict): Datos a actualizar
            
        Returns:
            tuple: (usuario, None) si la actualización es exitosa, (None, error) si hay error
        """
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return None, {'usuario': ['Usuario no encontrado']}
            
        # Si se proporciona un nuevo email, verificar que no esté en uso
        if 'email' in user_data and user_data['email'] != usuario.email:
            if Usuario.query.filter_by(email=user_data['email']).first():
                return None, {'email': ['Este email ya está registrado']}
        
        # Actualizar password si se proporciona
        if 'password' in user_data and user_data['password']:
            usuario.set_password(user_data['password'])
            user_data.pop('password')
            
        # Actualizar otros campos
        for key, value in user_data.items():
            if hasattr(usuario, key):
                setattr(usuario, key, value)
                
        try:
            db.session.commit()
            return usuario, None
        except Exception as e:
            db.session.rollback()
            return None, {'database': [str(e)]}
    
    def delete_usuario(self, usuario_id):
        """
        Elimina un usuario (estableciendo estado=False)
        
        Args:
            usuario_id (int): ID del usuario a eliminar
            
        Returns:
            bool: True si la eliminación es exitosa, False si hay error
        """
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return False
            
        usuario.estado = False
        
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False