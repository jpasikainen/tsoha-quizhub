from flask import session, flash
from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
from werkzeug.security import check_password_hash
from db import db

class LoginForm(FlaskForm):
    username = TextField("Username:", validators=[DataRequired(), Length(min=3, max=15)])
    password = PasswordField("Password:", validators=[DataRequired(), Length(min=7, max=30)])
    login_button = SubmitField("Login")

def initialize_form():
    return LoginForm()

def login_successful(username, password):
    sql = "SELECT id, password, admin FROM users " \
    "WHERE username=:username AND removed=FALSE"
    user = db.session.execute(sql, {"username":username}).fetchone()

    if user:
        hash_value = user[1]
        if check_password_hash(hash_value, password):
            session["username"] = username
            session["is_admin"] = user[2]
            session["user_id"] = user[0]
            return True
            
    flash("Wrong username or password")
    return False