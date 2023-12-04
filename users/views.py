# IMPORTS
import pyotp as pyotp
from flask import Blueprint, render_template, flash, redirect, url_for, session, make_response
from flask_wtf import form
from markupsafe import Markup
from sqlalchemy.sql.functions import user
from werkzeug.security import check_password_hash
from flask_login import current_user, login_required
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

        session['username'] = new_user.email
        return redirect(url_for('users.twofa'))
    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form)


@users_blueprint.route('/twofa')
def twofa():
    # User user = User.query.get(role)

    if 'username' not in session:
        return redirect(url_for('main.index'))

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
    # if not session.get('authentication_attempts'):
    #  session['authentication_attempts'] = 0

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not user.verify_password(form.password.data):  # or not user.verify_pin(form.pin.data)
            #    session['authentication_attempts'] += 1
            #   print("attempted login"+ str(session['authentication_attempts']))
            #  if session.get('authentication_attempts') >= 3:
            #     flash(Markup('Number of login attempts exceeded. Please click <a href="/reset>here</a> to reset.'))
            #     return render_template('users/login.html')

            flash('Unsuccessful login, please try again ')
            return render_template('users/login.html', form=form)
            # '{} login attempts remaining'.format(3-session.get('authentication_attempts')),'danger')
        else:
            return redirect(url_for('index'))

    #     return render_template('users/login.html', form=form)
    # else:
    #   flash('Login Successful' )
    #   return redirect(url_for('index'))
    # Passwords match, login
   # else:
       # return redirect(url_for('index'))

    return render_template('users/login.html', form=form)


# view user account
@users_blueprint.route('/account')
#@login_required
def account():
    return render_template('users/account.html',
                           acc_no="PLACEHOLDER FOR USER ID",
                           email="PLACEHOLDER FOR USER EMAIL",
                           firstname="PLACEHOLDER FOR USER FIRSTNAME",
                           lastname="PLACEHOLDER FOR USER LASTNAME",
                           phone="PLACEHOLDER FOR USER PHONE")

# new_post = User(email = current_user.email, title= form.title.data, body=form.body.data)
