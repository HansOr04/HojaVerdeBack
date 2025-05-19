from flask import jsonify, request
from app.api.v1 import bp
from app.api.v1.models.empleado import Empleado
from app import db
@bp.route('/empleados', methods=['GET'])
def get_empleados():
empleados = Empleado.query.all()
return jsonify([empleado.to_dict() for empleado in empleados]), 200
@bp.route('/empleados/int:id', methods=['GET'])
def get_empleado(id):
empleado = Empleado.query.get_or_404(id)
return jsonify(empleado.to_dict()), 200
