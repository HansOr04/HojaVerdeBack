Sistema de Automatización de Hojas de Asistencia - Florícola Hoja Verde
Backend API
Este repositorio contiene la API REST para el sistema de automatización de hojas de asistencia de Florícola Hoja Verde.
Tecnologías

Python
Flask
PostgreSQL
SQLAlchemy
JWT

Configuración Local

Clonar el repositorio
Crear un entorno virtual: python -m venv venv
Activar el entorno virtual:

Windows: .\venv\Scripts\Activate.ps1
Linux/MacOS: source venv/bin/activate


Instalar dependencias: pip install -r requirements.txt
Configurar variables de entorno en un archivo .env
Inicializar la base de datos:

flask db init
flask db migrate -m "Initial migration"
flask db upgrade


Ejecutar la aplicación: flask run

API Endpoints

/api/v1/empleados: Gestión de empleados
/api/v1/asistencias: Registro y gestión de asistencias
/api/v1/auth: Autenticación y gestión de usuarios
