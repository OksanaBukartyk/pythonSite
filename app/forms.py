from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from werkzeug.security import generate_password_hash
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, TextField
from wtforms.validators import InputRequired, Length, Email, EqualTo, DataRequired, ValidationError, Regexp
from app import bcrypt
from app.models import  User
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import rules
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired('A username is required')])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[Length(min=6, message="Length of password should be greater than 6")])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class CreateForm(FlaskForm):
    body = StringField('Body', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Create')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField(validators=[FileAllowed(['jpg', 'png'])])
    about_me = StringField('About Me', validators=[DataRequired()])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class UpdatePasswordForm(FlaskForm):
    password_old = PasswordField('Old Password',
                                 validators=[DataRequired(), Length(min=6,
                                                                    message="Length of password should be greater than 6")])

    password_new = PasswordField('New Password',
                                 validators=[DataRequired(), Length(min=2, max=20)])
    password_new2 = PasswordField('Repeat New Password',
                                  validators=[DataRequired(), EqualTo('password_new')])
    submit = SubmitField('Update password')


class UpdatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = StringField('Body', validators=[DataRequired()])
    submit = SubmitField('Update')

class SearchForm(FlaskForm):
    text = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')


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


