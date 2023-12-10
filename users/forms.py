from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, BooleanField
from wtforms.validators import InputRequired, Email, ValidationError, Length, EqualTo, DataRequired
import re
from flask_wtf import RecaptchaField
from flask import redirect, url_for




def fname_lname_check (form, field):
    excluded_chars = "*?!'^+%&/()=}][{$#@<>"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(f"Character {char} is not allowed")


def phone(self,phone):
    p = re.compile(r'^\d{4}-\d{3}-\d{4}$')
    if not p.match(phone.data):
        raise ValidationError('Must contain only digits from 0-9 in the form XXXX-XXX-XXXX')

def validate_password(self, password):
    p = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*\W)')
    if not p.match(password.data):
        raise ValidationError('Password must contain 1 digit, one lowercase letter and one uppercase letter and one symbol')



class RegisterForm(FlaskForm):
    email = EmailField(validators=[InputRequired(),Email('Please enter a valid email address')])
    firstname = StringField(validators=[InputRequired(),fname_lname_check])
    lastname = StringField(validators=[InputRequired(),fname_lname_check])
    phone = StringField(validators=[InputRequired(), phone])
    password = PasswordField(validators=[InputRequired(), Length(min=6, max=12), validate_password])
    confirm_password = PasswordField(validators=[InputRequired(),EqualTo('password',message='Both password fields must be equal')])
    submit = SubmitField()


class LoginForm(FlaskForm):
    recaptcha = RecaptchaField()
    pin = StringField(validators=[DataRequired()])
    email = EmailField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class PasswordForm(FlaskForm):
    current_password = PasswordField(id='password', validators=[DataRequired()])
    show_password = BooleanField('Show password', id='check')
    new_password = PasswordField(validators=[DataRequired(), Length(min=6, max=12, message="Must be between 6 and 12 characters in length"),
    validate_password])
    confirm_new_password = PasswordField(validators=[DataRequired(), EqualTo('new_password', message='Both new password fields must be equal')])
    submit = SubmitField('Change Password')
