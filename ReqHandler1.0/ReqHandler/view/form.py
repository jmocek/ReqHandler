from flask_wtf import Form
from wtforms.fields import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, url, ValidationError
from ReqHandler.module_file.models import User, Product


class RequirementAddForm(Form):
    text = StringField('Requirement text: ', validators=[DataRequired(), Length(0, 1000)])

    product_version_new = StringField('Enter product version if not already added: ', validators=[Length(0, 1000)])

    def validate_product_version_new(self, product_version_new_field):
        if len(product_version_new_field.data) > 0:
            try:
                float(product_version_new_field.data)
            except ValueError:
                raise ValidationError('Product version shall be a dot separated float number or int')
            if Product.query.filter_by(version=float(product_version_new_field.data)).first():
                raise ValidationError('There is already that product version.')


class LoginForm(Form):
    username = StringField('Your Username:', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class SignupForm(Form):
    username = StringField('Username',
                           validators=[
                                       DataRequired(), Length(3, 80),
                                       Regexp('^[A-Za-z0-9_]{3,}$',
                                              message='Usernames consist of numbers, letters,'
                                                      'and underscores.')])
    password = PasswordField('Password',
                             validators=[
                                         DataRequired(),
                                         EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Length(1, 120), Email()])

    def validate_email(self, email_field):
        if User.query.filter_by(email=email_field.data).first():
            raise ValidationError('There already is a user with this email address.')

    def validate_username(self, username_field):
        if User.query.filter_by(username=username_field.data).first():
            raise ValidationError('This username is already taken.')


class ExportForm(Form):
    filename = StringField('Enter file name: ', validators=[DataRequired(), Length(0, 100)])


class BaselineForm(Form):
    description = StringField('Enter baseline description: ', validators=[DataRequired(), Length(1, 1000)])

