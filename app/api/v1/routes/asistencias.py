from flask import jsonify, request
from app.api.v1 import bp
from app.api.v1.models.asistencia import Asistencia
from app import db
@bp.route('/asistencias', methods=['GET'])
def get_asistencias():
asistencias = Asistencia.query.all()
return jsonify([asistencia.to_dict() for asistencia in asistencias]), 200
@bp.route('/asistencias/int:id', methods=['GET'])
def get_asistencia(id):
asistencia = Asistencia.query.get_or_404(id)
return jsonify(asistencia.to_dict()), 200
