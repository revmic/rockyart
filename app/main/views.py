import os
import requests
import datetime

from flask import render_template, redirect, url_for, flash, request, Markup
from flask.ext.login import login_required

from app import mailer, models, db, admin
from app.main import main
from app.main.forms import ContactForm
# from app.models import Product, Order
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
        mailer.send_email("Instagram API Error", "inquiry")
        return render_template("blog.html", title='Blog', instagrams=instagrams)

    for instagram in r.json()['data']:
        img = instagram['images']['standard_resolution']['url']
        link = instagram['link']
        # Might not contain a caption
        try:
            caption = instagram['caption']['text']
        except Exception as e:
            print(e, "\nThere doesn't appear to be a caption for this instagram\n", link)
            caption = ""
        # Just in case we can't parse the date
        try:
            dt = datetime.datetime.fromtimestamp(int(instagram['created_time']))
            date_str = dt.strftime('%B %-d, %Y')
        except Exception as e:
            print("Problem getting datetime info\n", e)
            dt = datetime.datetime.now()
            date_str = dt.strftime('%B %-d, %Y')

        instagrams.append({'date_str': date_str, 'datetime': dt, 'image': img,
                           'caption': caption, 'link': link})

    return render_template("blog.html", title='Blog', instagrams=instagrams)


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
    items = models.Product.query.all()

    for i in items:
        print(i.title)

    # Get gallery items
    gallery_images = []
    img_dir = os.path.join(basedir, 'app', 'static', 'img', 'gallery')
    img_path = os.path.join(img_dir, 'jewelry', 'full')

    for img in os.listdir(img_path):
        if 'j' in img and 'g' in img:
            gallery_images.append(img)
    gallery_images = sorted(gallery_images, reverse=True)
    print(gallery_images)

    return render_template("shop.html", title='Rocky Shop', items=items,
                           gallery_images=gallery_images)


@main.route('/shop/<item_id>')
def shop_item(item_id):
    item = models.Product.query.filter_by(id=item_id).first()

    if not item:
        flash('Item not found (id: %s)' % item_id)
        return redirect(url_for('main.shop'))

    return render_template('shop_item.html', item=item)


@main.route('/example-product', methods=['GET'])
def example_product():
    return render_template("example-product.html", title='Products')


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
                  "Sorry about this!", "error")
        else:
            flash("Your message was sent successfully. "
                  "I'll get back to you soon!", "success")
        return redirect(url_for('main.contact'))

    return render_template("contact.html", title='Contact', form=form)


@main.route('/admin')
# @login_required
def admin():
    return render_template("admin.html", title='Admin')


@main.route('/inquiry')
def inquiry():
    form = ContactForm()
    return render_template("inquiry.html", title='Inquiry', form=form)


@main.route('/500')
def e500():
    return render_template('500.html', path=request.path,
                           title='Something Wrong')

