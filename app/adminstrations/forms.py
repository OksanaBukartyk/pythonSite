from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Email, EqualTo, DataRequired
from app import bcrypt
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import rules
from wtforms.widgets import TextArea

class AdminUserCreateForm(FlaskForm):
    username = StringField('Username', [InputRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', [InputRequired()])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    admin = BooleanField('Is Admin ?')
    submit = SubmitField('Create')


class AdminUserUpdateForm(FlaskForm):
    username = StringField('Username', [InputRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    admin = BooleanField('Is Admin ?')
    submit = SubmitField('Update')

class CKEditorWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += " ckeditor"
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKEditorWidget, self).__call__(field, **kwargs)


class CKEditorField(TextAreaField):
    widget = CKEditorWidget()


class UserAdminView(ModelView):
    form_overrides = dict(about_me=CKEditorField)
    can_view_details = True
    create_template = 'ckeditor.html'
    edit_template = 'ckeditor.html'

    column_searchable_list = ('username',)
    column_sortable_list = ('username', 'admin')
    column_exclude_list = ('about_me', 'last_seen')
    form_excluded_columns = ('password_hash', 'last_seen')
    form_edit_rules = ('username', 'admin')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def scaffold_form(self):
        form_class = super(UserAdminView, self).scaffold_form()
        form_class.password = PasswordField('Password')
        form_class.new_password = PasswordField('New Password')
        form_class.confirm = PasswordField('Confirm New Password')
        return form_class

    def create_model(self, form):
        model = self.model(username=form.username.data, password_hash=bcrypt.generate_password_hash(form.password.data),
                           admin=form.admin.data)
        form.populate_obj(model)
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()

    form_edit_rules = (
        'username', 'admin', 'about_me',
        rules.Header('Reset Password'),
        'new_password', 'confirm'
    )
    form_create_rules = (
        'username', 'admin', 'about_me', 'password'
    )

    def update_model(self, form, model):
        form.populate_obj(model)
        if form.new_password.data:
            if form.new_password.data != form.confirm.data:
                model.password = bcrypt.generate_password_hash(form.password.data)
                return  model.pwdhash
        self.session.add(model)
        self._on_model_change(form, model, False)
        self.session.commit()




class PostAdminView(ModelView):
    form_overrides = dict(body=CKEditorField)
    can_view_details = True
    create_template = 'ckeditor.html'
    edit_template = 'ckeditor.html'


    column_list = ['title', 'body', 'timestamp', 'author'] #cтовпці
    #column_exclude_list = ('timestamp',)  #стовпці крім
    column_searchable_list = ('id', 'title')  #пошук по
    column_sortable_list = ('title', 'timestamp')   #сортування
    column_filters = ('title', 'timestamp')    #фільтр


from flask_admin import BaseView, expose

class HelloView(BaseView):
    @expose('/')
    def index(self):
        return self.render('/main/index.html')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()


from flask_admin import AdminIndexView

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()