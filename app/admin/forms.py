from flask_wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form

from app.models import Product, Order

ProductForm = model_form(Product, Form)
OrderForm = model_form(Order, Form)
