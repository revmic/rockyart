import os
import shutil
from datetime import datetime

import requests
from PIL import Image
from flask import render_template, redirect, url_for, flash, request, jsonify, g
from flask_admin import expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.uploads import UploadSet, IMAGES
# from flask.ext.login import login_required, current_user

from app import mailer, db, admin
from app.main import main
from app.models import Product, ProductImage, ProductOption, Order, User
from app.main.forms import ContactForm, ProductForm
from config import basedir, INSTAGRAM_KEY

debug = 'DEBUG'
info = 'INFO'
warn = 'WARN'
error = 'ERROR'


@main.route('/')
@main.route('/index')
def index():
    carousel_pid = Product.query.filter_by(title='carousel').first()
    carousel_paths = []

    if carousel_pid:
        carousel_id = carousel_pid.id
        carousel_imgs = \
            ProductImage.query.filter_by(product_id=carousel_id).all()

        for img in carousel_imgs:
            carousel_paths.append(img.full_path)
    else:
        print(error, "The carousel product doesn't seem to exist. "
                     "Create it in the product interface.")

    return render_template(
        "index.html", title='Home', carousel_images=carousel_paths)


@main.route('/blog')
def blog():
    instagrams = []
    uri = 'https://api.instagram.com/v1/users/2099685218/media/recent/' \
          '?client_id=' + INSTAGRAM_KEY
    r = requests.get(uri)

    try:
        r.raise_for_status()
    except Exception as e:
        print(e)
        print(error, "Problem connecting with Instagram api\n", uri)
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
            print(e)
            print(error, "There doesn't appear to be a caption "
                         "for this instagram", link)
            caption = ""
        # Just in case we can't parse the date
        try:
            dt = datetime.fromtimestamp(int(instagram['created_time']))
            date_str = dt.strftime('%B %-d, %Y')
        except Exception as e:
            print(error, "Problem getting datetime info\n", e)
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
    Get all shop items, main images, gallery images, and render the storefront
    """
    results = Product.query.all()
    shop_items = []
    main_images = {}
    price_ranges = {}
    gallery_images = []

    # Only show shop item if it's published and is in stock
    for product in results:
        if product.published and product.quantity > 0:
            shop_items.append(product)

    for product in results:
        # Use the first image in case none are set as main
        main_img = ''
        try:
            main_img = product.images[0].thumb_path
        except IndexError:
            pass

        # Then search for one that's properly set
        try:
            for img in product.images:
                if img.main_image:
                    main_img = img.thumb_path
                if img.gallery_image:
                    gallery_images.append(img)
        except IndexError:
            pass

        main_images[product.id] = main_img

        # Figure out if there's a range in pricing or not
        try:
            price_lo = product.options[0].price
            price_hi = product.options[-1].price
        except:
            continue

        if price_lo == price_hi:
            # Use the string of the integer value
            price_ranges[product.id] = str(int(price_lo))
        else:
            price_ranges[product.id] = "%d-%d" % (price_lo, price_hi)

    print(debug, main_images)

    return render_template("shop.html", title='Rocky Shop', items=shop_items,
                           main_images=main_images, price_ranges=price_ranges,
                           gallery_images=gallery_images)


@main.route('/shop/<item_id>')
def shop_item(item_id):
    item = Product.query.filter_by(id=item_id).first()

    if not item:
        flash('Item not found (id: %s)' % item_id, "warning")
        return redirect(url_for('main.shop'))

    opt_label = "Option:"
    if item.category == "necklace" or item.category == "bracelet":
        opt_label = "Length:"
    elif item.category == "ring" or item.category == "earring":
        opt_label = "Size:"

    item_images = ProductImage.query.filter_by(product_id=item_id).all()
    image_paths = []

    for img in item_images:
        image_paths.append(img.full_path)

    print(debug, item_images)

    return render_template('shop_item.html', item=item, images=image_paths,
                           option_label=opt_label)


@main.route('/cart', methods=['GET'])
def cart():
    return render_template("cart.html", title='Shopping Cart')


@main.route('/cart/success', methods=['GET', 'POST'])
def cart_success():
    return render_template("order_successful.html", title='Order Successful')


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

from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


@main.route('/admin/products', methods=['GET', 'POST'])
# @login_required
@auth.login_required
def view_products():
    all_products = Product.query.all()
    product_images = {}
    product_options = {}
    new_id = all_products[-1].id + 1

    for p in all_products:
        product_images[p.id] = \
            ProductImage.query.filter_by(product_id=p.id).all()
        product_options[p.id] = \
            ProductOption.query.filter_by(product_id=p.id).all()

    # print(debug, product_images)

    if request.method == "POST":
        return redirect(url_for('view_products'))

    return render_template("admin/products.html", products=all_products,
                           product_images=product_images, new_id=new_id,
                           product_options=product_options)


class ProductView(ModelView):
    categories = ['necklace', 'ring', 'earring', 'bracelet']

    # @expose('/')
    # @auth.login_required
    # def index(self):
    #     if not current_user.is_authenticated():
    #         return redirect(url_for('view_products'))
    #     return super(ProductView, self).index()

    @expose('/new/', methods=('GET', 'POST'))
    @auth.login_required
    def create_view(self):
        new_product = Product(creation_date=datetime.now(), quantity=1)
        form = ProductForm(request.form, new_product)
        product_id = request.args.get('id')

        if request.method == 'POST':
            # if not record_exists:
            try:
                db.session.add(new_product)
                db.session.commit()
            except Exception as e:
                msg = "Something happened with product creation."
                flash(msg, "danger")
                print(error, msg)
                print(e)

            self.save(new_product, form)

            return redirect('/admin/product/edit?id=' + str(new_product.id))

        return self.render('admin/manage_product.html', form=form,
                           product=new_product, product_id=product_id,
                           creating=True, categories=self.categories)

    @expose('/edit/', methods=('GET', 'POST'))
    @auth.login_required
    def edit_view(self):
        product_id = request.args.get('id')
        product = Product.query.filter_by(id=product_id).first()
        product_images = ProductImage.query.filter_by(
            product_id=product_id).all()
        product_options = ProductOption.query.filter_by(
            product_id=product_id).all()
        # product_options = [{'name': 'size 1', 'price': 123, 'quantity': 2},
        #                    {'name': 'size 2', 'price': 134, 'quantity': 1}]
        form = ProductForm(request.form, product)

        # image_paths = []
        #
        # for img in product_images:
        #     image_paths.append(img.full_path)

        if not product_images:
            print(warn, "No images for product id:", product_id)
        else:
            print(debug, "Product images:", product_images)

        # Handle different form requests by name
        # if form.validate_on_submit():
        if request.method == 'POST':
            # Main form elements
            if 'save' in request.form:
                self.save(product, form)
            elif 'publish' in request.form:
                self.save(product, form)
                self.publish(product.id)
            elif 'publish_add' in request.form:
                print("Publish and add another")
            elif 'delete' in request.form:
                self.delete(product)

            # Option form elements
            elif 'save_option' in request.form:
                self.save_option(product)
            elif 'update_option' in request.form:
                self.update_option()
                print(request.form)
            elif 'remove_option' in request.form:
                self.remove_option()

            # Go back to edit screen if not redirected elsewhere by prev request
            return redirect('/admin/product/edit?id=' + product_id)

        return self.render('admin/manage_product.html',
                           product=product, images=product_images, form=form,
                           categories=self.categories, product_id=product.id,
                           options=product_options)

    @staticmethod
    def save(product, form):
        product.title = form.title.data
        product.category = form.category.data
        product.quantity = form.quantity.data
        product.price = form.price.data
        product.description = form.description.data
        product.creation_date = form.creation_date.data

        msg = "Saved product id " + str(product.id)
        print(info, msg)
        flash(msg, "success")

    @staticmethod
    @auth.login_required
    def publish(product_id):
        """
        Toggles a product between published and unpublished
        """
        product = Product.query.filter_by(id=product_id).first()

        # product.published = True
        print(info, "Publishing product " + str(product_id))

        if not product.published:
            product.published = True
            flash("Published " + product.title, "success")
        else:
            product.published = False
            flash("Unpublished " + product.title, "success")

        db.session.commit()

    @staticmethod
    @auth.login_required
    def delete(product):
        print(info, "Deleting product " + str(product.id))
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

    @staticmethod
    @auth.login_required
    def save_option(product):
        print(info, "Saving option for", product.title)
        opt = ProductOption(product_id=product.id,
                            name=request.form['opt_name'],
                            price=request.form['opt_price'],
                            quantity=request.form['opt_qty'])
        db.session.add(opt)
        db.session.commit()

    @staticmethod
    @auth.login_required
    def update_option():
        opt_id = request.form['update_option']
        print(info, "Updating option id", opt_id)

        option = ProductOption.query.filter_by(id=opt_id).first()
        print(request.form)
        option.name = request.form['opt_name_'+opt_id]
        option.price = request.form['opt_price_'+opt_id]
        option.quantity = request.form['opt_qty_'+opt_id]
        # db.session.add(option)
        # db.session.commit()

    @staticmethod
    @auth.login_required
    def remove_option():
        opt_id = request.form['remove_option']
        option = ProductOption.query.filter_by(id=opt_id).first()
        print(info, "Removing", option.name, "option")

        db.session.delete(option)
        db.session.commit()


@main.route('/admin/orders', methods=['GET', 'PUT'])
@auth.login_required
def view_orders():
    all_orders = Order.query.all()
    return render_template("admin/orders.html", orders=all_orders)


@main.route('/admin/orders/<oid>/edit', methods=['GET', 'PUT'])
@auth.login_required
def edit_order(oid):
    order = Order.query.filter_by(id=oid).first()
    products = Product.query.filter_by(order_id=oid).all()

    return render_template("admin/manage_order.html", order=order,
                           products=products)


@main.route('/admin/images', methods=['GET', 'PUT'])
@auth.login_required
def image_admin():
    images = ProductImage.query.all()
    gallery_product = Product.query.filter_by(title="gallery").first()

    return render_template("admin/image_admin.html", images=images,
                           gallery=gallery_product)


@main.route('/admin/image/upload', methods=['POST'])
@auth.login_required
def upload():
    f = request.files['file']
    pid = request.args.get("product_id")
    upload_dir = os.path.join(basedir, 'app/static/img/store/%s' % pid)
    print(info, "Uploading " + f.filename + " to " + upload_dir)

    if not os.path.exists(upload_dir):
        os.mkdir(upload_dir)

    # Save to filesystem
    f.save(os.path.join(upload_dir, f.filename))
    file_size = os.path.getsize(os.path.join(upload_dir, f.filename))

    # Create thumb
    infile = os.path.join(upload_dir, f.filename)
    outfile = os.path.join(upload_dir, 'thumb_'+f.filename)
    make_thumb(infile, outfile)

    # Save to database
    rel_path = 'img/store/%s/%s' % (pid, f.filename)
    thumb_path = 'img/store/%s/%s' % (pid, 'thumb_'+f.filename)
    image = ProductImage(product_id=pid, filename=f.filename,
                         full_path=rel_path, thumb_path=thumb_path)
    db.session.add(image)
    db.session.commit()

    return jsonify(name=f.filename, size=file_size, product_id=pid)


@main.route('/admin/image/<image_id>/thumb', methods=['POST'])
@auth.login_required
def create_thumb(image_id):
    fullsize_path = ProductImage.query.filter_by(id=image_id).first().full_path
    image_name = os.path.basename(fullsize_path)
    path_name = os.path.dirname(fullsize_path)
    thumb_path = os.path.join(path_name, 'thumb_'+image_name)
    fullsize_abs_path = os.path.join(basedir, 'app', 'static', fullsize_path)
    thumbnail_abs_path = os.path.join(basedir, 'app', 'static', thumb_path)
    print(info, "Creating thumb for", fullsize_path)

    make_thumb(fullsize_abs_path, thumbnail_abs_path)

    return jsonify(id=image_id, fullsize_path=fullsize_path,
                   thumbnail_path=thumb_path)


def make_thumb(infile, outfile):
    try:
        im = Image.open(infile)
        size = (256, 256)
        im.thumbnail(size)
        im.save(outfile, "JPEG")
    except IOError as e:
        print(e)
        print(error, "Couldn't create thumbnail for", infile)


@main.route('/admin/image/<image_id>/main', methods=['POST'])
@auth.login_required
def main_image(image_id):
    image = ProductImage.query.filter_by(id=image_id).first()

    # get product images and set them all to false
    product_images = ProductImage.query.filter_by(
        product_id=image.product_id).all()

    print(info, "Unsetting main image for " + str(image.product_id))

    for img in product_images:
        img.main_image = False

    # then set this one to true
    print(info, "Making", os.path.basename(image.full_path), "the main image")
    image.main_image = True

    return jsonify(name=image_id)


@main.route('/admin/image/<image_id>/gallery', methods=['POST'])
@auth.login_required
def gallery_image(image_id):
    image = ProductImage.query.filter_by(id=image_id).first()
    fname = os.path.basename(image.full_path)

    if image.gallery_image:
        print(info, "Removing", fname, "from gallery")
        image.gallery_image = False
    else:
        print(info, "Adding", fname, "to gallery")
        image.gallery_image = True

    return jsonify(name=fname)


@main.route('/admin/image/<image_id>/remove', methods=['POST'])
@auth.login_required
def remove(image_id):
    """Delete an uploaded file."""
    img = ProductImage.query.filter_by(id=image_id).first()
    product_id = img.product_id
    img_path_abs = os.path.join(basedir, 'app', 'static', img.full_path)
    thumb_path_abs = os.path.join(basedir, 'app', 'static', img.thumb_path)
    # db_img = ProductImage.query.filter_by(full_path=img_arg).first()
    print(debug, img)

    db.session.delete(img)
    db.session.commit()

    try:
        print(info, "Removing " + img.full_path)
        os.remove(img_path_abs)
        os.remove(thumb_path_abs)
    except Exception as e:
        print(e)
        flash("Could not remove " + img_path_abs, "danger")
    else:
        flash("Successfully removed " +
              os.path.basename(img_path_abs), "success")

    print(request.path)
    if request.args.get('redirect'):
        redirect_url = request.args.get('redirect')
    else:
        # Go to the product the image belonged to
        redirect_url = '/admin/product/edit?id=' + str(product_id)

    return redirect(redirect_url)


@main.route('/admin/product/<pid>/options/add', methods=['POST', 'DELETE'])
@auth.login_required
def product_options(pid):
    option_value = request.form['option_value']

    print("Adding option", option_value, "for product id", pid)

    return ""


admin.add_view(ProductView(Product, db.session, name="Products"))
admin.add_view(ModelView(Order, db.session, name="Orders"))
admin.add_view(ModelView(ProductImage, db.session, name="Images"))
