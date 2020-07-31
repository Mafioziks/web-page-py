from flask import Flask, request, redirect, url_for, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'backend_ap1_k3y'

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

db.create_all()

# app

@app.route('/')
def main():
    return 'Hello world!'

@app.route('/user', methods = ['GET'])
def user_list():
    list_of_users = User.query.all()
    return render_template("user/list.html", user_list=list_of_users) 

@app.route('/auth/login', methods = ['GET'])
def login_form():
    return render_template('auth/login.html')

@app.route('/auth/login', methods = ['POST'])
def auth_login():
    content = request.get_json()

    return str(content)

    # if ()
    # if (request.)

if __name__ == '__main__':
    app.run(debug=True)