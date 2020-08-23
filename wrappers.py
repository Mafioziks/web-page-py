from functools import wraps
from flask import session, redirect, url_for
from models import User, UserPermission, Permission

def is_authorized():
    if 'user' in session:
        return True
    return False

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
            return redirect(url_for('auth.login_form'))
        return r(*args, **kwargs)
    return authorization_setup