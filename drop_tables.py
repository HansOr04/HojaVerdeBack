# drop_tables.py
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Usar el nuevo método de ejecución de consultas
    with db.engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS asistencias CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS empleados CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS usuarios CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        conn.commit()
    
    print("Todas las tablas han sido eliminadas correctamente.")