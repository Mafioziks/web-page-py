from functools import wraps
from flask import session, redirect, url_for, g
from models import User, UserPermission, Permission

def is_authorized():
    if 'user' in session:
        return True
    return False

def setup_user():
    if is_authorized():
        user = User.query.filter_by(id=session['user']).first()

        if None is user:
            session.pop('user', None)
            g.pop('user')
            return
        g.user = user
            

def setup_permissions():
    if not is_authorized():
        return
    
    user = g.get('user')
    user_permissions = UserPermission.query.filter_by(user_id=user.id).all()
    permission_ids   = set()

    for user_permission in user_permissions:
        permission_ids.add(user_permission.permission_id)

    permissions = g.get('permissions', set())
    filtered_permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()

    for filtered_permission in filtered_permissions:
        permissions.add(filtered_permission.name)

    g.permissions = permissions

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