from flask import Blueprint, render_template
pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/admin/pedidos')
def admin_pedidos():
    # Simulación de pedidos (reemplaza con tu consulta real a la base de datos)
    pedidos = [
        {"producto": "Camisa", "talla": "M", "color": "Azul", "direccion": "Cra 10 #20-30"},
        {"producto": "Pantalón", "talla": "32", "color": "Negro", "direccion": "Av 5 #15-22"}
    ]
    return render_template('admin_pedidos.html', pedidos=pedidos)
