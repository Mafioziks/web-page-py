from flask import Blueprint
from models import User
from app_wrappers import is_authorized, authorized, setup_globals

admin_blueprint = Blueprint('admin', __name__, template_folder='templates/admin')

@admin_blueprint.route('/users', methods = ['GET'])
@setup_globals
@authorized
def user_list():
    return render_template('user_list.html', user_list=User.query.all(), authorized=is_authorized())