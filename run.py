import os
from app import create_app
from flask_migrate import Migrate, upgrade
from app.api.v1.models.usuario import Usuario
from app import db

# Crear la aplicación usando la configuración predeterminada
app = create_app()

# Configurar migración
migrate = Migrate(app, db)

@app.cli.command("init-db")
def init_db():
    """Inicializa la base de datos y crea un usuario administrador si no existe."""
    with app.app_context():
        # Ejecutar migraciones
        # Nota: esto solo funcionará si ya has creado las migraciones con 'flask db init', 'flask db migrate'
        upgrade()
        
        # Verificar si existe un usuario administrador
        admin_user = Usuario.query.filter_by(nombre_usuario='admin').first()
        
        if not admin_user:
            # Crear usuario administrador predeterminado
            admin = Usuario(
                nombre_usuario='admin',
                nombre_completo='Administrador',
                email='admin@hojaverde.com',
                rol='administrador',
                estado=True
            )
            # Establecer contraseña desde variable de entorno o usar valor predeterminado
            admin_password = os.environ.get('ADMIN_PASSWORD', 'hojaverde2025')
            admin.set_password(admin_password)
            
            db.session.add(admin)
            db.session.commit()
            print(f"Usuario administrador creado con éxito. Usuario: admin, Contraseña: {admin_password}")
        else:
            print("El usuario administrador ya existe.")

@app.cli.command("create-demo-data")
def create_demo_data():
    """Crea datos de demostración para pruebas."""
    from datetime import datetime, date, time, timedelta
    from app.api.v1.models.empleado import Empleado
    from app.api.v1.models.asistencia import Asistencia
    
    with app.app_context():
        # Verificar si ya existen datos de demostración
        if Empleado.query.count() > 1:
            print("Ya existen datos de demostración.")
            return
            
        # Crear algunos empleados de demostración
        empleados = [
            {
                'cedula': '1721234567',
                'nombres': 'Juan Carlos',
                'apellidos': 'Rodríguez Pérez',
                'area': 'Producción',
                'cargo': 'Supervisor',
                'fecha_ingreso': date(2020, 1, 15),
                'unidad_productiva': 'JOYGARDENS'
            },
            {
                'cedula': '1757654321',
                'nombres': 'María Fernanda',
                'apellidos': 'López Gómez',
                'area': 'Administración',
                'cargo': 'Asistente',
                'fecha_ingreso': date(2021, 3, 10),
                'unidad_productiva': 'JOYGARDENS'
            },
            {
                'cedula': '1768901234',
                'nombres': 'Pedro José',
                'apellidos': 'Suárez Torres',
                'area': 'Producción',
                'cargo': 'Operario',
                'fecha_ingreso': date(2022, 5, 5),
                'unidad_productiva': 'JOYGARDENS'
            }
        ]
        
        # Insertar empleados
        for emp_data in empleados:
            empleado = Empleado(**emp_data)
            db.session.add(empleado)
        
        db.session.commit()
        print("Empleados de demostración creados con éxito.")
        
        # Crear asistencias de demostración para la última semana
        empleados_db = Empleado.query.all()
        hoy = date.today()
        
        # Registrar asistencias para los últimos 5 días
        for i in range(5):
            dia = hoy - timedelta(days=i)
            
            # Saltarse fines de semana
            if dia.weekday() >= 5:  # 5=sábado, 6=domingo
                continue
                
            for empleado in empleados_db:
                # Crear registro de asistencia
                asistencia = Asistencia(
                    empleado_id=empleado.id,
                    fecha=dia,
                    hora_entrada=time(8, 0),
                    hora_salida=time(14, 30),
                    observaciones="Registro de demostración",
                    estado="Aprobado"
                )
                
                # Calcular horas trabajadas y extras
                asistencia.calcular_horas()
                
                db.session.add(asistencia)
        
        db.session.commit()
        print("Asistencias de demostración creadas con éxito.")

if __name__ == '__main__':
    # El puerto se configura a través de la variable de entorno PORT si está disponible (útil para Heroku/Render)
    # De lo contrario, usa el puerto predeterminado 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)