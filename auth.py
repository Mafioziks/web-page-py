from flask import Blueprint, render_template, redirect, url_for, flash, session, request, g
from wrappers import setup_globals, authorized, is_authorized
from models import User, db
from flask_mail import Mail, Message

authorization_blueprint = Blueprint('auth', __name__, template_folder='templates/auth')

@authorization_blueprint.route('/register', methods = ['GET'])
def register_form():
    if is_authorized():
        return redirect(url_for('profile'))
    return render_template('auth/register.html')

@authorization_blueprint.route('/register', methods = ['POST'])
def register():
    if is_authorized():
        return redirect(url_for('profile'))

    user = User.query.filter_by(email=request.form['email']).first()

    if None is not user:
        flash('Email already used', 'danger')
        return redirect(url_for('auth.register_form'))

    if (request.form['password'] != request.form['password_repeated']):
        flash('Password need to be same both times', 'danger')
        return redirect(url_for('auth.register_form'))

    user = User(request.form['first_name'], request.form['last_name'])
    user.email = request.form['email']
    user.password = User.hash_password(request.form['password'])

    db.session.add(user)
    db.session.commit()

    # mail_message = Message('Email validation on registration', recipients = [user.email])
    # mail_message.body = 'This is email verification email at registration time!'
    # mail.send(mail_message)

    session.permanent = True
    session['user']   = user.id
    return redirect(url_for('profile'))
    

@authorization_blueprint.route('/login', methods = ['GET'])
@setup_globals
def login_form():
    if is_authorized():
        return redirect(url_for('profile'))
    return render_template('auth/login.html')

@authorization_blueprint.route('/login', methods = ['POST'])
def auth_login():
    if is_authorized():
        return redirect(url_for('profile'))

    user = User.query.filter_by(email=request.form['email']).first()

    if (None == user or not user.is_same_password(request.form['password'])):
        flash('Wrong email or/and password', 'danger')
        return redirect(url_for('auth.login_form'))

    session.permanent = True
    session['user']   = user.id

    return redirect(url_for('profile'))

@authorization_blueprint.route('/logout', methods = ['GET'])
@setup_globals
@authorized
def logout():
    if 'user' in session:
        session.pop('user', None)

    return redirect(url_for('landing'))

@authorization_blueprint.route('/change-password', methods = ['GET'])
@setup_globals
@authorized
def change_password_form():
    return render_template('auth/change_password.html')

@authorization_blueprint.route('/change-password', methods = ['POST'])
@setup_globals
@authorized
def save_password_change():
    if request.form['new-password'] != request.form['new-password-repeated']:
        flash('New password and repeated is not same', 'danger')
        return redirect(url_for('auth.change_password_form'))

    user.password = User.hash_password(request.form['new-password'])
    db.session.add(user)
    db.session.commit()

    flash('Password successfuly changed', 'success')

    # mail_message = Message('Password has been changed', recipients = [user.email])
    # mail_message.body = 'Password has been changed'
    # mail.send(mail_message)

    return redirect(url_for('profile'))