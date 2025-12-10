from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Pedido, db

pedidos_bp = Blueprint('pedidos', __name__)

# Vista principal de pedidos
@pedidos_bp.route('/admin/pedidos')
def admin_pedidos():
    pedidos = Pedido.query.all()
    return render_template('admin_pedidos.html', pedidos=pedidos)

# Cambiar estado de un pedido
@pedidos_bp.route('/admin/pedidos/estado/<int:pedido_id>', methods=['POST'])
def cambiar_estado_pedido(pedido_id):
    nuevo_estado = request.form.get('estado')
    pedido = Pedido.query.get_or_404(pedido_id)

    if nuevo_estado in ['pendiente', 'finalizado']:
        pedido.estado = nuevo_estado
        db.session.commit()
        flash(f"Estado del pedido actualizado a {nuevo_estado}.", "success")
    else:
        flash("Estado inválido.", "warning")

    return redirect(url_for('pedidos.admin_pedidos'))

# Eliminar un pedido individual
@pedidos_bp.route('/admin/pedidos/eliminar/<int:pedido_id>', methods=['POST'])
def eliminar_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    db.session.delete(pedido)
    db.session.commit()
    flash("Pedido eliminado correctamente.", "success")
    return redirect(url_for('pedidos.admin_pedidos'))

# Eliminar todos los pedidos
@pedidos_bp.route('/admin/pedidos/eliminar_todos', methods=['POST'])
def eliminar_todos_pedidos():
    try:
        db.session.query(Pedido).delete()
        db.session.commit()
        flash("Todos los pedidos fueron eliminados correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error al eliminar los pedidos: " + str(e), "danger")
    return redirect(url_for('pedidos.admin_pedidos'))
