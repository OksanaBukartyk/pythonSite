from flask import render_template, flash, redirect, url_for
from app import  db
from flask import Blueprint
from app.models import User
from flask_login import current_user, login_required
from flask import request, abort
from datetime import datetime
from functools import wraps
from app.adminstrations.forms import AdminUserCreateForm, AdminUserUpdateForm

administrations = Blueprint('administrations', __name__, template_folder="templates", static_folder="static")

@administrations.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()





def admin_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin():
            return abort(403)
        return func(*args, **kwargs)
    return decorated_view







@administrations.route('/administrator')
@login_required
@admin_login_required
def admin_home():
    return render_template('/administrations/admin_home.html')



@administrations.route('/administrator/users-list')
@login_required
@admin_login_required
def users_list_admin():
    users = User.query.all()
    return render_template('/administrations/users_list_admin.html', users=users)


@administrations.route('/administrator/create-user', methods=['GET', 'POST'])
@login_required
@admin_login_required
def user_create_admin():
    form = AdminUserCreateForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, admin=form.admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('administrations.users_list_admin'))
    return render_template('/administrations/user_create_admin.html',  form=form)


@administrations.route('/administrator/update-user/<id>', methods=['GET', 'POST'])
@login_required
@admin_login_required
def user_update_admin(id):
    form = AdminUserUpdateForm()
    user = User.query.filter_by(id=id).first()
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.admin = form.admin.data
        db.session.commit()
        flash("User was updated", category="info")
        return redirect(url_for('administrations.users_list_admin'))
    elif request.method == 'GET':
        user = User.query.get(id)
        form.username.data = user.username
        form.email.data = user.email
        form.admin.data = user.admin
    return render_template('/administrations/user_update_admin.html', form=form, user=user)


@administrations.route('/administrator/delete-user/<id>')
@login_required
@admin_login_required
def user_delete_admin(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash("User was deleted", category="info")
    return render_template('/administrations/admin_home.html')


