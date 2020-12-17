from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, Email, EqualTo, DataRequired, ValidationError
from app.models import User


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
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
    password_old = PasswordField('Old Password', validators=[DataRequired(), Length(min=6,
                                                                                    message="Length of password should be greater than 6")])

    password_new = PasswordField('New Password', validators=[DataRequired(), Length(min=2, max=20)])
    password_new2 = PasswordField('Repeat New Password', validators=[DataRequired(), EqualTo('password_new')])
    submit = SubmitField('Update password')
