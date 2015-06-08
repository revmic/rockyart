from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user

from app.auth import auth
from app.models import User
from app.auth.forms import LoginForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user, False)  # or form.remember_me.data
            return redirect(request.args.get('next') or url_for('admin'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)
