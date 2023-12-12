from datetime import datetime

import pyotp
from cryptography.fernet import Fernet

from app import db, app
from flask_login import UserMixin


class User(db.Model, UserMixin):
    def get_2fa_uri(self):
        return str(pyotp.totp.TOTP(self.pin_key).provisioning_uri(
            name=self.email,

            issuer_name='Lottery App')
        )

    def verify_pin(self,pin):
        return pyotp.TOTP(self.pin_key).verify(pin)
    def verify_password(self, password):
        return self.password == password
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')
    pin_key = db.Column(db.String(32), nullable=False, default=pyotp.random_base32())
    registered_on = db.Column(db.DateTime, nullable=False)
    current_login = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    post_key = db.Column(db.BLOB, nullable=False, default=Fernet.generate_key())

    # Define the relationship to Draw
    draws = db.relationship('Draw')

    def __init__(self, email, firstname, lastname, phone, password, role):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = password
        self.role = role
        self.registered_on = datetime.now()
        self.current_login = None
        self.last_login = None








class Draw(db.Model):
    __tablename__ = 'draws'

    id = db.Column(db.Integer, primary_key=True)

    # ID of user who submitted draw
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    # 6 draw numbers submitted
    numbers = db.Column(db.String(100), nullable=False)

    # Draw has already been played (can only play draw once)
    been_played = db.Column(db.BOOLEAN, nullable=False, default=False)

    # Draw matches with master draw created by admin (True = draw is a winner)
    matches_master = db.Column(db.BOOLEAN, nullable=False, default=False)

    # True = draw is master draw created by admin. User draws are matched to master draw
    master_draw = db.Column(db.BOOLEAN, nullable=False)

    # Lottery round that draw is used
    lottery_round = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, user_id, numbers, master_draw, lottery_round, post_key):
        self.user_id = user_id
        self.numbers = numbers
        self.been_played = False
        self.matches_master = False
        self.master_draw = master_draw
        self.lottery_round = lottery_round
        self.post_key = post_key


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(email='admin@email.com',
                     password='Admin1!',
                     firstname='Alice',
                     lastname='Jones',
                     phone='0191-123-4567',
                     role='admin')


        db.session.add(admin)
        db.session.commit()


    def view_post(self, post_key):
        self.title = decrypt(self.title, post_key)
        self.body = decrypt(self)


def encrypt(data, post_key):
    return Fernet(post_key).encrypt(bytes(data, 'utf-8'))

#def decrypt(data, post_key):
 #   return Fernet(post_key).decrypt(data).decode('utf-8')

def decrypt_draws(draws):
    decrypted_draws = []

    for draw in draws:
        try:
            # Fetch the user's post_key from the database
            user = User.query.filter_by(id=draw.user_id).first()

            # Check if the user and post_key are found
            if user and user.post_key:
                # Decrypt the draw using the user's post_key
                decrypted_numbers = Fernet(user.post_key).decrypt(draw.numbers).decode('utf-8')

                # Append the decrypted draw to the list
                decrypted_draws.append((draw.id, decrypted_numbers))
            else:
                # Handle the case where user or post_key is not found
                print(f"User or post_key not found for draw {draw.id}")

        except Exception as e:
            # Handle decryption errors
            print(f"Error decrypting draw {draw.id}: {e}")

    return decrypted_draws

# Example usage:
user_draws = Draw.query.filter_by(master_draw=False, been_played=True).all()
decrypted_user_draws = decrypt_draws(user_draws)