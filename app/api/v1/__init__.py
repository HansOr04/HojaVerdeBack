from flask import Blueprint

# Crear Blueprint principal para API v1
bp = Blueprint('api_v1', __name__)

# Importar las rutas (debe ir después de crear el Blueprint para evitar referencias circulares)
from app.api.v1.routes import usuarios, empleados, asistencias

# Ruta base para verificar el estado de la API
@bp.route('/status', methods=['GET'])
def status():
    return {'status': 'ok', 'version': 'v1', 'message': 'API de Sistema de Asistencia Hoja Verde funcionando correctamente'}