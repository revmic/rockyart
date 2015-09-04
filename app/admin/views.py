from flask import request, render_template, redirect, url_for, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
# from flask.ext.login import login_required

from app import db, admin
from app.models import Product, Order
from app.admin.forms import ProductForm


# @login_required
class ProductView(ModelView):
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        p = Product.query.all()
        return self.render('admin/create_product.html', product=p)

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        pid = request.args.get('id')
        product = Product.query.filter_by(id=pid).first()
        form = ProductForm(request.form, product)
        # form.populate_obj(product)

        return self.render('admin/edit_product.html', pid=pid, product=product, form=form)


# @login_required
class DashboardView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/admin_dashboard.html')

# admin.index_view = DashboardView(name='Dashboard', template='admin/admin_dashboard.html')
# # admin.add_view(DashboardView(name='Dashboard'))  #, endpoint='dashboard'))
admin.add_view(ProductView(Product, db.session, name="Products"))
admin.add_view(ModelView(Order, db.session, name="Orders"))
