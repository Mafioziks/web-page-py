from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

if None != app:
    db = SQLAlchemy(app)

def User(db.Model):
    first_name = db.
