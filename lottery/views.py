# IMPORTS
from flask import Blueprint, render_template, request, flash, redirect, url_for

import app
from app import db, forbidden
from users.views import requires_roles
from lottery.forms import DrawForm
from models import Draw, decrypt, encrypt
from flask_login import current_user, login_required
from sqlalchemy.orm import make_transient


# CONFIG
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


# VIEWS
# view lottery page
@lottery_blueprint.route('/lottery')
@login_required
#@requires_roles('user')
def lottery():
    if current_user.role == 'admin':
        print('======================================================')
        return app.forbidden()
    return render_template('lottery/lottery.html', name=current_user.firstname)


# view all draws that have not been played
@lottery_blueprint.route('/create_draw', methods=['POST'])
def create_draw():
    form = DrawForm()


    if form.validate_on_submit():
        submitted_numbers = (str(form.number1.data) + ' '
                          + str(form.number2.data) + ' '
                          + str(form.number3.data) + ' '
                          + str(form.number4.data) + ' '
                          + str(form.number5.data) + ' '
                          + str(form.number6.data))



        numbers = [form.number1.data, form.number2.data, form.number3.data, form.number4.data, form.number5.data,
                   form.number6.data]
        form.sort_num()
        print(form.data)
        print("###########################\n#################")
        if len(numbers) != len(set( numbers)):
            flash('Numbers must be unique.')
            return render_template('lottery/lottery.html', name=current_user.firstname, form=form)

        encrypted_numbers = encrypt(submitted_numbers, current_user.post_key)

        # create a new draw with the form data.
        new_draw = Draw(user_id=current_user.id, numbers=encrypted_numbers, master_draw=False, lottery_round=1,post_key=current_user.post_key)
        # add the new draw to the database
        db.session.add(new_draw)
        db.session.commit()

        # re-render lottery.page
        flash('Draw %s submitted.' % submitted_numbers)
        return redirect(url_for('lottery.lottery'))

    return render_template('lottery/lottery.html', name=current_user.firstname, form=form)


# view all draws that have not been played
@lottery_blueprint.route('/view_draws', methods=['POST'])
def view_draws():
    # get all draws that have not been played [played=0]
    playable_draws = Draw.query.filter_by(been_played=False,user_id=current_user.id).all() #.with_entities(Draw.numbers).all()


    # if playable draws exist
    if len(playable_draws) != 0:

        for draw in playable_draws:
            draw.numbers= decrypt(draw.numbers, current_user.post_key)

        # re-render lottery page with playable draws
        return render_template('lottery/lottery.html', playable_draws=playable_draws)
    else:
        flash('No playable draws.')
        return lottery()


# view lottery results
@lottery_blueprint.route('/check_draws', methods=['POST'])
def check_draws():
    # get played draws
    played_draws = Draw.query.filter_by(been_played=True, user_id=current_user.id).all()
   # print(type(played_draws))
    # if played draws exist
    if len(played_draws) != 0:
      #  for draw in played_draws:
          #  draw.numbers = decrypt(draw.numbers, current_user.post_key)

      #  db.session.commit()
        return render_template('lottery/lottery.html', results=played_draws, played=True)

    # if no played draws exist [all draw entries have been played therefore wait for next lottery round]
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# delete all played draws
@lottery_blueprint.route('/play_again', methods=['POST'])
def play_again():
    Draw.query.filter_by(been_played=True, master_draw=False).delete(synchronize_session=False)
    db.session.commit()

    flash("All played draws deleted.")
    return lottery()


