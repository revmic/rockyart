from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Email


class LoginForm(Form):
    email = StringField(validators=[Required(), Email()])
    password = PasswordField(validators=[Required()])
    # remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')
