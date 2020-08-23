from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

db = SQLAlchemy()

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