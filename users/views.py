# IMPORTS
import pyotp as pyotp
from flask import Blueprint, render_template, flash, redirect, url_for, session
from sqlalchemy.sql.functions import user
from werkzeug.security import check_password_hash

from app import db
from models import User
from users.forms import RegisterForm, LoginForm

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('users/register.html', form=form)

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        session['username'] = new_user.username
        return redirect(url_for('users.twofa'))
    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)

@users_blueprint.route('/twofa')
def twofa():

    if 'username' not in session:
        return redirect(url_for('main.index'))

    del session['username']
    return render_template('users/twofa.html', username=user.username, uri=user.get_2fa_uri())
    200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }

def get_2fa_uri(self):
    return str(pyotp.totp.TOTP(self.pin_key).provisioning_uri(
        name=self.username,

        issuer_name='Lottery App')
    )
# view user login


@users_blueprint.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()
        if not user or not user.verify_password(form.password.data):
            flash('Unsuccessful login','danger')

            return render_template('users/login.html', form=form)
        else:
            flash('Login Successful' )
            return redirect(url_for('index'))
            # Passwords match, login



    return render_template('users/login.html', form=form)


# view user account
@users_blueprint.route('/account')
def account():
    return render_template('users/account.html',
                           acc_no="PLACEHOLDER FOR USER ID",
                           email="PLACEHOLDER FOR USER EMAIL",
                           firstname="PLACEHOLDER FOR USER FIRSTNAME",
                           lastname="PLACEHOLDER FOR USER LASTNAME",
                           phone="PLACEHOLDER FOR USER PHONE")
