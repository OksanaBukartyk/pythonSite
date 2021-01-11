from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo, DataRequired, ValidationError, Regexp


class CreateProductForm(FlaskForm):

    name = StringField('Name', validators=[Length(min=3, max=25,
                                              message='This field length must be between 3 and 25 characters'),
                                              DataRequired('This field is required')])

    count = StringField('Number', validators=[Length(min=1, max=10,
                                              message='This field length must be between 3 and 25 characters'),
                                              DataRequired('This field is required')])
    price = StringField('Cost', validators=[Length(min=1, max=10,
                                              message='This field length must be between 3 and 25 characters'),
                                              DataRequired('This field is required')])

    category =  SelectField(u'Category', coerce=str)
    submit = SubmitField('Create')


class UpdateProductForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=3, max=25,
                                                  message='This field length must be between 3 and 25 characters'),
                                           DataRequired('This field is required')])

    count = StringField('Number', validators=[DataRequired()])
    price = StringField('Cost', validators=[DataRequired()])

    category = SelectField(u'Category', coerce=str)
    submit = SubmitField('Update')