from flask import Flask, request, redirect, url_for, jsonify, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'backend_ap1_k3y'
app.permanent_session_lifetime = timedelta(hours=3)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# models

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password = db.Column(db.String(256))
    email = db.Column(db.String(256))

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

class UserPermission(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    pemrission_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, user_id, permission_id):
        self.user_id = user_id
        self.pemrission_id = permission_id

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, permission_name):
        self.name = permission_name

db.create_all()

def seed_db():
    """
    Here should be seeded admin user and permissions
    """

# app

def is_authorized():
    if 'user' in session:
        return True
    return False

@app.errorhandler(404) 
def error_page(error):
    return render_template(f'errors/404.html')

@app.route('/')
def main():
    return 'Main page'

@app.route('/user', methods = ['GET'])
def user_list():
    return render_template('user/list.html', user_list=User.query.all(), authorized=is_authorized()) 

@app.route('/user/<id>', methods = ['DELETE', 'POST'])
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
    return render_template('auth/register.html')

@app.route('/auth/register', methods = ['POST'])
def register():
    if (request.form['password'] != request.form['password_repeated']):
        return redirect(url_for('register_form'))

    user = User(request.form['first_name'], request.form['last_name'])
    user.email = request.form['email']
    user.password = sha256_crypt.encrypt(request.form['password'])

    db.session.add(user)
    db.session.commit()

    session.permanent = True
    session['user']   = user.id
    return redirect(url_for('profile'))
    # logged_user = User.query.filter_by(email=user.email, password=sha256_crypt.encrypt(request.form['email'])).first()
    # if None == logged_user:
    #     return redirect(url_for('register_form'))

    

@app.route('/auth/login', methods = ['GET'])
def login_form():
    return render_template('auth/login.html')

@app.route('/auth/login', methods = ['POST'])
def auth_login():
    user = User.query.filter_by(email=request.form['email'], password=sha256_crypt.encrypt(request.form['password'])).first()

    if None == user:
        return redirect(url_for('login_form'))


    session.permanent = True
    session['user']   = user.id

    return redirect(url_for('profile'))

@app.route('/auth/logout', methods = ['GET'])
def logout():
    if 'user' in session:
        session.pop('user', None)

    return redirect(url_for('main'))

@app.route('/profile')
def profile():
    if 'user' not in session: 
        return redirect(url_for('login_form'))

    user = User.query.filter_by(id=session['user']).first()

    return render_template('user/profile.html', user=user, authorized=is_authorized())

if __name__ == '__main__':
    seed_db()
    app.run(debug=True)