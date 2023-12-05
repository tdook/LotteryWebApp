# IMPORTS
from datetime import datetime
from functools import wraps

import pyotp as pyotp
from flask import Blueprint, render_template, flash, redirect, url_for, session, make_response
from flask_wtf import form
from markupsafe import Markup
from sqlalchemy.sql.functions import user
from werkzeug.security import check_password_hash
from flask_login import current_user, login_required, logout_user
from app import db
from models import User
from users.forms import RegisterForm, LoginForm, PasswordForm
from flask_login import login_user

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

        session['username'] = new_user.email
        return redirect(url_for('users.twofa'))
    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)


@users_blueprint.route('/twofa')

def twofa():
    # User user = User.query.get(role)

    if 'username' not in session:
        return redirect(url_for('index'))

    del session['username']

    # Create a Flask response object using make_response
    response = make_response(render_template('users/twofa.html', username=User.email, uri=User.get_2fa_uri))

    # Set headers for caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    # Return the response object
    return response


# view user login


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if not session.get('authentication_attempts'):
        session['authentication_attempts'] = 0

    form = LoginForm()
    print("prior")
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        login_user(user)

        current_user.current_login = datetime.now()
        current_user.last_login = datetime.now()

        if not user: #or (not user.verify_password(form.password.data) or not user.verify_pin(form.pin.data)):  # or not user.verify_pin(form.pin.data)
                print(session['authentication_attempts'])
                session['authentication_attempts'] += 1
                print("attempted login"+ str(session['authentication_attempts']))
                if session.get('authentication_attempts') >= 3:
                     flash(Markup('Number of login1 attempts exceeded. Please click <a href="/reset">here</a> to reset.'))
                     return render_template('users/login.html')

                flash('Unsuccessful login, please try again, {} login attempts remaining'.format(3-session.get('authentication_attempts')),'danger')

                return render_template('users/login.html', form=form)



        else:
            if current_user.role == "user":
                return redirect(url_for('lottery.lottery'))

            else:
                return redirect(url_for('admin.admin'))



    print("logged in ")

    return render_template('users/login.html', form=form)

@users_blueprint.route('/reset')
def reset():
    session['authentication_attempts'] = 0
    return redirect(url_for('users.login'))

@users_blueprint.route('/logout')
@login_required

def logout():
    logout_user()
    return redirect(url_for('index'))


@users_blueprint.route('/update_password', methods=['GET', 'POST'])
def update_password():
    form = PasswordForm()

    if form.validate_on_submit():

        # IF STATEMENT: check if current password entered by user does not match current password stored for user in the database.

        # IF STATEMENT: check if new password entered by the user matches current password stored for user in the database.

        current_user.password = form.new_password.data
        db.session.commit()
        flash('Password changed successfully')

        return redirect(url_for('users.account'))

    return render_template('users/update_password.html', form=form)

# view user account
@users_blueprint.route('/account')
@login_required
def account():
    return render_template('users/account.html',
                           acc_no=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone)

#new_post = User(email = current_user.email, title= form.title.data, body=form.body.data)

def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                return render_template('403.html')
            return f(*args, **kwargs)
        return wrapped
    return wrapper