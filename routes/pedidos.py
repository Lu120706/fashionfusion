from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Pedido, db

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/admin/pedidos')
def admin_pedidos():
    pedidos = Pedido.query.all()
    return render_template('admin_pedidos.html', pedidos=pedidos)

@pedidos_bp.route('/admin/pedidos/estado/<int:pedido_id>', methods=['POST'])
def cambiar_estado_pedido(pedido_id):
    """Permite cambiar el estado de un pedido desde el panel admin."""
    nuevo_estado = request.form.get('estado')
    pedido = Pedido.query.get_or_404(pedido_id)

    if nuevo_estado in ['pendiente', 'finalizado']:
        pedido.estado = nuevo_estado
        db.session.commit()
        flash(f"Estado del pedido actualizado a {nuevo_estado}.", "success")
    else:
        flash("Estado inválido.", "warning")

    return redirect(url_for('pedidos.admin_pedidos'))
