from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo

class loginForm(FlaskForm):
    
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    login = SubmitField("Log In")

class createUserForm(FlaskForm):
    
    email = StringField("Email", validators=[DataRequired()])
    username = StringField("Username")
    password = PasswordField("Password", validators=[DataRequired(), EqualTo("confirmPass", "Passwords must match")])
    confirmPass = PasswordField("Confirm Password", validators=[DataRequired()])
    create = SubmitField("Create Account")