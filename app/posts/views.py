from flask import Blueprint, render_template, redirect, url_for, flash
from app.models import Post
from flask_login import login_required, current_user
from flask import request
from datetime import datetime
from app import db
from app.posts.forms import CreateForm, UpdatePostForm

posts = Blueprint('posts', __name__, template_folder="templates" , static_folder="static")


@posts.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@posts.route('/all_posts', methods=['GET', 'POST'])
@login_required
def all_posts():
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    if q:
        posts = Post.query.filter(Post.title.contains(q) | Post.body.contains(q)).order_by(
            Post.timestamp.desc()).paginate(page=page, per_page=4)
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=4)
    return render_template('/posts/all_posts.html', posts=posts)


@posts.route('/my_posts', methods=['GET', 'POST'])
@login_required
def my_posts():
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    if q:
        posts = Post.query.filter(Post.title.contains(q) | Post.body.contains(q)).order_by(
            Post.timestamp.desc()).paginate(page=page, per_page=3)
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=3)
    return render_template('/posts/my_posts.html', posts=posts)


@posts.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateForm()
    if form.validate_on_submit():
        db.session.add(Post(body=form.body.data, title=form.title.data, author=current_user))
        db.session.commit()
        flash('Congratulations, you create new post!', 'success')
        return redirect(url_for('posts.my_posts'))
    return render_template('/posts/create.html', form=form)


@posts.route('/posts/<id>')
@login_required
def post(id):
    return render_template('/posts/post.html', post=Post.query.filter_by(id=id))


@posts.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    form = UpdatePostForm()
    post = Post.query.get(id)
    if post.user_id == current_user.id:
        if form.validate_on_submit():
            Post.query.filter_by(id=id).update({'body': form.body.data, 'title': form.title.data})
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('posts.my_posts', id=id))
        elif request.method == 'GET':
            post = Post.query.get(id)
            form.title.data = post.title
            form.body.data = post.body
    else:
        flash('You try edit not your post!', 'danger')
        return redirect(url_for('/posts/my_posts', id=current_user.id))
    return render_template('/posts/edit.html', title='Edit', form=form)


@posts.route('/posts/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete(id):
    post = Post.query.get(id)
    if post.user_id == current_user.id:
        Post.query.filter_by(id=id).delete()
        db.session.commit()
        flash('Post was deleted', 'success')
        return redirect(url_for('posts.my_posts'))
    else:
        flash('You try delete not your post!', 'danger')
        return redirect(url_for('posts.my_posts', id=current_user.id))
