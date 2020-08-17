from functools import wraps
from flask import Flask, request, redirect, url_for, jsonify, render_template, session, flash
from flask_mail import Mail, Message
from flask_assets import Environment, Bundle
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from datetime import timedelta

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
app.config['MAIL_DEFAULT_SENDER'] = 'toms.teteris.personal@gmail.com' # enter your email here
app.config['MAIL_PASSWORD'] = 'Mafioziks007' # enter your password here


assets = Environment(app)
js = Bundle('base.js', filters='jsmin', output='interactive/packed.js')
assets.register('js_all', js)
icons = Bundle('bootstrap-icons.svg')
assets.register('icons', icons)
mail = Mail(app)

# models

db = SQLAlchemy(app)

class UserPermission(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    permission_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, user_id, permission_id):
        self.user_id = user_id
        self.permission_id = permission_id

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, permission_name):
        self.name = permission_name

    def find(permission_name):
        return self.query.filter_by(name=permission_name)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password = db.Column(db.String(256))
    email = db.Column(db.String(256))

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def hash_password(password):
        return sha256_crypt.encrypt(password)

    def is_same_password(self, password) -> bool:
        return sha256_crypt.verify(password, self.password)

    def have_permission(self, permission: Permission) -> bool:
        user_permissions = UserPermission.query.filter_by(user_id=self.id, permission_id=permission.id)

        if None is user_permissions:
            return False

        return True

db.drop_all()
db.create_all()

def seed_db():
    """
    Here should be seeded admin user and permissions
    """
    permission = Permission('manage_users')
    db.session.add(permission)

    user = User('Admin', 'User')
    user.email = 'tt007@inbox.lv'
    user.password = User.hash_password('Password123')
    db.session.add(user)

    db.session.commit()

    permission = Permission.query.filter_by(name='manage_users').first()
    user = User.query.filter_by(email='tt007@inbox.lv').first()

    # something wrong with data 
    db.session.add(UserPermission(user.id, permission.id))
    db.session.commit()

# app

user = None
permissions = set()

def setup_user():
    global user
    if is_authorized():
        user = User.query.filter_by(id=session['user']).first()

def setup_permissions():
    if not is_authorized():
        return
    
    global user
    user_permissions = UserPermission.query.filter_by(user_id=user.id).all()
    permission_ids   = set()

    for user_permission in user_permissions:
        permission_ids.add(user_permission.permission_id)

    global permissions
    filtered_permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()

    for filtered_permission in filtered_permissions:
        permissions.add(filtered_permission.name)

def setup_globals(r):
    @wraps(r)
    def global_setup(*args, **kwargs):
        setup_user()
        setup_permissions()

        return r(*args, **kwargs)
    return global_setup

def authorized(r):
    @wraps(r)
    def authorization_setup(*args, **kwargs):
        if not is_authorized():
            return redirect(url_for('login_form'))
        return r(*args, **kwargs)
    return authorization_setup

@app.errorhandler(404) 
def error_page(error):
    return render_template(f'errors/404.html')

@app.context_processor
def inject_user():
    global user
    global permissions
    return dict(user=user, permissions=permissions, is_authorized=is_authorized)

def is_authorized():
    if 'user' in session:
        return True
    return False

@app.route('/')
@setup_globals
def landing():
    return render_template('base.html')

@app.route('/user', methods = ['GET'])
@setup_globals
@authorized
def user_list():
    print("User is: ", user)
    return render_template('user/list.html', user_list=User.query.all(), authorized=is_authorized()) 

@app.route('/user/<id>', methods = ['DELETE', 'POST'])
@setup_globals
@authorized
def user_delete(id):
    if ('POST' == request.method and 'DELETE' != request.form['_method']):
        return redirect(url_for('error_page', 404), 404)
    
    user = User.query.filter_by(id=id).first()
    
    if None == user:
        flash('User not found!', 'error')
        return redirect(url_for('user_list'))

    User.query.filter_by(id=id).delete()
    db.session.commit()

    flash('User successfuly removed', 'success')
    return redirect(url_for('user_list'))

@app.route('/auth/register', methods = ['GET'])
def register_form():
    if is_authorized():
        return redirect(url_for('profile'))
    return render_template('auth/register.html')

@app.route('/auth/register', methods = ['POST'])
def register():
    if is_authorized():
        return redirect(url_for('profile'))

    user = User.query.filter_by(email=request.form['email']).first()

    if None is not user:
        flash('Email already used', 'danger')
        return redirect(url_for('register_form'))

    if (request.form['password'] != request.form['password_repeated']):
        flash('Password need to be same both times', 'danger')
        return redirect(url_for('register_form'))

    user = User(request.form['first_name'], request.form['last_name'])
    user.email = request.form['email']
    user.password = User.hash_password(request.form['password'])

    db.session.add(user)
    db.session.commit()

    mail_message = Message('Email validation on registration', recipients = [user.email])
    mail_message.body = 'This is email verification email at registration time!'
    mail.send(mail_message)

    session.permanent = True
    session['user']   = user.id
    return redirect(url_for('profile'))
    

@app.route('/auth/login', methods = ['GET'])
@setup_globals
def login_form():
    if is_authorized():
        return redirect(url_for('profile'))
    return render_template('auth/login.html')

@app.route('/auth/login', methods = ['POST'])
def auth_login():
    if is_authorized():
        return redirect(url_for('profile'))

    user = User.query.filter_by(email=request.form['email']).first()

    if (None == user or not user.is_same_password(request.form['password'])):
        flash('Wrong email or/and password', 'danger')
        return redirect(url_for('login_form'))

    session.permanent = True
    session['user']   = user.id

    return redirect(url_for('profile'))

@app.route('/auth/logout', methods = ['GET'])
@setup_globals
@authorized
def logout():
    if 'user' in session:
        session.pop('user', None)

    return redirect(url_for('landing'))

@app.route('/auth/change-password', methods = ['GET'])
@setup_globals
@authorized
def change_password_form():
    return render_template('auth/change_password.html')

@app.route('/auth/change-password', methods = ['POST'])
@setup_globals
@authorized
def save_password_change():
    if request.form['new-password'] != request.form['new-password-repeated']:
        flash('New password and repeated is not same', 'danger')
        return redirect(url_for('change_password_form'))

    user.password = User.hash_password(request.form['new-password'])
    db.session.add(user)
    db.session.commit()

    flash('Password successfuly changed', 'success')

    mail_message = Message('Password has been changed', recipients = [user.email])
    mail_message.body = 'Password has been changed'
    mail.send(mail_message)

    return redirect(url_for('profile'))

@app.route('/profile')
@setup_globals
@authorized
def profile():
    if 'user' not in session: 
        return redirect(url_for('login_form'))

    user = User.query.filter_by(id=session['user']).first()

    return render_template('user/profile.html', user=user, authorized=is_authorized())

if __name__ == '__main__':
    seed_db()
    app.run(debug=True)