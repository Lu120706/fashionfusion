from flask import Blueprint, render_template
from models import Pedido

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/admin/pedidos')
def admin_pedidos():
    pedidos = Pedido.query.all()
    return render_template('admin_pedidos.html', pedidos=pedidos)
