from flask import Blueprint, render_template, redirect, url_for, flash
from urllib.parse import urlparse
from app.models import User
from flask_login import current_user, login_user, logout_user
from flask import request
from datetime import datetime
from app import db
from app.auth.forms import LoginForm, RegistrationForm

auth = Blueprint('auth', __name__, template_folder="templates", static_folder="static")


@auth.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        # if not is_safe_url(next_page):
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('/auth/login.html', title='Sign In', form=form)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('/auth/signup.html', title='Register', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('Logged out')
    return redirect(url_for('main.index'))
