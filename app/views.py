from flask import render_template, flash, redirect, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, CreateForm, UpdateAccountForm, UpdatePasswordForm, UpdatePostForm, SearchForm
from .models import User, Post
from flask_login import current_user, login_user, logout_user, login_required
from PIL import Image

import os
import secrets
from flask import request
from werkzeug.urls import url_parse
from urllib.parse import urlparse, urljoin
from datetime import datetime


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/animal')
def animal():
    return render_template('animal.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        # if not is_safe_url(next_page):
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email =form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Register', form=form)


@app.route('/all_posts')
@login_required
def all_posts():
    q = request.args.get('q')
    if q:
        posts = Post.query.filter(Post.title.contains(q) | Post.body.contains(q))
    else:
        posts = Post.query.order_by(Post.timestamp.desc())
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=4)
    return render_template('all_posts.html',posts = posts)


@app.route('/posts')
@login_required
def posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.timestamp.desc()).paginate(page=page, per_page=3)
    return render_template('posts.html',posts = posts)



@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out')
    return redirect(url_for('index'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/profile', methods=['GET', 'POST'])
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
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile.html', title='Profile', image_file=image_file, form=form)


@app.route('/profile/edit_pass', methods=['GET', 'POST'])
@login_required
def edit_pass():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if user.check_password(form.password_old.data):
            current_user.set_password(form.password_new2.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Incorrect old password','danger')
            return redirect(url_for('edit_pass'))
    return render_template('edit_pass.html', title='Profile', form=form)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateForm()
    if form.validate_on_submit():
        db.session.add(Post(body=form.body.data, title = form.title.data, author=current_user))
        db.session.commit()
        flash('Congratulations, you create new post!', 'success')
        return redirect(url_for('posts'))

    return render_template('create.html', form=form)


@app.route('/posts/<id>')
@login_required
def post(id):
    return render_template('post.html', post=Post.query.filter_by(id=id))


@app.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    form = UpdatePostForm()
    post = Post.query.get(id)
    if post.user_id == current_user.id:
        if form.validate_on_submit():
            Post.query.filter_by(id=id).update({'body': form.body.data,'title': form.title.data})
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('post', id=id))

        elif request.method == 'GET':
            post =Post.query.get(id)
            form.title.data = post.title
            form.body.data = post.body
    else:
        flash('You try edit not your post!', 'danger')
        return redirect(url_for('posts', id = current_user.id))

    return render_template('edit.html', title='Edit', form=form)


@app.route('/posts/<int:id>/delete', methods = ['GET', 'POST'])
@login_required
def delete(id):
    post = Post.query.get(id)
    if post.user_id == current_user.id:
        Post.query.filter_by(id=id).delete()
        db.session.commit()
        flash('Post was deleted', 'success')
        return redirect(url_for('posts'))
    else:
        flash('You try delete not your post!', 'danger')
        return redirect(url_for('posts', id = current_user.id))


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    if q:
        posts = Post.query.filter(Post.title.contains(q) | Post.body.contains(q)).order_by(Post.timestamp.desc()).paginate(page=page, per_page=3)
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=3)
    return render_template('search.html', posts=posts)


