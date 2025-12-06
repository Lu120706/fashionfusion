from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    abort, current_app, Response
)
from werkzeug.utils import secure_filename
import datetime
import os
from extensions import db
from models import Producto
from decorators import role_required  # asumes que este decorador existe y usa session

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")

# -----------------------
# RUTAS ADMIN (CRUD)
# -----------------------

@productos_bp.route('/admin/productos')
@role_required(1)
def admin_products():
    productos = Producto.query.order_by(Producto.creado_en.desc()).all()
    return render_template('admin_products.html', productos=productos)


@productos_bp.route('/admin/productos/new', methods=['GET', 'POST'])
@role_required(1)
def admin_create_product():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        categoria = request.form.get('categoria', '').strip()
        talla = request.form.get('talla', '').strip()

        try:
            precio = float(request.form.get('precio_producto', 0))
        except ValueError:
            precio = 0.0

        disponibilidad = request.form.get('disponibilidad', 'SI')

        try:
            stock = int(request.form.get('stock', 0))
        except ValueError:
            stock = 0

        # FOTO — si el admin sube archivo, lo guardas en static/img
        foto_filename = None
        if 'foto_producto' in request.files:
            f = request.files['foto_producto']
            if f and f.filename:
                filename = secure_filename(f.filename)
                upload_path = os.path.join(current_app.static_folder, 'img')
                os.makedirs(upload_path, exist_ok=True)
                f.save(os.path.join(upload_path, filename))
                foto_filename = filename  # solo guardamos el nombre

        nuevo = Producto(
            nombre=nombre,
            descripcion=descripcion,
            categoria=categoria,
            talla=talla,
            precio_producto=precio,
            disponibilidad=disponibilidad,
            stock=stock,
            foto_producto=foto_filename
        )

        db.session.add(nuevo)
        try:
            db.session.commit()
            flash('Producto creado con éxito', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear producto: {e}', 'danger')

        return redirect(url_for('productos.admin_products'))

    return render_template('product_form.html', action='Crear', producto=None)


@productos_bp.route('/admin/productos/edit/<int:id_producto>', methods=['GET', 'POST'])
@role_required(1)
def admin_edit_product(id_producto):
    producto = Producto.query.get_or_404(id_producto)

    if request.method == 'POST':
        producto.nombre = request.form.get('nombre', producto.nombre).strip()
        producto.descripcion = request.form.get('descripcion', producto.descripcion).strip()
        producto.categoria = request.form.get('categoria', producto.categoria).strip()
        producto.talla = request.form.get('talla', producto.talla).strip()

        try:
            producto.precio_producto = float(request.form.get('precio_producto', producto.precio_producto))
        except:
            pass

        producto.disponibilidad = request.form.get('disponibilidad', producto.disponibilidad)

        try:
            producto.stock = int(request.form.get('stock', producto.stock))
        except:
            pass

        # Si suben nueva foto, reemplaza archivo
        if 'foto_producto' in request.files:
            f = request.files['foto_producto']
            if f and f.filename:
                filename = secure_filename(f.filename)
                ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                filename = f"{ts}_{filename}"
                upload_path = os.path.join(current_app.static_folder, 'img')
                os.makedirs(upload_path, exist_ok=True)
                f.save(os.path.join(upload_path, filename))
                producto.foto_producto = filename  

        try:
            db.session.commit()
            flash('Producto actualizado', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error actualizando producto: {e}', 'danger')

        return redirect(url_for('productos.admin_products'))

    return render_template('product_form.html', action='Editar', producto=producto)

@productos_bp.route('/admin/productos/delete/<int:id_producto>', methods=['POST'])
@role_required(1)
def admin_delete_product(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    db.session.delete(producto)
    try:
        db.session.commit()
        flash('Producto eliminado', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error eliminando: {e}', 'danger')
    return redirect(url_for('productos.admin_products'))


# ------------------------------------------------
# NUEVA RUTA PARA SERVIR IMÁGENES DESDE EL BLOB
# ------------------------------------------------
@productos_bp.route('/imagen/<int:pid>')
def imagen(pid):
    producto = Producto.query.get_or_404(pid)

    if producto.foto_producto is None:
        return "", 404

    # Si la imagen ES BLOB (bytes)
    if isinstance(producto.foto_producto, bytes):
        return Response(producto.foto_producto, mimetype="image/jpeg")

    # Si es ruta de archivo
    ruta = os.path.join(current_app.static_folder, producto.foto_producto)

    if os.path.isfile(ruta):
        with open(ruta, "rb") as f:
            return Response(f.read(), mimetype="image/jpeg")

    # Imagen por defecto
    default_path = os.path.join(current_app.static_folder, "no-image.png")
    with open(default_path, "rb") as f:
        return Response(f.read(), mimetype="image/png")
    
@productos_bp.route('/debug/imagenes')
def debug_imagenes():
    productos = Producto.query.all()
    html = "<h2>Listado de productos con imágenes</h2>"
    for p in productos:
        img_path = url_for('static', filename='img/' + p.foto_producto) if p.foto_producto else url_for('static', filename='img/no-image.png')
        html += f"""
        <div style='margin-bottom:20px;'>
            <strong>ID:</strong> {p.id_producto} <br>
            <strong>Nombre:</strong> {p.nombre} <br>
            <strong>Imagen:</strong><br>
            <img src='{img_path}' alt='{p.nombre}' style='max-width:200px; border:1px solid #ccc;'>
        </div>
        """
    return html

# -----------------------
# CATÁLOGO (CLIENTE)
# -----------------------

@productos_bp.route("/catalogo")
def catalogo():
    productos = Producto.query.all()
    return render_template("catalogo.html", products=productos)


@productos_bp.route("/<int:pid>")
def detalle(pid):
    product = Producto.query.get_or_404(pid)
    return render_template("productos.html", product=product)
