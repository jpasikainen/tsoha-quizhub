from flask import session, flash
from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash
from db import db

class RegisterForm(FlaskForm):
    username = TextField("Username:", validators=[DataRequired(), Length(min=3, max=15)])
    password = PasswordField("Password:", validators=[DataRequired(), \
        EqualTo('confirm', message='Passwords must match'), Length(min=7, max=30)])
    confirm = PasswordField("Confirm", validators=[DataRequired()])
    register_button = SubmitField("Register")

def initialize_form():
    return RegisterForm()

def username_is_valid(username):
    sql = "SELECT COUNT(*) FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username}).fetchone()[0]
    if result == 0:
        return True
    flash("Username has been taken. Try another one.")
    return False

def save_credentials(username, password):
    hash_value = generate_password_hash(password)
    sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
    db.session.execute(sql, {"username":username, "password":hash_value})
    db.session.commit()