from flask import render_template, session, redirect, url_for, flash
from flask.ext.login import login_required

from app import email, db
from app.main import main
from app.main.forms import ContactForm


@main.route('/')
@main.route('/index')
def index():
    return render_template("index.html", title='Home')


@main.route('/blog')
def blog():
    return render_template("blog.html", title='Blog')


@main.route('/gallery')
def gallery():
    return render_template("gallery.html", title='About')


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        try:
            email.send_email("Customer Inquiry", "inquiry")
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
@login_required
def admin():
    return render_template("admin.html", title='Admin')


@main.route('/inquiry')
def inquiry():
    form = ContactForm()
    return render_template("inquiry.html", title='Inquiry', form=form)
