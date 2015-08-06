import os
import shutil
import requests
from datetime import datetime

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_admin import expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.uploads import UploadSet, IMAGES
# from flask.ext.login import login_required
from sqlalchemy.sql.expression import true, false

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
    """
    Get all shop items, main images, and gallery images
    """
    result = Product.query.all()
    shop_items = []
    main_images = {}
    gallery_images = []

    # Only show shop item if it's published and is in stock
    for product in result:
        if product.published and product.quantity > 0:
            shop_items.append(product)

    for product in shop_items:
        # Use in case none are set as main image
        try:
            main_img = product.images[0].full_path  # TODO make thumb_path
        except IndexError:
            main_img = None

        # Then search for one that's properly set
        for img in product.images:
            if img.main_image:
                main_img = img.full_path
            if img.gallery_image:
                gallery_images.append(img)

        main_images[product.id] = main_img

    print(main_images)

    return render_template("shop.html", title='Rocky Shop', items=shop_items,
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
        except Exception as e:
            flash("Something went wrong while sending your message. "
                  "Please email rockypardo.art@gmail.com with your question. "
                  "And if you're feeling generous with your time, "
                  "send mhilema@gmail.com a message about this error. "
                  "Sorry about this!", "danger")
            print(e)
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

photos = UploadSet('photos', IMAGES)


@main.route('/admin/products', methods=['GET', 'POST'])
def products():
    all_products = Product.query.all()
    product_images = {}
    new_id = all_products[-1].id + 1

    for p in all_products:
        product_images[p.id] = \
            ProductImage.query.filter_by(product_id=p.id).all()
    print(product_images)

    if request.method == "POST":
        return redirect(url_for('products'))

    return render_template("admin/products.html",products=all_products,
                           product_images=product_images, new_id=new_id)


# @login_required
class ProductView(ModelView):
    categories = ['necklace', 'ring', 'earring', 'bracelet']

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        new_product = Product(creation_date=datetime.now(), quantity=1)
        form = ProductForm(request.form, new_product)
        product_id = request.args.get('id')

        if request.method == 'POST':
            try:
                db.session.add(new_product)
                db.session.commit()
            except Exception as e:
                msg = "Something happened with product creation."
                flash(msg, "danger")
                print(msg)
                print(e)

            self.save(new_product, form)

            return redirect('/admin/product/edit?id=' + str(new_product.id))

        return self.render('admin/manage_product.html', form=form,
                           product=new_product, product_id=product_id,
                           creating=True, categories=self.categories)

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        product_id = request.args.get('id')
        product = Product.query.filter_by(id=product_id).first()
        product_images = ProductImage.query.filter_by(
            product_id=product_id).all()
        form = ProductForm(request.form, product)

        # image_paths = []
        #
        # for img in product_images:
        #     image_paths.append(img.full_path)

        if not product_images:
            print("No images for product id:", product_id)
        else:
            print("Product images:", product_images)

        # Handle different form requests by name
        # if form.validate_on_submit():
        if request.method == 'POST':
            if 'save' in request.form:
                self.save(product, form)
            elif 'publish' in request.form:
                self.save(product, form)
                self.publish(product.id)
            elif 'publish_add' in request.form:
                print("Publish and add another")
            elif 'delete' in request.form:
                self.delete(product)

            # Go back to edit screen if not redirected elsewhere
            return redirect('/admin/product/edit?id=' + product_id)

        return self.render('admin/manage_product.html',
                           product=product, images=product_images, form=form,
                           categories=self.categories, product_id=product.id)

    @staticmethod
    def save(product, form):
        product.title = form.title.data
        product.category = form.category.data
        product.quantity = form.quantity.data
        product.price = form.price.data
        product.description = form.description.data
        product.creation_date = form.creation_date.data

        msg = "Saved product id " + str(product.id)
        print(msg)
        flash(msg, "success")

    @staticmethod
    def publish(product_id):
        """
        Toggles a product between published and unpublished
        """
        product = Product.query.filter_by(id=product_id).first()

        # product.published = True
        print("Publishing product " + str(product_id))

        if not product.published:
            product.published = True
            flash("Published " + product.title, "success")
        else:
            product.published = False
            flash("Unpublished " + product.title, "success")

        db.session.commit()

    @staticmethod
    def delete(product):
        print("Deleting product " + str(product.id))
        product_images = ProductImage.query.filter_by(
            product_id=product.id).all()
        img_path_abs = os.path.join(
            basedir, 'app/static/img/store/%s' % product.id)

        shutil.rmtree(img_path_abs, ignore_errors=True)

        for img in product_images:
            db.session.delete(img)

        db.session.delete(product)
        db.session.commit()

        flash("Deleted " + product.title +
              " (id " + str(product.id) + ")", "success")

        return redirect('/admin/products')


@main.route('/admin/image/upload', methods=['POST'])
def upload():
    f = request.files['file']
    pid = request.args.get("product_id")
    upload_dir = os.path.join(basedir, 'app/static/img/store/%s' % pid)
    print("Uploading " + f.filename + " to " + upload_dir)

    if not os.path.exists(upload_dir):
        os.mkdir(upload_dir)

    # Save to filesystem
    f.save(os.path.join(upload_dir, f.filename))
    file_size = os.path.getsize(os.path.join(upload_dir, f.filename))

    # TODO create thumbs

    # Save to database
    rel_path = 'img/store/%s/%s' % (pid, f.filename)
    image = ProductImage(product_id=pid, full_path=rel_path, thumb_path='')
    db.session.add(image)
    db.session.commit()

    print(jsonify(name=f.filename, size=file_size))
    return jsonify(name=f.filename, size=file_size)


@main.route('/admin/image/remove', methods=['POST'])
def remove():
    """Delete an uploaded file."""
    # img_file = ProductImage.query.get_or_404(img)
    product_id = request.args.get("product_id")
    img_arg = request.args.get("img").lstrip(os.path.sep)  # del leading /
    img_path = os.path.join(basedir, 'app/static', img_arg)
    db_img = ProductImage.query.filter_by(full_path=img_arg).first()
    print(db_img)

    db.session.delete(db_img)
    db.session.commit()

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


@main.route('/admin/image/<image_id>/main', methods=['POST'])
def main_image(image_id):
    image = ProductImage.query.filter_by(id=image_id).first()
    print("Making", os.path.basename(image.full_path), "a main image")

    # get current main image if any and set image.main to false
    all_images = ProductImage.query.all()
    for img in all_images:
        img.main_image = False

    # then set this one to true
    image.main_image = True

    return jsonify(name=image_id)


@main.route('/admin/image/<image_id>/gallery', methods=['POST'])
def gallery_image(image_id):
    image = ProductImage.query.filter_by(id=image_id).first()
    fname = os.path.basename(image.full_path)

    if image.gallery_image:
        print("Setting image", fname, "to FALSE")
        image.gallery_image = False
    else:
        print("Setting image", fname, "to TRUE")
        image.gallery_image = True

    return jsonify(name=fname)


admin.add_view(ProductView(Product, db.session, name="Products"))
admin.add_view(ModelView(Order, db.session, name="Orders"))
admin.add_view(ModelView(ProductImage, db.session, name="Images"))
