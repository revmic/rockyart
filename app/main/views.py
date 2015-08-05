import os
import requests
from datetime import datetime

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify
)
from flask_admin import AdminIndexView, expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.uploads import UploadSet, IMAGES
from flask.ext.login import login_required

from app import mailer, db, admin
from app.main import main
from app.models import Product, ProductImage, Order
from app.main.forms import ContactForm, ProductForm
from config import basedir, INSTAGRAM_KEY


@main.route('/')
@main.route('/index')
def index():
    return render_template("index.html", title='Home')


@main.route('/blog')
def blog():
    instagrams = []
    uri = 'https://api.instagram.com/v1/users/2099685218/media/recent/' \
          '?client_id=' + INSTAGRAM_KEY
    r = requests.get(uri)

    try:
        r.raise_for_status()
    except Exception as e:
        print(e, "\nProblem connecting with Instagram api\n", uri)
        flash(e, "danger")
        flash("Error connecting with Instagram api", "danger")

        # mailer.send_email("Instagram API Error", "inquiry")
        return render_template("blog.html", title='Blog', instagrams=instagrams)

    if len(r.json()['data']) == 0:
        flash("No instagram posts found. Probably an issue with the api. "
              "Try checking back later.", "warning")

    for instagram in r.json()['data']:
        img = instagram['images']['standard_resolution']['url']
        link = instagram['link']
        # Might not contain a caption
        try:
            caption = instagram['caption']['text']
        except Exception as e:
            print(e, "\nThere doesn't appear to be a caption "
                     "for this instagram\n", link)
            caption = ""
        # Just in case we can't parse the date
        try:
            dt = datetime.fromtimestamp(int(instagram['created_time']))
            date_str = dt.strftime('%B %-d, %Y')
        except Exception as e:
            print("Problem getting datetime info\n", e)
            dt = datetime.now()
            date_str = dt.strftime('%B %-d, %Y')

        instagrams.append({'date_str': date_str, 'datetime': dt, 'image': img,
                           'caption': caption, 'link': link})

    return render_template("blog.html", title='Blog', instagrams=instagrams)


@main.route('/blog/statement')
def statement():
    return render_template("statement.html", title='Artist Statement')


@main.route('/gallery')
def gallery():
    img_dir = os.path.join(basedir, 'app', 'static', 'img', 'gallery')
    category = request.args.get("c")
    images = []

    if category == "jewelry":
        img_path = os.path.join(img_dir, 'jewelry', 'full')
    elif category == "drawings":
        img_path = os.path.join(img_dir, 'drawings', 'full')
    else:
        img_path = os.path.join(img_dir, 'jewelry', 'full')

    for img in os.listdir(img_path):
        if 'j' in img and 'g' in img:
            images.append(img)

    # Sort reverse if jewelry
    if category == "jewelry":
        images = sorted(images, reverse=True)

    return render_template("gallery.html", title='Gallery',
                           images=images, c=category)


@main.route('/shop', methods=['GET'])
def shop():
    # Get all shop items
    result = Product.query.all()
    items = []

    # Only show shop item if it's published and is in stock
    for item in result:
        if item.published and item.quantity > 0:
            items.append(item)

    # Get product main images
    # Use absolute path for directory listing
    img_base_dir = os.path.join(basedir, 'app/static/img/store')
    main_images = {}

    for item in items:
        img_abs_path = os.path.join(img_base_dir, str(item.id))
        main_img = None
        try:
            main_img = os.listdir(img_abs_path)[0]
        except:
            pass

        img_rel_path = os.path.join('img/store/%s/%s' % (item.id, main_img))
        main_images[item.id] = img_rel_path

    print(main_images)

    # Use absolute path for directory listing
    # img_path_abs = os.path.join(basedir, 'app/static/img/store/%s' % item_id)
    # Use relative path to make url building easier
    # img_path_rel = 'img/store/%s/' % item_id
    # img_files = os.listdir(img_path_abs)
    # item_images = []

    # Get gallery items
    gallery_images = []
    img_dir = os.path.join(basedir, 'app', 'static', 'img', 'gallery')
    img_path = os.path.join(img_dir, 'jewelry', 'full')

    for img in os.listdir(img_path):
        if 'j' in img and 'g' in img:
            gallery_images.append(img)

    gallery_images = sorted(gallery_images, reverse=True)

    return render_template("shop.html", title='Rocky Shop', items=items,
                           gallery_images=gallery_images,
                           main_images=main_images)


@main.route('/shop/<item_id>')
def shop_item(item_id):
    item = Product.query.filter_by(id=item_id).first()

    if not item:
        flash('Item not found (id: %s)' % item_id, "warning")
        return redirect(url_for('main.shop'))

    # Use absolute path for directory listing
    img_path_abs = os.path.join(basedir, 'app/static/img/store/%s' % item_id)
    # Use relative path to make url building easier
    img_path_rel = 'img/store/%s/' % item_id

    item_images = []
    img_files = []
    try:
        img_files = os.listdir(img_path_abs)
    except FileNotFoundError:
        print("No images for product id " + item_id)

    for i in img_files:
        item_images.append(os.path.join(img_path_rel, i))

    print(item_images)

    return render_template('shop_item.html', item=item, images=item_images)


@main.route('/cart', methods=['GET'])
def cart():
    return render_template("cart.html", title='Shopping Cart')


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        try:
            mailer.send_email("Customer Inquiry", "inquiry")
        except:
            flash("Something went wrong while sending your message. "
                  "Please email rockypardo.art@gmail.com with your question. "
                  "And if you're feeling generous with your time, "
                  "send mhilema@gmail.com a message about this error. "
                  "Sorry about this!", "danger")
        else:
            flash("Your message was sent successfully. "
                  "I'll get back to you soon!", "success")
        return redirect(url_for('main.contact'))

    return render_template("contact.html", title='Contact', form=form)


@main.route('/inquiry')
def inquiry():
    form = ContactForm()
    return render_template("inquiry.html", title='Inquiry', form=form)


@main.route('/500')
def e500():
    return render_template('500.html', path=request.path,
                           title='Something Wrong')


###############
# ADMIN VIEWS #
###############

admin.base_template = "admin/manage_product.html"
photos = UploadSet('photos', IMAGES)


# @login_required
class ProductView(ModelView):
    categories = ['necklace', 'ring', 'earring', 'bracelet']

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        new_product = Product(creation_date=datetime.now(), quantity=1)
        form = ProductForm(request.form, new_product)

        if request.method == 'POST':
            try:
                db.session.add(new_product)
                db.session.commit()
            except Exception as e:
                msg = "Something happened with product creation."
                flash(msg, "danger")
                print(msg)
                print(e)

            self.save_product(new_product, form)
            return redirect('/admin/product/edit?id=' + str(new_product.id))

        return self.render('admin/manage_product.html', form=form,
                           product=new_product, creating=True,
                           categories=self.categories)

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        product_id = request.args.get('id')
        img_path_abs = os.path.join(
            basedir, 'app/static/img/store/%s' % product_id)
        img_path_rel = 'img/store/%s/' % product_id
        images = []

        try:
            for img in os.listdir(img_path_abs):
                images.append(os.path.join(img_path_rel, img))
        except FileNotFoundError:
            # images = ['img/store/placeholder.jpg']
            print("No images for product id: " + product_id)

        product = Product.query.filter_by(id=product_id).first()
        form = ProductForm(request.form, product)

        # if form.validate_on_submit():
        # TODO break up into functions
        if request.method == 'POST':
            print(request.form)
            if 'save' in request.form:
                self.save_product(product, form)
            if 'publish' in request.form:
                self.save_product(product, form)
                publish_product(product.id)
                if product.published:
                    flash("Published " + product.title, "success")
                else:
                    flash("Unpublished " + product.title, "success")
            if 'publish_add' in request.form:
                print("Publish and add another")
            if 'delete' in request.form:
                print("Deleting")
                db.session.delete(product)
                # TODO delete images
                flash("Deleted " + product.title +
                      " (id " + str(product.id) + ")", "success")
                return redirect('/admin/product')

            return redirect('/admin/product/edit?id=' + product_id)

        return self.render('admin/manage_product.html',
                           product=product, images=images, form=form,
                           categories=self.categories)

    @staticmethod
    def save_product(product, form):
        product.title = form.title.data
        product.category = form.category.data
        product.quantity = form.quantity.data
        product.price = form.price.data
        product.description = form.description.data
        product.creation_date = form.creation_date.data

        msg = "Saved product id " + str(product.id)
        print(msg)
        flash(msg, "success")


# @login_required
class DashboardView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/admin_dashboard.html')

# admin.index_view = DashboardView(name='Dashboard', endpoint='dashboard',
#   template='admin/admin_dashboard.html')
# admin.add_view(DashboardView(name='Dashboard'))  #, endpoint='dashboard'))
admin.add_view(ProductView(Product, db.session, name="Products"))
admin.add_view(ModelView(Order, db.session, name="Orders"))
admin.add_view(ModelView(ProductImage, db.session, name="Images"))


@main.route('/admin/upload', methods=['POST'])
def upload():
    f = request.files['file']
    pid = request.args.get("product_id")
    upload_dir = os.path.join(basedir, 'app/static/img/store/%s' % pid)
    print("Uploading " + f.filename + " to " + upload_dir)

    if not os.path.exists(upload_dir):
        os.mkdir(upload_dir)

    f.save(os.path.join(upload_dir, f.filename))
    file_size = os.path.getsize(os.path.join(upload_dir, f.filename))

    # TODO create thumbs

    # TODO Write to db ??? Could do FS operations on ID directory

    print(jsonify(name=f.filename, size=file_size))
    return jsonify(name=f.filename, size=file_size)


# @main.route('/admin/product/<id>/publish', methods=['POST'])
def publish_product(id):
    """
    Toggles a product between published and unpublished
    """
    product = Product.query.filter_by(id=id).first()

    # product.published = True
    print(product.published)

    if not product.published:
        product.published = True
    else:
        product.published = False

    db.session.commit()
    return True


@main.route('/admin/remove', methods=['POST'])
def remove():
    """Delete an uploaded file."""
    # img_file = ProductImage.query.get_or_404(img)
    product_id = request.args.get("product_id")
    img_arg = request.args.get("img").lstrip(os.path.sep)  # del leading /
    img_path = os.path.join(basedir, 'app', img_arg)

    try:
        print("Removing " + img_path)
        os.remove(img_path)
    except Exception as e:
        print(e)
        flash("Could not remove " + img_path, "danger")
    else:
        flash("Successfully removed " + os.path.basename(img_path), "success")

    redirect_url = '/admin/product/edit?id=' + product_id
    return redirect(redirect_url)
