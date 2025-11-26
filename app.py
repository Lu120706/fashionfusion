# app.py
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager, mail
from models import Usuario, Rol
from routes import (
    contraseña_bp,
    factura_bp,
    productos_bp,
    registro_bp,
    rol_bp,
    usuarios_bp,
    carrito_bp,
    home_bp
)
from globals import SHOPPING_CARTS


def create_app():
    # Crear la aplicación Flask con las carpetas correctas
    app = Flask(__name__, static_folder='style', template_folder='templates')

    # Cargar configuración
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Configurar Flask-Login
    login_manager.login_view = 'registro.login'  # Nombre del blueprint y la función de login
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar Blueprints
    app.register_blueprint(contraseña_bp)
    app.register_blueprint(factura_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(registro_bp)
    app.register_blueprint(rol_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(home_bp)

    # Crear las tablas si no existen
    with app.app_context():
        db.create_all()

    return app


# Crear instancia de la aplicación
app = create_app()


# Ruta raíz (por si el blueprint de home no la maneja)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-admin')
def create_admin():
    from models import Usuario, Rol, db

    # Verificar si ya existe el rol "admin"
    admin_role = Rol.query.filter_by(nombre='admin').first()
    if not admin_role:
        admin_role = Rol(nombre='admin')
        db.session.add(admin_role)
        db.session.commit()

    # Verificar si ya existe el usuario admin
    admin_user = Usuario.query.filter_by(correo='admin@fashionfusion.com').first()
    if not admin_user:
        admin_user = Usuario(
            id_usuario='admin01',
            nombre='Administrador',
            correo='admin@fashionfusion.com',
            direccion='Oficina Central',
            id_rol=admin_role.id_rol
        )
        admin_user.set_password('admin123')  # 🔑 Contraseña inicial
        db.session.add(admin_user)
        db.session.commit()
        return "Usuario administrador creado 🎉"
    else:
        return "El usuario administrador ya existe ✅"

# Ejecutar servidor
if __name__ == "__main__":
    app.run(debug=True)

