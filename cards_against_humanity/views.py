'''
GAME STATES
-1 = error
0 = black card selection
1 = card playing
2 = winner selection

PLAYER STATES
-1 = error
0 = card playing
1 = card played
2 = card tzar

'''
from cards_against_humanity import app
from flask import render_template, request, redirect, url_for, make_response
from jinja2 import Template
from sqlalchemy import func
import coloredlogs, logging
import json
from cards_against_humanity.models import *
from cards_against_humanity.utils import *


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        game_id = request.form.get("game-id")
        return redirect(url_for("game", game_id = game_id))
    else:
        return render_template("home.html")

@app.route('/add_cards', methods=['GET', 'POST'])
def add_cards():
    if request.method == 'POST':
        text = request.form.get("card-text")
        new_card = Card(id=create_id(24), text=text, type=0)
        db.session.add(new_card)
        db.session.commit()
        return render_template("add-cards.html")
    else:
        return render_template("add-cards.html")

@app.route('/set_name', methods=['GET', 'POST'])
def set_name(): # set player name if player hasn't done so before
    if request.method == 'POST':

        # create new player
        name = request.form.get("name")
        player_id = create_id(8)
        new_player = Player(id=player_id, name=name, state=0, score=0)
        db.session.add(new_player)
        db.session.commit()

        # redirect back to game
        resp = make_response(redirect(request.cookies.get('next')))
        resp.set_cookie('player_id', player_id)
        return resp
    else:
        return render_template("set-name.html")

@app.route('/new_game')
def new_game(): # create new game

    player_id = request.cookies.get('player_id')
    # if player has not been here before
    if player_id is None:
        # create new name
        resp = make_response(redirect(url_for("set_name")))
        resp.set_cookie('next', '/new_game')
        return resp
    else:
        # create new unique game
        game_id = create_id(5)
        while Game.query.filter_by(id=game_id).first() is not None:
            logger.warning("Game ID already exists")
            game_id = create_id(5)
        new_game = Game(id=game_id, state=0)
        db.session.add(new_game)

        # set card tzar
        card_tzar = Player.query.filter_by(id=player_id).first()
        card_tzar.state = 2

        db.session.commit()

        return redirect(url_for("game", game_id = game_id))



@app.route('/game/<game_id>')
def game(game_id):
    game = Game.query.filter_by(id=game_id).first()
    if game:
        player_id = request.cookies.get('player_id')
        # if player has not been here before
        if player_id is None:
            # create new name
            resp = make_response(redirect(url_for("set_name")))
            resp.set_cookie('next', 'game/' + game_id)
            return resp
        else:
            # add game to player
            player = Player.query.filter_by(id=player_id).first()
            player.game = game_id
            db.session.commit()

            # return game page
            resp = make_response(render_template("game.html"))
            resp.set_cookie('game_id', game_id)
            return resp
    else:
        return redirect(url_for("home"))
