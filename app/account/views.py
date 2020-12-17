from flask import Blueprint, render_template, redirect, url_for, flash, request
from PIL import Image
from urllib.parse import urlparse, urljoin
import os
import secrets
from app.models import User
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.account.forms import UpdateAccountForm, UpdatePasswordForm

account = Blueprint('account', __name__, template_folder="templates", static_folder="static")


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@account.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(account.root_path, 'static/profile_pics', picture_fn)
    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@account.route('/', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me

    image_file = url_for('account.static', filename='profile_pics/' + current_user.image_file)
    return render_template('/account/profile.html', title='Profile', image_file=image_file, form=form)


@account.route('/profile/edit_pass', methods=['GET', 'POST'])
@login_required
def edit_pass():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if user.check_password(form.password_old.data):
            current_user.set_password(form.password_new2.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('account.profile'))
        else:
            flash('Incorrect old password', 'danger')
            return redirect(url_for('account.edit_pass'))
    return render_template('/account/edit_pass.html', title='Profile', form=form)
