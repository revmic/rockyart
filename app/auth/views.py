from flask import render_template, redirect, request, flash, g
from flask.ext.login import login_user, logout_user, login_required

from app.auth import auth
from app.models import User
from app.auth.forms import LoginForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # if form.validate_on_submit():
    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user, False)  # or form.remember_me.data
            return redirect(request.args.get('next') or '/admin')
        flash('Invalid username or password', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    g.user = None
    flash('You have been logged out.', 'info')
    return redirect('/admin')
