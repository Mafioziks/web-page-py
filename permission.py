from flask import Blueprint, render_template, session, g
from models import User, Permission, UserPermission
from app_wrappers import is_authorized, authorized, setup_globals

permission_blueprint = Blueprint('permission', __name__, template_folder='templates/permission')

@permission_blueprint.route('/my', methods = ['GET'])
@setup_globals
@authorized
def user_list():
    user            = g.get('user', None)
    user_permission = UserPermission.query.filter_by(user_id=user.id).all()
    permission_ids  = set()

    for permission_relation in user_permission:
        permission_ids.add(permission_relation.permission_id)

    filtered_permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()

    return render_template('permission_list.html', permission_list=filtered_permissions)