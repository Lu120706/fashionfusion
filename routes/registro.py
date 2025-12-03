# routes/registro.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import Usuario, Rol
from decorators import find_or_create_role
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

# Blueprint de registro/autenticación
registro_bp = Blueprint('registro', __name__, url_prefix='/registro')

# -----------------------
# REGISTRO DE USUARIO
# -----------------------
@registro_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id_usuario = request.form['id_usuario'].strip()
        nombre = request.form['nombre'].strip()
        correo = request.form['correo'].strip()
        password = request.form['password']
        confirm = request.form['confirm_password']
        direccion = request.form.get('direccion', '').strip()

        # Validaciones básicas
        if password != confirm:
            flash('⚠️ Las contraseñas no coinciden', 'danger')
            return render_template('register.html')

        if Usuario.query.filter_by(id_usuario=id_usuario).first():
            flash('⚠️ El ID de usuario ya está registrado', 'danger')
            return render_template('register.html')

        if correo and Usuario.query.filter_by(correo=correo).first():
            flash('⚠️ El correo ya está registrado', 'danger')
            return render_template('register.html')

        # Crear o buscar rol 'user'
        rol_user = find_or_create_role(db, Rol, 'user')
        if not rol_user:
            flash('❌ Error creando rol de usuario', 'danger')
            return render_template('register.html')

        # Crear usuario
        nuevo_usuario = Usuario(
            id_usuario=id_usuario,
            nombre=nombre,
            correo=correo,
            direccion=direccion,
            id_rol=rol_user.id_rol
        )
        nuevo_usuario.set_password(password)  # guarda hash en usuario.contrasena

        db.session.add(nuevo_usuario)
        try:
            db.session.commit()
            flash('✅ Registro exitoso. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('registro.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al guardar el usuario: {e}', 'danger')
            return render_template('register.html')

    return render_template('register.html')


# -----------------------
# LOGIN DE USUARIO
# -----------------------
@registro_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id_usuario = request.form['id_usuario'].strip()
        contrasena = request.form['contrasena']

        usuario = Usuario.query.filter_by(id_usuario=id_usuario).first()

        if usuario and check_password_hash(usuario.contrasena, contrasena):
            login_user(usuario)

            # Guardar datos en sesión
            session["role"] = usuario.id_rol
            session["user_id"] = usuario.id_usuario

            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('home.index'))
        else:
            flash("Usuario o contraseña incorrectos", "danger")

    return render_template('login.html')


# -----------------------
# LOGOUT DE USUARIO
# -----------------------
@registro_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for('home.index'))


# -----------------------
# RECUPERAR CONTRASEÑA
# -----------------------
@registro_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        correo = request.form['correo'].strip()
        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario:
            # ⚠️ Aquí deberías enviar un correo con un token seguro
            # Por simplicidad, redirigimos a reset_password con el id_usuario
            flash("📧 Ingresa tu nueva contraseña.", "info")
            return redirect(url_for('registro.reset_password', user_id=usuario.id_usuario))
        else:
            flash("⚠️ No existe un usuario con ese correo.", "danger")

    return render_template('forgot_password.html')


# -----------------------
# RESTABLECER CONTRASEÑA
# -----------------------
@registro_bp.route('/reset_password/<user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    usuario = Usuario.query.filter_by(id_usuario=user_id).first()
    if not usuario:
        flash("❌ Usuario no encontrado.", "danger")
        return redirect(url_for('registro.forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash("⚠️ Las contraseñas no coinciden.", "danger")
            return render_template('reset_password.html')

        usuario.contrasena = generate_password_hash(password)
        db.session.commit()
        flash("✅ Contraseña actualizada correctamente. Ya puedes iniciar sesión.", "success")
        return redirect(url_for('registro.login'))

    return render_template('reset_password.html')
