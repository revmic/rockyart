from flask_wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, validators
from wtforms.validators import Required

class ContactForm(Form):
    name = TextField('Name', validators=[Required(message="Required")])
    email = TextField('Email', validators=[
        Required(message="Email required"), validators.Email()])
    phone = TextField('Phone Number')
    body = TextAreaField('Message', validators=[Required()])
    send = SubmitField('Send')
