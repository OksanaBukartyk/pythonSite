from flask import render_template, flash , redirect, url_for
from app import app, bcrypt, db
from app.forms import LoginForm, RegistrationForm, CreateForm, UpdateAccountForm, UpdatePasswordForm
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
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        #if not is_safe_url(next_page):
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
        user = User(form.username.data,form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Register', form=form)

@app.route('/all_posts')
@login_required 
def all_posts():
    posts = Post.query.all()
    return render_template('all_posts.html', posts=posts)

@app.route('/my_posts')
@login_required 
def my_posts():
    posts = Post.query.filter_by(user_id=current_user.id)
    return render_template('my_posts.html', posts=posts)

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
    return render_template('profile.html', title ='Profile', image_file = image_file, form =form)


@app.route('/edit_pass', methods=['GET', 'POST'])
@login_required
def edit_pass():
    form = UpdatePasswordForm()
    if form.validate_on_submit():

        #current_user.password_hash= form.username1.data
        user = User.query.filter_by(email=current_user.email).first()
        if user.check_password(form.password_old.data):
            #current_user.password_hash = form.username3.data
            current_user.set_password(form.password_new2.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Incorrect old password')
            return redirect(url_for('edit_pass'))
   
    return render_template('edit_pass.html', title ='Profile', form =form)



@app.route('/create')
@login_required
def create():
    return render_template('create.html')

@app.route('/create', methods=['POST'])
@login_required
def create_post():
    body = request.form.get('body')
    
    post = Post(body=body, user_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    
    return redirect (url_for('posts'))