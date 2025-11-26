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
from flask import session

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
        return Usuario.query.get(user_id)

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
    
@app.route('/debug/session')
def debug_session():
    return str(session)

@app.route('/debug/env')
def debug_env():
    import os
    return {
        "SECRET_KEY": os.environ.get("SECRET_KEY"),
        "MAIL_USERNAME": os.environ.get("MAIL_USERNAME"),
        "MAIL_PASSWORD": os.environ.get("MAIL_PASSWORD"),
        "DATABASE_URL": os.environ.get("DATABASE_URL")
    }

@app.route('/debug/users')
def debug_users():
    from models import Usuario
    users = Usuario.query.all()
    return {
        "usuarios": [
            {
                "id_usuario": u.id_usuario,
                "nombre": u.nombre,
                "id_rol": int(u.id_rol)
            } for u in users
        ]
    }

# Ejecutar servidor
if __name__ == "__main__":
    app.run(debug=True)

with app.app_context():
    db.create_all()