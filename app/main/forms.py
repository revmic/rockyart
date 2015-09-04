from flask_wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import TextField, TextAreaField, SubmitField, validators
from wtforms.validators import Required

from app.models import Product, Order


class ContactForm(Form):
    name = TextField('Name', validators=[Required(message="Required")])
    email = TextField('Email', validators=[
        Required(message="Email required"), validators.Email()])
    phone = TextField('Phone Number')
    body = TextAreaField('Message', validators=[Required()])
    send = SubmitField('Send')

ProductForm = model_form(Product, Form)

OrderForm = model_form(Order, Form)
