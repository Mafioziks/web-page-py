from functools import wraps
from flask import Flask, request, redirect, url_for, jsonify, render_template, session, flash, g
from flask_mail import Mail, Message
from flask_assets import Environment, Bundle
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from datetime import timedelta
from app_wrappers import authorized, setup_globals, is_authorized
from models import User, UserPermission, Permission, db as app_db
from auth import authorization_blueprint
from admin import admin_blueprint  # this maybe remove
from permission import permission_blueprint


def create_app():
    global app
    app = None
    app = Flask(__name__)
    app.secret_key = 'backend_ap1_k3y'
    app.permanent_session_lifetime = timedelta(hours=3)

    # database configs
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # mail configs
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'toms.teteris.personal@gmail.com'  # enter your email here
    app.config['MAIL_DEFAULT_SENDER'] = 'toms.teteris.personal@gmail.com'  # enter your email here
    app.config['MAIL_PASSWORD'] = '-------'  # enter your password here

    assets = Environment(app)
    js = Bundle('base.js', filters='jsmin', output='interactive/packed.js')
    assets.register('js_all', js)
    icons = Bundle('bootstrap-icons.svg')
    assets.register('icons', icons)
    mail = Mail(app)

    # Blueprints
    app.register_blueprint(authorization_blueprint, url_prefix='/auth')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(permission_blueprint, url_prefix='/permission')

    # models
    app_db.init_app(app)
    with app.app_context():
        app_db.drop_all()
        app_db.create_all()
        seed_db(app_db)
    add_main_routes(app, app_db)

    return app


def seed_db(db):
    """
    Here should be seeded admin user and permissions
    """
    permission = Permission('manage_users')
    permission.description = 'Can manage users'
    db.session.add(permission)

    global user
    user = User('Admin', 'User')
    user.email = 'tt007@inbox.lv'
    user.password = User.hash_password('Password123')
    db.session.add(user)

    db.session.commit()

    permission = Permission.query.filter_by(name='manage_users').first()
    user = User.query.filter_by(email='tt007@inbox.lv').first()

    db.session.add(UserPermission(user.id, permission.id))
    db.session.commit()


# app

user = None
permissions = set()


def add_main_routes(app, db):
    @app.errorhandler(404)
    def error_page(error):
        return render_template(f'errors/404.html')

    @app.context_processor
    def inject_user():
        global user
        user = g.get('user', None)
        permission = g.get('permissions', set())
        return dict(user=user, permissions=permissions, is_authorized=is_authorized)

    @app.route('/')
    @setup_globals
    def landing():
        return render_template('base.html')

    @app.route('/user', methods=['GET'])
    @setup_globals
    @authorized
    def user_list():
        return render_template('user/list.html', user_list=User.query.all(), authorized=is_authorized())

    @app.route('/user/<id>', methods=['DELETE', 'POST'])
    @setup_globals
    @authorized
    def user_delete(id):
        if 'POST' == request.method and 'DELETE' != request.form['_method']:
            return redirect(url_for('error_page', 404), 404)

        permissions = g.get('permissions')

        if 'manage_users' not in permissions:
            return redirect(url_for('error_page', 403), 403)

        user = User.query.filter_by(id=id).first()

        if None == user:
            flash('User not found!', 'error')
            return redirect(url_for('user_list'))

        User.query.filter_by(id=id).delete()
        db.session.commit()

        flash('User successfuly removed', 'success')
        return redirect(url_for('user_list'))

    @app.route('/profile')
    @setup_globals
    @authorized
    def profile():
        if 'user' not in session:
            return redirect(url_for('login_form'))

        user = User.query.filter_by(id=session['user']).first()

        return render_template('user/profile.html', user=user, authorized=is_authorized())


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
