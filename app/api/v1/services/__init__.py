"""
Módulo de servicios para la aplicación.
Los servicios implementan la lógica de negocio y sirven como capa intermedia 
entre los controladores y los modelos.
"""

from app.api.v1.services.auth_service import AuthService
from app.api.v1.services.asistencia_service import AsistenciaService
from app.api.v1.services.empleado_service import EmpleadoService

# Instancias de servicios para uso en la aplicación
auth_service = AuthService()
asistencia_service = AsistenciaService()
empleado_service = EmpleadoService()