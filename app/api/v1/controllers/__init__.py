"""
Módulo de controladores para la aplicación.
Los controladores gestionan la interacción entre rutas y servicios,
y son responsables de sanitizar las entradas, manejar errores,
y formatear las respuestas.
"""

from app.api.v1.controllers.auth_controller import AuthController
from app.api.v1.controllers.empleado_controller import EmpleadoController
from app.api.v1.controllers.asistencia_controller import AsistenciaController

# Instancias de controladores para uso en la aplicación
auth_controller = AuthController()
empleado_controller = EmpleadoController()
asistencia_controller = AsistenciaController()