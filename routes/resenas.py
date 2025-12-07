from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app import db
from models import Resena

resenas_bp = Blueprint('resenas', __name__)

@resenas_bp.route('/guardar', methods=['POST'])
@login_required
def guardar_resena():
    id_producto = request.form.get('id_producto')
    calidad = request.form.get('calidad')
    comodidad = request.form.get('comodidad')
    comentario = request.form.get('comentario')
    foto = request.files.get('foto')

    nombre_archivo = None
    if foto and foto.filename != '':
        nombre_archivo = secure_filename(foto.filename)
        foto.save(os.path.join('static/img/resenas', nombre_archivo))

    nueva_resena = Resena(
        id_producto=id_producto,
        calidad=calidad,
        comodidad=comodidad,
        comentario=comentario,
        foto=nombre_archivo,
        usuario=current_user.nombre,
        fecha=datetime.utcnow()
    )
    db.session.add(nueva_resena)
    db.session.commit()

    return redirect(url_for('productos.detalle_producto', id_producto=id_producto))
