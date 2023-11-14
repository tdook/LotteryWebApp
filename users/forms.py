from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import InputRequired, Email, ValidationError, Length
import re


def fname_lname_check (form, field):
    excluded_chars = "*?!'^+%&/()=}][{$#@<>"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(f"Character {char} is not allowed")


def phone(self,phone):
    p = re.compile(r'^\d{4}-\d{3}-\d{4}$')
    if not p.match(phone.data):
        raise ValidationError('Must contain only digits from 0-9 in the form XXXX-XXX-XXXX')


class RegisterForm(FlaskForm):
    email = EmailField(validators=[InputRequired(),Email('Please enter a valid email address')])
    firstname = StringField(validators=[InputRequired(),fname_lname_check])
    lastname = StringField(validators=[InputRequired(),fname_lname_check])
    phone = StringField(validators=[InputRequired(), phone])
    password = PasswordField()
    confirm_password = PasswordField()
    submit = SubmitField()
